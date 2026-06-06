
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sintaxis.parser_dcg import ParserDCG
from sintaxis.arbol import Nodo
from gramatica import lexico


class DialogATN:
    """
    Máquina de Diálogo (ATN) para Entrevistas de Triaje Psicológico.
    Gestiona estados empáticos, guarda el contexto clínico acumulado,
    ejecuta protocolos de crisis inmediata, maneja confirmaciones,
    ofrece recuperación asistida ante entradas no reconocidas
    y extrae dinámicamente los síntomas desde el árbol sintáctico.

    Estados: {inicio, esperando_estado, confirmando_sintoma, indagando_tiempo, aclaracion, analizado, crisis, fin}
    """
    def __init__(self):
        self.estado = "inicio"
        self.contexto = {
            'historia_oraciones': [],
            'dimensiones': set(),
            'max_sev': 'bajo',
            'escala_temporal': None,
            'crisis_detectada': False,
            'repeticiones_errores': 0,
            'sintoma_actual': None,
            'dim_actual': None,
            'sev_actual': None
        }
        self.parser = ParserDCG()

        self.transiciones = {
            'inicio': {
                'saludo': 'esperando_estado',
                'consulta': 'confirmando_sintoma',
                'invalido': 'aclaracion',
                'crisis': 'crisis'
            },
            'esperando_estado': {
                'consulta': 'confirmando_sintoma',
                'saludo_repetido': 'esperando_estado',
                'invalido': 'aclaracion',
                'crisis': 'crisis'
            },
            'aclaracion': {
                'seleccion_opcion': 'confirmando_sintoma',
                'saludo': 'esperando_estado',
                'despedida': 'fin',
                'invalido': 'aclaracion',
                'crisis': 'crisis'
            },
            'confirmando_sintoma': {
                'confirmacion': 'indagando_tiempo',
                'negacion': 'esperando_estado',
                'invalido': 'confirmando_sintoma',
                'crisis': 'crisis'
            },
            'indagando_tiempo': {
                'tiempo': 'analizado',
                'consulta_adicional': 'confirmando_sintoma',
                'invalido': 'indagando_tiempo',
                'crisis': 'crisis'
            },
            'analizado': {
                'agradecimiento': 'fin',
                'despedida': 'fin',
                'consulta_adicional': 'confirmando_sintoma',
                'invalido': 'analizado',
                'crisis': 'crisis'
            },
            'crisis': {
                'confirmar_ayuda': 'fin',
                'invalido': 'crisis'
            },
            'fin': {
                'saludo': 'esperando_estado',
                'invalido': 'fin'
            }
        }

    def _buscar_nodos_clinicos_significativos(self, nodo):
        if nodo is None:
            return []
        
        # Si este nodo es una categoría clínica representativa, lo guardamos
        if nodo.etiqueta in ['AP', 'NP', 'SP', 'Vinf'] and nodo.rasgos and nodo.rasgos.get('dim', 'neutro') != 'neutro':
            return [nodo]
            
        result = []
        if not nodo.is_terminal() and nodo.hijos:
            for hijo in nodo.hijos:
                if isinstance(hijo, Nodo):
                    result.extend(self._buscar_nodos_clinicos_significativos(hijo))
        return result

    def _extraer_sintoma(self, arbol):
        if arbol is None:
            return None
        nodos = self._buscar_nodos_clinicos_significativos(arbol)
        if not nodos:
            return None
        
        textos = []
        for n in nodos:
            txt = n.get_text()
            if txt:
                textos.append(txt)
        
        if len(textos) == 1:
            return textos[0]
        elif len(textos) > 1:
            return " y ".join(textos)
        return None

    def clasificar_acto_lenguaje(self, texto, arbol_sintactico):
        texto_lower = texto.lower().strip()

        # 1. Detectar crisis primero si hay rasgos críticos
        if arbol_sintactico is not None:
            rasgos = arbol_sintactico.rasgos
            if rasgos.get('dim') == 'crisis' and rasgos.get('sev') == 'critico':
                return "crisis", rasgos

        # 2. Si el estado es 'crisis'
        if self.estado == "crisis":
            if any(w in texto_lower for w in ["si", "sí", "bueno", "acepto", "ayuda", "llamar", "marcar", "por favor"]):
                return "confirmar_ayuda", {}
            return "invalido", {}

        # 3. Si el estado es 'confirmando_sintoma'
        if self.estado == "confirmando_sintoma":
            if any(w in texto_lower for w in ["si", "sí", "correcto", "efectivamente", "así es", "afirmativo", "claro", "vale", "s", "ok"]):
                return "confirmacion", {}
            if any(w in texto_lower for w in ["no", "incorrecto", "para nada", "falso", "negativo", "n"]):
                return "negacion", {}
            return "invalido", {}

        # 4. Si el estado es 'aclaracion'
        if self.estado == "aclaracion":
            if "1" in texto_lower or "emocional" in texto_lower or "triste" in texto_lower or "animo" in texto_lower:
                return "seleccion_opcion", {'dim': 'animo', 'sev': 'medio', 'sintoma': 'malestar afectivo/emocional'}
            if "2" in texto_lower or "ansiedad" in texto_lower or "tension" in texto_lower or "nervio" in texto_lower:
                return "seleccion_opcion", {'dim': 'ansiedad', 'sev': 'medio', 'sintoma': 'ansiedad o tension'}
            if "3" in texto_lower or "fisico" in texto_lower or "sueño" in texto_lower or "cansancio" in texto_lower or "dormir" in texto_lower:
                return "seleccion_opcion", {'dim': 'fisico', 'sev': 'medio', 'sintoma': 'dificultad de sueno o cansancio'}
            if "4" in texto_lower or "concentra" in texto_lower or "pensar" in texto_lower or "cognitivo" in texto_lower:
                return "seleccion_opcion", {'dim': 'cognitivo', 'sev': 'medio', 'sintoma': 'dificultad para concentrarte o pensar'}

        # 5. Saludos, Agradecimientos, Despedidas
        if any(w in texto_lower for w in ["hola", "buenos días", "buenas tardes", "buenas", "un saludo", "hey", "hola!"]):
            if self.estado == "esperando_estado":
                return "saludo_repetido", {}
            return "saludo", {}

        if any(w in texto_lower for w in ["gracias", "muchas gracias", "entendido", "vale", "perfecto", "excelente"]):
            return "agradecimiento", {}
        if any(w in texto_lower for w in ["adiós", "adios", "chao", "hasta luego", "bye"]):
            return "despedida", {}

        # 6. Uso del árbol sintáctico para consulta o tiempo
        if arbol_sintactico is not None:
            rasgos = arbol_sintactico.rasgos
            if rasgos.get('escala') is not None:
                return "tiempo", rasgos
            if rasgos.get('dim') != 'neutro':
                return "consulta", rasgos

        return "invalido", {}

    def procesar_turno(self, texto):
        # Intentar parsear oracion completa
        arbol = self.parser.parsear_oracion(texto)
        
        # Si falla y estamos buscando la escala temporal, intentar parsear como expresion de tiempo o sintagma preposicional
        if arbol is None and self.estado == 'indagando_tiempo':
            from tokenizacion.dfa_tokenizer import TokenizerDFA
            dfa = TokenizerDFA()
            tokens_sucios = dfa.tokenize(texto)
            tokens = []
            i = 0
            n = len(tokens_sucios)
            while i < n:
                if i + 2 < n and tokens_sucios[i] == "todo" and tokens_sucios[i+1] == "el" and tokens_sucios[i+2] == "tiempo":
                    tokens.append("todo el tiempo")
                    i += 3
                elif i + 1 < n and tokens_sucios[i] == "un" and tokens_sucios[i+1] == "poco":
                    tokens.append("un poco")
                    i += 2
                elif i + 1 < n and tokens_sucios[i] == "a" and tokens_sucios[i+1] == "veces":
                    tokens.append("a veces")
                    i += 2
                else:
                    tokens.append(tokens_sucios[i])
                    i += 1
            
            # Intentar parsear como SP (Sintagma Preposicional)
            arbol_sp, pos_sp = self.parser.parse_simbolo('SP', tokens, 0)
            if arbol_sp is not None and pos_sp == len(tokens):
                arbol = arbol_sp
            else:
                # Intentar parsear como Exp_temp (Expresion temporal)
                arbol_exp, pos_exp = self.parser.parse_simbolo('Exp_temp', tokens, 0)
                if arbol_exp is not None and pos_exp == len(tokens):
                    arbol = arbol_exp

        # 1. Caso de Tercero (Reporte)
        if arbol and arbol.rasgos.get('pers') == '3':
            self.estado = 'fin'
            sintoma = "Malestar"
            texto_lower = texto.lower()
            if any(w in texto_lower for w in ["dormir", "duerme", "insomnio", "sueño"]):
                sintoma = "Insomnio"
            elif any(w in texto_lower for w in ["ansioso", "ansiosa", "ansiedad", "nervioso", "nerviosa"]):
                sintoma = "Ansiedad"
            elif any(w in texto_lower for w in ["triste", "tristeza", "deprimido", "deprimida", "desesperado"]):
                sintoma = "Depresión"
                
            reporte_msg = (
                f"Entendido. He registrado un reporte sobre un tercero (Sujeto: Tercero) "
                f"que presenta síntomas de {sintoma.lower()}.\n"
                f"Te sugiero recomendarle buscar apoyo profesional de manera directa."
            )
            return f"{reporte_msg}\n\n[Sujeto: Tercero, Síntoma: {sintoma}, Acción: Reporte]"

        # 2. Caso de Síntoma + Temporalidad Completa (Auto-triage inmediato)
        if arbol and arbol.rasgos.get('dim') != 'neutro' and arbol.rasgos.get('escala') is not None:
            self.estado = 'analizado'
            self.contexto['dim_actual'] = arbol.rasgos.get('dim')
            self.contexto['sev_actual'] = arbol.rasgos.get('sev', 'medio')
            self.contexto['escala_temporal'] = arbol.rasgos.get('escala')
            self.contexto['dimensiones'].add(arbol.rasgos.get('dim'))
            self.actualizar_severidad(arbol.rasgos.get('sev', 'medio'))
            
            texto_lower = texto.lower()
            if "una semana" in texto_lower or "1 semana" in texto_lower:
                self.contexto['tiempo_exacto_str'] = "7 días"
            elif "un dia" in texto_lower or "un día" in texto_lower or "1 dia" in texto_lower or "1 día" in texto_lower:
                self.contexto['tiempo_exacto_str'] = "1 día"
            elif "dos semanas" in texto_lower:
                self.contexto['tiempo_exacto_str'] = "14 días"
            elif "tres semanas" in texto_lower:
                self.contexto['tiempo_exacto_str'] = "21 días"
            elif "semanas" in texto_lower:
                self.contexto['tiempo_exacto_str'] = "varias semanas"
            elif "meses" in texto_lower:
                self.contexto['tiempo_exacto_str'] = "varios meses"
            elif "años" in texto_lower or "anios" in texto_lower:
                self.contexto['tiempo_exacto_str'] = "varios años"
            
            return self.generar_informe_triaje()
        # -----------------------------------------------------------------------------

        acto, rasgos = self.clasificar_acto_lenguaje(texto, arbol)

        posibles = self.transiciones.get(self.estado, {})
        nuevo_estado = posibles.get(acto, None)

        if nuevo_estado is None:
            nuevo_estado = posibles.get('invalido', self.estado)

        self.estado = nuevo_estado
        self.contexto['repeticiones_errores'] = 0 if acto != 'invalido' else self.contexto['repeticiones_errores'] + 1

        respuesta = self.ejecutar_acciones_y_generar_respuesta(acto, rasgos, arbol, texto)
        return respuesta

    def ejecutar_acciones_y_generar_respuesta(self, acto, rasgos, arbol, texto):
        if (rasgos and rasgos.get('dim') == 'crisis' and rasgos.get('sev') == 'critico') or acto == 'crisis':
            self.estado = 'crisis'
            self.contexto['crisis_detectada'] = True
            return ("[ALERTA CRITICA] Me preocupa profundamente tu seguridad inmediata. "
                    "Por favor, no estas solo. Quiero pedirte que hablemos con un profesional medico ahora. "
                    "Me autorizas a darte el numero directo de atencion telefonica de emergencia psicologica de la Universidad (o nacional) "
                    "o deseas que llamemos juntos? Por favor, responde 'SI' para recibir la ayuda.")

        if self.contexto['repeticiones_errores'] >= 3:
            self.estado = 'aclaracion'
            self.contexto['repeticiones_errores'] = 0
            return ("Me esta costando un poco entender tu respuesta en este momento de la conversacion. "
                    "Para poder ayudarte, por favor elige una de las siguientes opciones (digita 1, 2, 3 o 4):\n"
                    "  1. Malestar afectivo o de animo (tristeza, llanto)\n"
                    "  2. Ansiedad o tension constante\n"
                    "  3. Dificultades fisicas (insomnio, cansancio)\n"
                    "  4. Problemas cognitivos (falta de concentracion)\n"
                    "Por favor, escribe el numero correspondiente.")

        if self.estado == 'inicio':
            return "Hola! Bienvenido al asistente de triaje psicologico. Como te has sentido en estos ultimos dias?"

        elif self.estado == 'esperando_estado':
            if acto == 'saludo':
                return "Hola, espero que estes bien. Me podrias contar que te trae por aqui o como te has sentido ultimamente?"
            elif acto == 'saludo_repetido':
                return "Hola de nuevo! Dime, como te has estado sintiendo ultimamente emocional o fisicamente?"
            elif acto == 'negacion':
                return "Entendido, disculpa el malentendido. Por favor cuéntame con tus propias palabras qué es lo que estás sintiendo."
            return "Me podrias detallar un poco mas sobre lo que estas experimentando emocional o fisicamente?"

        elif self.estado == 'aclaracion':
            return ("No he logrado identificar un sintoma claro en tu respuesta. "
                    "Para poder asistirte mejor, elige una de las siguientes opciones (digita 1, 2, 3 o 4):\n"
                    "  1. Malestar afectivo o de animo (tristeza, desanimo, llanto)\n"
                    "  2. Ansiedad (tension, nerviosismo, estres)\n"
                    "  3. Problema fisico o del sueno (cansancio, insomnio)\n"
                    "  4. Dificultad para concentrarte o pensar\n"
                    "Cual de ellas describe mejor tu situacion actual?")

        elif self.estado == 'confirmando_sintoma':
            if acto == 'consulta' and arbol:
                sintoma = self._extraer_sintoma(arbol)
                self.contexto['sintoma_actual'] = sintoma if sintoma else "un malestar"
                self.contexto['dim_actual'] = rasgos.get('dim')
                self.contexto['sev_actual'] = rasgos.get('sev')
            elif acto == 'seleccion_opcion' and rasgos:
                self.contexto['sintoma_actual'] = rasgos.get('sintoma')
                self.contexto['dim_actual'] = rasgos.get('dim')
                self.contexto['sev_actual'] = rasgos.get('sev')

            sintoma_actual = self.contexto.get('sintoma_actual', 'un sintoma')
            dim_actual = self.contexto.get('dim_actual', 'emocional')
            sev_actual = self.contexto.get('sev_actual', 'bajo')

            # Registrar provisionalmente
            self.contexto['dimensiones'].add(dim_actual)
            self.actualizar_severidad(sev_actual)
            if arbol:
                self.contexto['historia_oraciones'].append(arbol)

            return (f"Entendido. Registro que estas experimentando '{sintoma_actual}' "
                    f"(relacionado con {dim_actual} y de severidad estimada '{sev_actual.upper()}'). "
                    f"Es correcto? (Por favor responde 'SI' o 'NO')")

        elif self.estado == 'indagando_tiempo':
            sintoma_actual = self.contexto.get('sintoma_actual', 'este sintoma')
            return f"Gracias por confirmarlo. Hace cuanto tiempo te vienes sintiendo con '{sintoma_actual}'?"

        elif self.estado == 'analizado':
            if rasgos and rasgos.get('escala'):
                self.contexto['escala_temporal'] = rasgos.get('escala')
            # Guardar el tiempo exacto si está en la respuesta de tiempo
            texto_lower = texto.lower()
            if "una semana" in texto_lower or "1 semana" in texto_lower:
                self.contexto['tiempo_exacto_str'] = "7 días"
            elif "un dia" in texto_lower or "un día" in texto_lower or "1 dia" in texto_lower or "1 día" in texto_lower:
                self.contexto['tiempo_exacto_str'] = "1 día"
            elif "dos semanas" in texto_lower:
                self.contexto['tiempo_exacto_str'] = "14 días"
            elif "tres semanas" in texto_lower:
                self.contexto['tiempo_exacto_str'] = "21 días"
            elif "semanas" in texto_lower:
                self.contexto['tiempo_exacto_str'] = "varias semanas"
            elif "meses" in texto_lower:
                self.contexto['tiempo_exacto_str'] = "varios meses"
            elif "años" in texto_lower or "anios" in texto_lower:
                self.contexto['tiempo_exacto_str'] = "varios años"
            return self.generar_informe_triaje()

        elif self.estado == 'crisis':
            if acto == 'confirmar_ayuda':
                self.estado = 'fin'
                return ("[LINEA DE CRISIS] Llama inmediatamente al 106 (Salud Mental Univalle) "
                        "o al numero nacional de emergencia 192 (linea gratuita 24/7). Por favor, busca apoyo "
                        "medico inmediato o acude a urgencias de tu IPS. Tu vida es valiosa y hay personas listas para apoyarte.")
            return "Por favor, dime si estas de acuerdo en que te brinde los numeros de emergencia inmediata (escribe 'SI')."

        elif self.estado == 'fin':
            self.estado = 'inicio'
            self.contexto = {
                'historia_oraciones': [],
                'dimensiones': set(),
                'max_sev': 'bajo',
                'escala_temporal': None,
                'crisis_detectada': False,
                'repeticiones_errores': 0,
                'sintoma_actual': None,
                'dim_actual': None,
                'sev_actual': None
            }
            return "He finalizado la sesion de evaluacion actual. Si deseas iniciar un nuevo triaje, escribe 'Hola'."

        return "Lamento no entender. Me podrias detallar mejor como te sientes emocional o fisicamente?"

    def actualizar_severidad(self, sev):
        sev_precedence = {'critico': 5, 'alto': 4, 'medio': 3, 'bajo': 2, 'neutro': 1, None: 1}
        actual = self.contexto['max_sev']
        if sev_precedence.get(sev, 1) > sev_precedence.get(actual, 1):
            self.contexto['max_sev'] = sev

    def generar_informe_triaje(self):
        sev_global = self.contexto['max_sev']
        dims = list(self.contexto['dimensiones'])
        escala = self.contexto['escala_temporal']

        nivel_triage = {
            'critico': 'Nivel I (Emergencia - Atencion Inmediata)',
            'alto': 'Nivel II (Urgencia - Atencion prioritaria en menos de 2 horas)',
            'medio': 'Nivel III (Prioridad Media - Consulta prioritaria externa en menos de 48 horas)',
            'bajo': 'Nivel IV (Prioridad Baja - Consulta psicologica externa ordinaria)'
        }

        traduc_dim = {
            'animo': 'Afectiva/Depresiva',
            'ansiedad': 'Ansiedad/Tension Emocional',
            'fisico': 'Sintomatologia Somatica/Fisica',
            'cognitivo': 'Cognitiva (Concentracion/Pensamientos)',
            'social': 'Social/Relacional',
            'neutro': 'General'
        }
        dims_str = ", ".join([traduc_dim.get(d, d) for d in dims if d != 'neutro'])
        if not dims_str:
            dims_str = "No especificada"

        escala_str = {
            'corto': 'Reciente (agudo, menos de 1 semana)',
            'medio': 'Subagudo (duracion intermedia, semanas)',
            'largo': 'Cronico (duracion prolongada, meses)',
            'muy_largo': 'Muy Cronico (permanente, anios)'
        }.get(escala, 'No especificada')

        recomendaciones = {
            'critico': "[!] Requiere intervencion de urgencias psiquiatricas/medicas inmediatas.",
            'alto': "[!] Se aconseja acudir a valoracion medica prioritaria y agendar sesion terapeutica de urgencia.",
            'medio': "Se sugiere agendar cita de asesoria psicologica prioritaria en la Universidad o con su red de salud.",
            'bajo': "Se recomienda acompanamiento psicologico regular para el manejo de sintomas leves."
        }

        informe = (
            f"[RESULTADO] === RESULTADO DEL TRIAJE PSICOLOGICO ===\n"
            f"  Dimensiones Clinicas Afectadas: {dims_str}\n"
            f"  Cronicidad / Duracion de Sintomas: {escala_str}\n"
            f"  Severidad Estimada: {sev_global.upper()} -- {nivel_triage.get(sev_global, 'Evaluacion general')}\n"
            f"  Recomendacion Clinica: {recomendaciones.get(sev_global, 'Sin recomendaciones.')}\n"
            f"===========================================\n"
            f"Te agradecemos por tu honestidad. Hay algo mas en lo que te pueda colaborar hoy?"
        )
        
        cat_map = {'ansiedad': 'Ansiedad', 'animo': 'Ánimo', 'fisico': 'Físico', 'cognitivo': 'Cognitivo', 'crisis': 'Crisis'}
        cat_str = cat_map.get(dims[0] if dims else 'neutro', 'Neutro')
        
        sev_map = {'bajo': 'Baja', 'medio': 'Media', 'alto': 'Alta', 'critico': 'Crítica'}
        sev_str = sev_map.get(sev_global, 'Media')
        
        tiempo_str = self.contexto.get('tiempo_exacto_str')
        if not tiempo_str:
            tiempo_str = {'corto': 'días', 'medio': 'semanas', 'largo': 'meses', 'muy_largo': 'años'}.get(escala, 'días')
            
        return f"{informe}\n\n[Categoría: {cat_str}, Intensidad: {sev_str}, Tiempo: {tiempo_str}]"


if __name__ == "__main__":
    conversaciones = [
        # Caso normal (con confirmación de síntoma y cronicidad)
        [
            "hola",
            "me siento triste",
            "si",
            "hace tres semanas",
            "gracias"
        ],
        # Ansiedad
        [
            "hola",
            "estoy muy ansioso",
            "si",
            "hace dos meses",
            "adios"
        ],
        # Problema físico
        [
            "hola",
            "estoy cansado",
            "si",
            "hace varios dias",
            "gracias"
        ],
        # Crisis
        [
            "hola",
            "quiero suicidarme",
            "si"
        ],
        # Recuperación de errores (aclaración)
        [
            "hola",
            "no entiendo nada de esto",
            "1", # selecciona emocional
            "si",
            "hace tres semanas",
            "gracias"
        ]
    ]

    for i, conv in enumerate(conversaciones, start=1):
        print(f"\n{'='*60}")
        print(f"CONVERSACIÓN {i}")
        print(f"{'='*60}")

        dialogo = DialogATN()

        for mensaje in conv:
            print(f"\nUsuario: {mensaje}")
            respuesta = dialogo.procesar_turno(mensaje)
            print(f"Estado: {dialogo.estado}")
            print(f"ATN: {respuesta}")