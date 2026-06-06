
# =======================================================================
# PARTE 1 — GRAMÁTICA EN FORMATO CFG
# Los terminales (palabras) están dentro de la gramática misma.
# =======================================================================

gramatica_cfg = {

    # ── REGLAS ESTRUCTURALES ───────────────────────────────────────────

    # S (Oración): seis patrones de entrada del paciente.
    # Se contemplan sujeto explícito/tácito, negación y marcador de frecuencia.
    'S': [
        ['NP', 'VP'],               # "yo estoy muy triste"
        ['VP'],                     # "estoy muy triste"         (sujeto tácito)
        ['Neg', 'VP'],              # "no puedo dormir"
        ['NP', 'Neg', 'VP'],        # "yo no puedo dormir"
        ['Adv_frec', 'VP'],         # "siempre lloro"
        ['Adv_frec', 'Neg', 'VP'],  # "casi nunca duermo bien"
    ],

    # NP (Sintagma Nominal): sujeto o complemento nominal.
    'NP': [
        ['Pro'],                    # "yo"
        ['Det', 'N'],               # "la tristeza" / "mi familia"
        ['Det', 'N', 'SP'],         # "las ganas de vivir"
        ['N'],                      # "ansiedad"                 (sin det.)
        ['N', 'SP'],                # "pensamientos de muerte"
    ],

    # VP (Sintagma Verbal): núcleo del predicado.
    # Siete estructuras verbales organizadas por relevancia clínica:
    'VP': [
        # 1. Copulativos ─ estado general del paciente
        ['Vcop', 'AP'],                     # "estoy triste"
        ['Vcop', 'AP', 'SP'],               # "estoy mal desde hace semanas"

        # 2. Reflexivos de emoción (Clit + Vsent) ─ autopercepción emocional
        ['Clit', 'Vsent', 'AP'],            # "me siento muy solo"
        ['Clit', 'Vsent', 'AP', 'SP'],      # "me siento mal desde hace días"

        # 3. Dificultad / esfuerzo (Clit + Vcuesta) ─ limitaciones funcionales
        ['Clit', 'Vcuesta', 'Vinf'],        # "me cuesta dormir"
        ['Clit', 'Vcuesta', 'Vinf', 'NP'], # "me cuesta controlar mis emociones"

        # 4. Transitivos ─ síntomas que el paciente "tiene" o "experimenta"
        ['Vtrans', 'NP'],                   # "tengo miedo"
        ['Vtrans', 'NP', 'SP'],             # "tengo pensamientos de muerte"

        # 5. Modales ─ deseos, capacidades y planes del paciente
        ['Vmod', 'Vinf'],                   # "quiero vivir"
        ['Vmod', 'Vinf', 'NP'],             # "quiero controlar mi ansiedad"

        # 6. Modales de crisis ─ ideación suicida / autolesión (PRIORIDAD CRÍTICA)
        ['Vmod', 'Vcris', 'NP'],            # "quiero hacerme daño"
        ['Vmod', 'Vcris'],                  # "quiero suicidarme"

        # 7. Intransitivos ─ síntomas comportamentales observables
        ['Vintr'],                          # "lloro"
        ['Vintr', 'SP'],                    # "pienso en la muerte"
        ['Vintr', 'Adv_frec'],              # "lloro constantemente"
    ],

    # AP (Sintagma Adjetival): predicado o modificador adjetival.
    # El Adv_int permite capturar gradación del síntoma ("muy", "demasiado").
    'AP': [
        ['Adj'],                    # "triste"
        ['Adv_int', 'Adj'],         # "muy triste"
        ['Adj', 'SP'],              # "cansado de todo"
        ['Adv_int', 'Adj', 'SP'],   # "muy cansado de todo"
    ],

    # SP (Sintagma Preposicional): adjunto o complemento de régimen.
    'SP': [
        ['Prep', 'NP'],             # "de nada" / "en el futuro"
        ['Prep', 'AP'],             # "sin energía"
        ['Prep_temp', 'Exp_temp'],  # "desde hace semanas"
    ],

    # Exp_temp: duración del síntoma — informa cronicidad para el triaje.
    # Permite distinguir: episodio agudo (días) vs. cuadro crónico (meses/años).
    'Exp_temp': [
        ['Prep_temp', 'Tunidad'],          # "hace días"
        ['Prep_temp', 'Num', 'Tunidad'],   # "hace tres semanas"
        ['Num', 'Tunidad'],                # "tres meses"  (tras "desde")
        ['Tunidad'],                       # "semanas"     (tras "desde hace")
    ],

    # Vinf: complemento verbal en infinitivo, con o sin objeto directo.
    'Vinf': [
        ['V_inf'],                  # "dormir"
        ['V_inf', 'NP'],            # "controlar mis emociones"
    ],

    # ── TERMINALES ─────────────────────────────────────────────────────

    # Unidades temporales — escala de cronicidad del síntoma
    'Tunidad': [
        ['días'],       # reciente
        ['semanas'],    # subagudo
        ['meses'],      # crónico
        ['años'],       # muy crónico
    ],

    # Negación
    'Neg': [
        ['no'],         # negación simple: "no puedo dormir"
        ['nunca'],      # negación temporal: "nunca tengo energía"
        ['jamás'],      # negación enfática: "jamás me siento bien"
    ],

    # Pronombres sujeto
    'Pro': [
        ['yo'], ['él'], ['ella'], ['uno'],
    ],

    # Clíticos (pronombres átonos — fundamentales en construcciones reflexivas)
    'Clit': [
        ['me'], ['se'],
    ],

    # Determinantes
    'Det': [
        ['el'], ['la'], ['los'], ['las'],
        ['un'], ['una'], ['mi'], ['mis'],
    ],

    # Preposiciones generales
    'Prep': [
        ['de'], ['en'], ['con'], ['sin'],
        ['sobre'], ['por'], ['a'], ['hacia'],
    ],

    # Preposiciones temporales (marcan inicio o duración del síntoma)
    'Prep_temp': [
        ['desde'],      # inicio: "desde hace semanas"
        ['hace'],       # duración: "hace días"
    ],

    # Cuantificadores / números (acompañan a Tunidad)
    'Num': [
        ['dos'], ['tres'], ['varios'], ['muchos'], ['algunos'],
    ],

    # ── Sustantivos — agrupados por dimensión clínica ──────────────────
    'N': [
        # — dim: animo — estados afectivos depresivos
        ['tristeza'], ['angustia'], ['desesperanza'], ['desesperación'],
        ['culpa'], ['vergüenza'], ['vacío'], ['soledad'], ['llanto'],

        # — dim: ansiedad — miedo y activación
        ['ansiedad'], ['miedo'], ['pánico'], ['estrés'],
        ['nerviosismo'], ['preocupación'],

        # — dim: fisico — síntomas somáticos
        ['insomnio'], ['agotamiento'], ['fatiga'],
        ['sueño'], ['apetito'],

        # — dim: cognitivo — síntomas del pensamiento
        ['pensamientos'], ['confusión'],

        # — dim: animo secundario —
        ['ira'], ['rabia'],

        # — dim: crisis — conceptos de alto riesgo (PRIORIDAD CRÍTICA)
        ['muerte'], ['daño'],

        # — dim: neutro — contexto y recursos del paciente
        ['vida'], ['futuro'], ['nada'], ['todo'],
        ['energía'], ['ganas'], ['trabajo'], ['familia'],
        ['tiempo'], ['razón'], ['emociones'],
    ],

    # ── Adjetivos — agrupados por dimensión clínica ────────────────────
    'Adj': [
        # — dim: animo — ánimo deprimido
        ['triste'],
        ['deprimido'],    ['deprimida'],
        ['desesperado'],  ['desesperada'],
        ['angustiado'],   ['angustiada'],
        ['agotado'],      ['agotada'],
        ['solo'],         ['sola'],
        ['vacío'],        ['vacía'],
        ['perdido'],      ['perdida'],

        # — dim: ansiedad —
        ['ansioso'],      ['ansiosa'],
        ['nervioso'],     ['nerviosa'],
        ['asustado'],     ['asustada'],
        ['abrumado'],     ['abrumada'],

        # — estado general (aplica a múltiples dim) —
        ['mal'], ['bien'], ['peor'], ['mejor'],

        # — dim: cognitivo —
        ['confundido'],   ['confundida'],
        ['bloqueado'],    ['bloqueada'],

        # — otros —
        ['irritable'], ['inútil'],
        ['cansado'],      ['cansada'],
    ],

    # Adverbios de intensidad — modulan la severidad percibida del síntoma
    'Adv_int': [
        ['muy'],              # intensidad alta
        ['bastante'],         # intensidad alta
        ['demasiado'],        # intensidad muy alta (señal de alarma)
        ['poco'],             # intensidad baja
        ['extremadamente'],   # intensidad muy alta (señal de alarma)
        ['casi'],             # aproximación
        ['tan'],              # comparativo
    ],

    # Adverbios de frecuencia — modulan la cronicidad del síntoma
    'Adv_frec': [
        ['siempre'],
        ['nunca'],
        ['constantemente'],
        ['frecuentemente'],
        ['continuamente'],
        ['a', 'veces'],             # bitoken
        ['todo', 'el', 'tiempo'],   # tritoken
    ],

    # ── Verbos ─────────────────────────────────────────────────────────

    # Copulativos: describen estado del paciente
    'Vcop': [
        ['estoy'], ['soy'], ['ando'],
    ],

    # De percepción/emoción (siempre acompañados del clítico 'me')
    'Vsent': [
        ['siento'], ['encuentro'], ['noto'],
    ],

    # De dificultad / esfuerzo (siempre acompañados del clítico 'me')
    'Vcuesta': [
        ['cuesta'], ['resulta'],
    ],

    # Transitivos: síntomas que el paciente posee o experimenta
    'Vtrans': [
        ['tengo'], ['necesito'], ['siento'],
        ['experimento'], ['busco'],
    ],

    # Modales: expresan voluntad, capacidad y plan de acción
    'Vmod': [
        ['puedo'], ['quiero'], ['logro'],
        ['consigo'], ['debo'], ['deseo'],
    ],

    # Intransitivos: síntomas comportamentales
    'Vintr': [
        ['lloro'], ['pienso'], ['duermo'], ['como'],
        ['vivo'], ['trabajo'], ['funciono'], ['descanso'],
    ],

    # Infinitivos generales: complemento de verbos modales o de dificultad
    'V_inf': [
        ['dormir'], ['comer'], ['trabajar'], ['vivir'],
        ['funcionar'], ['concentrarme'], ['relacionarme'],
        ['levantarme'], ['continuar'], ['controlar'],
        ['pensar'], ['salir'], ['descansar'],
    ],

    # Infinitivos de crisis: ACTIVAN PROTOCOLO DE ATENCIÓN URGENTE
    'Vcris': [
        ['hacerme'], ['quitarme'],
        ['lastimarme'], ['suicidarme'], ['morirme'],
    ],
}


# =======================================================================
# PARTE 2 — GRAMÁTICA EN FORMATO DCG
# Las reglas estructurales permanecen igual.
# Las palabras salen al léxico y llevan sus rasgos lingüísticos y clínicos.
# =======================================================================

# ── Reglas estructurales (idénticas a CFG, sin terminales) ─────────────

gramatica_dcg = {

    'S': [
        ['NP', 'VP'],
        ['VP'],
        ['Neg', 'VP'],
        ['NP', 'Neg', 'VP'],
        ['Adv_frec', 'VP'],
        ['Adv_frec', 'Neg', 'VP'],
    ],

    'NP': [
        ['Pro'],
        ['Det', 'N'],
        ['Det', 'N', 'SP'],
        ['N'],
        ['N', 'SP'],
    ],

    'VP': [
        ['Vcop', 'AP'],
        ['Vcop', 'AP', 'SP'],
        ['Clit', 'Vsent', 'AP'],
        ['Clit', 'Vsent', 'AP', 'SP'],
        ['Clit', 'Vcuesta', 'Vinf'],
        ['Clit', 'Vcuesta', 'Vinf', 'NP'],
        ['Vtrans', 'NP'],
        ['Vtrans', 'NP', 'SP'],
        ['Vmod', 'Vinf'],
        ['Vmod', 'Vinf', 'NP'],
        ['Vmod', 'Vcris', 'NP'],
        ['Vmod', 'Vcris'],
        ['Vintr'],
        ['Vintr', 'SP'],
        ['Vintr', 'Adv_frec'],
    ],

    'AP': [
        ['Adj'],
        ['Adv_int', 'Adj'],
        ['Adj', 'SP'],
        ['Adv_int', 'Adj', 'SP'],
    ],

    'SP': [
        ['Prep', 'NP'],
        ['Prep', 'AP'],
        ['Prep_temp', 'Exp_temp'],
    ],

    'Exp_temp': [
        ['Prep_temp', 'Tunidad'],
        ['Prep_temp', 'Num', 'Tunidad'],
        ['Num', 'Tunidad'],
        ['Tunidad'],
    ],

    'Vinf': [
        ['V_inf'],
        ['V_inf', 'NP'],
    ],
}


# ── Léxico con rasgos (DCG) ─────────────────────────────────────────────
#
# Rasgos lingüísticos estándar:
#   cat   — categoría gramatical
#   gen   — género: 'masc' | 'fem' | 'neutro'
#   num   — número: 'sing' | 'plur'
#   pers  — persona: '1' | '3'
#
# Rasgos clínicos para el triaje:
#   dim   — dimensión psicológica: 'animo' | 'ansiedad' | 'fisico' |
#            'cognitivo' | 'crisis' | 'social' | 'neutro'
#   sev   — severidad: 'bajo' | 'medio' | 'alto' | 'critico'
#   pol   — polaridad: 'pos' | 'neg' | 'neutro'
#   grado — grado del adverbio de intensidad: 'bajo' | 'alto' | 'muy_alto'
#   frec  — frecuencia del adverbio: 'siempre' | 'alto' | 'bajo' | 'nunca'
#   escala— escala temporal: 'corto' | 'medio' | 'largo' | 'muy_largo'

lexico = {

    # ── Determinantes ─────────────────────────────────────────────────
    'el':   {'cat': 'det', 'gen': 'masc',   'num': 'sing'},
    'la':   {'cat': 'det', 'gen': 'fem',    'num': 'sing'},
    'los':  {'cat': 'det', 'gen': 'masc',   'num': 'plur'},
    'las':  {'cat': 'det', 'gen': 'fem',    'num': 'plur'},
    'un':   {'cat': 'det', 'gen': 'masc',   'num': 'sing'},
    'una':  {'cat': 'det', 'gen': 'fem',    'num': 'sing'},
    'mi':   {'cat': 'det', 'gen': 'neutro', 'num': 'sing'},
    'mis':  {'cat': 'det', 'gen': 'neutro', 'num': 'plur'},

    # ── Pronombres sujeto ─────────────────────────────────────────────
    'yo':   {'cat': 'pro', 'gen': 'neutro', 'num': 'sing', 'pers': '1'},
    'él':   {'cat': 'pro', 'gen': 'masc',   'num': 'sing', 'pers': '3'},
    'ella': {'cat': 'pro', 'gen': 'fem',    'num': 'sing', 'pers': '3'},
    'uno':  {'cat': 'pro', 'gen': 'masc',   'num': 'sing', 'pers': '3'},

    # ── Clíticos ──────────────────────────────────────────────────────
    'me': {'cat': 'clit', 'num': 'sing', 'pers': '1'},
    'se': {'cat': 'clit', 'num': 'sing', 'pers': '3'},

    # ── Negación ──────────────────────────────────────────────────────
    'no':    {'cat': 'neg', 'tipo': 'simple'},
    'nunca': {'cat': 'neg', 'tipo': 'temporal'},
    'jamás': {'cat': 'neg', 'tipo': 'temporal'},

    # ── Preposiciones generales ───────────────────────────────────────
    'de':    {'cat': 'prep', 'tipo': 'genitivo'},
    'en':    {'cat': 'prep', 'tipo': 'locativo'},
    'con':   {'cat': 'prep', 'tipo': 'comitatvo'},
    'sin':   {'cat': 'prep', 'tipo': 'privativo'},   # ← señal: "sin ganas", "sin energía"
    'sobre': {'cat': 'prep', 'tipo': 'locativo'},
    'por':   {'cat': 'prep', 'tipo': 'causal'},
    'a':     {'cat': 'prep', 'tipo': 'direccional'},
    'hacia': {'cat': 'prep', 'tipo': 'direccional'},

    # ── Preposiciones temporales ──────────────────────────────────────
    'desde': {'cat': 'prep_temp', 'tipo': 'inicio'},    # punto de inicio
    'hace':  {'cat': 'prep_temp', 'tipo': 'duracion'},  # duración hacia atrás

    # ── Cuantificadores ───────────────────────────────────────────────
    'dos':     {'cat': 'num', 'val': 2},
    'tres':    {'cat': 'num', 'val': 3},
    'varios':  {'cat': 'num', 'val': None},
    'muchos':  {'cat': 'num', 'val': None},
    'algunos': {'cat': 'num', 'val': None},

    # ── Unidades de tiempo ────────────────────────────────────────────
    'días':    {'cat': 'tunidad', 'escala': 'corto'},
    'semanas': {'cat': 'tunidad', 'escala': 'medio'},
    'meses':   {'cat': 'tunidad', 'escala': 'largo'},
    'años':    {'cat': 'tunidad', 'escala': 'muy_largo'},

    # ── Sustantivos — dim: animo (estados afectivos) ──────────────────
    'tristeza':      {'cat': 'n', 'gen': 'fem',    'num': 'sing', 'dim': 'animo',    'pol': 'neg', 'sev': 'medio'},
    'angustia':      {'cat': 'n', 'gen': 'fem',    'num': 'sing', 'dim': 'ansiedad', 'pol': 'neg', 'sev': 'alto'},
    'desesperanza':  {'cat': 'n', 'gen': 'fem',    'num': 'sing', 'dim': 'animo',    'pol': 'neg', 'sev': 'alto'},
    'desesperación': {'cat': 'n', 'gen': 'fem',    'num': 'sing', 'dim': 'animo',    'pol': 'neg', 'sev': 'alto'},
    'culpa':         {'cat': 'n', 'gen': 'fem',    'num': 'sing', 'dim': 'animo',    'pol': 'neg', 'sev': 'medio'},
    'vergüenza':     {'cat': 'n', 'gen': 'fem',    'num': 'sing', 'dim': 'animo',    'pol': 'neg', 'sev': 'bajo'},
    'vacío':         {'cat': 'n', 'gen': 'masc',   'num': 'sing', 'dim': 'animo',    'pol': 'neg', 'sev': 'medio'},
    'soledad':       {'cat': 'n', 'gen': 'fem',    'num': 'sing', 'dim': 'animo',    'pol': 'neg', 'sev': 'medio'},
    'llanto':        {'cat': 'n', 'gen': 'masc',   'num': 'sing', 'dim': 'animo',    'pol': 'neg', 'sev': 'medio'},
    'ira':           {'cat': 'n', 'gen': 'fem',    'num': 'sing', 'dim': 'animo',    'pol': 'neg', 'sev': 'medio'},
    'rabia':         {'cat': 'n', 'gen': 'fem',    'num': 'sing', 'dim': 'animo',    'pol': 'neg', 'sev': 'medio'},

    # ── Sustantivos — dim: ansiedad ───────────────────────────────────
    'ansiedad':     {'cat': 'n', 'gen': 'fem',  'num': 'sing', 'dim': 'ansiedad', 'pol': 'neg', 'sev': 'medio'},
    'miedo':        {'cat': 'n', 'gen': 'masc', 'num': 'sing', 'dim': 'ansiedad', 'pol': 'neg', 'sev': 'medio'},
    'pánico':       {'cat': 'n', 'gen': 'masc', 'num': 'sing', 'dim': 'ansiedad', 'pol': 'neg', 'sev': 'alto'},
    'estrés':       {'cat': 'n', 'gen': 'masc', 'num': 'sing', 'dim': 'ansiedad', 'pol': 'neg', 'sev': 'medio'},
    'nerviosismo':  {'cat': 'n', 'gen': 'masc', 'num': 'sing', 'dim': 'ansiedad', 'pol': 'neg', 'sev': 'bajo'},
    'preocupación': {'cat': 'n', 'gen': 'fem',  'num': 'sing', 'dim': 'ansiedad', 'pol': 'neg', 'sev': 'bajo'},

    # ── Sustantivos — dim: fisico ─────────────────────────────────────
    'insomnio':    {'cat': 'n', 'gen': 'masc', 'num': 'sing', 'dim': 'fisico', 'pol': 'neg', 'sev': 'medio'},
    'agotamiento': {'cat': 'n', 'gen': 'masc', 'num': 'sing', 'dim': 'fisico', 'pol': 'neg', 'sev': 'medio'},
    'fatiga':      {'cat': 'n', 'gen': 'fem',  'num': 'sing', 'dim': 'fisico', 'pol': 'neg', 'sev': 'bajo'},
    'sueño':       {'cat': 'n', 'gen': 'masc', 'num': 'sing', 'dim': 'fisico', 'pol': 'neutro', 'sev': 'neutro'},
    'apetito':     {'cat': 'n', 'gen': 'masc', 'num': 'sing', 'dim': 'fisico', 'pol': 'neutro', 'sev': 'neutro'},

    # ── Sustantivos — dim: cognitivo ──────────────────────────────────
    'pensamientos': {'cat': 'n', 'gen': 'masc', 'num': 'plur', 'dim': 'cognitivo', 'pol': 'neutro', 'sev': 'medio'},
    'confusión':    {'cat': 'n', 'gen': 'fem',  'num': 'sing', 'dim': 'cognitivo', 'pol': 'neg',    'sev': 'medio'},

    # ── Sustantivos — dim: crisis (PRIORIDAD CRÍTICA) ─────────────────
    'muerte': {'cat': 'n', 'gen': 'fem',  'num': 'sing', 'dim': 'crisis', 'pol': 'neg', 'sev': 'alto'},
    'daño':   {'cat': 'n', 'gen': 'masc', 'num': 'sing', 'dim': 'crisis', 'pol': 'neg', 'sev': 'alto'},

    # ── Sustantivos — dim: neutro (contexto y recursos) ───────────────
    'vida':      {'cat': 'n', 'gen': 'fem',    'num': 'sing', 'dim': 'neutro', 'pol': 'pos',    'sev': 'neutro'},
    'futuro':    {'cat': 'n', 'gen': 'masc',   'num': 'sing', 'dim': 'neutro', 'pol': 'neutro', 'sev': 'neutro'},
    'nada':      {'cat': 'n', 'gen': 'neutro', 'num': 'sing', 'dim': 'neutro', 'pol': 'neg',    'sev': 'medio'},
    'todo':      {'cat': 'n', 'gen': 'neutro', 'num': 'sing', 'dim': 'neutro', 'pol': 'neutro', 'sev': 'neutro'},
    'energía':   {'cat': 'n', 'gen': 'fem',    'num': 'sing', 'dim': 'fisico', 'pol': 'neutro', 'sev': 'neutro'},
    'ganas':     {'cat': 'n', 'gen': 'fem',    'num': 'plur', 'dim': 'animo',  'pol': 'neutro', 'sev': 'neutro'},
    'trabajo':   {'cat': 'n', 'gen': 'masc',   'num': 'sing', 'dim': 'neutro', 'pol': 'neutro', 'sev': 'neutro'},
    'familia':   {'cat': 'n', 'gen': 'fem',    'num': 'sing', 'dim': 'neutro', 'pol': 'neutro', 'sev': 'neutro'},
    'tiempo':    {'cat': 'n', 'gen': 'masc',   'num': 'sing', 'dim': 'neutro', 'pol': 'neutro', 'sev': 'neutro'},
    'razón':     {'cat': 'n', 'gen': 'fem',    'num': 'sing', 'dim': 'neutro', 'pol': 'neutro', 'sev': 'neutro'},
    'emociones': {'cat': 'n', 'gen': 'fem',    'num': 'plur', 'dim': 'animo',  'pol': 'neutro', 'sev': 'neutro'},

    # ── Adjetivos — dim: animo (ánimo deprimido) ──────────────────────
    'triste':       {'cat': 'adj', 'gen': 'neutro', 'num': 'sing', 'dim': 'animo',    'pol': 'neg', 'sev': 'medio'},
    'deprimido':    {'cat': 'adj', 'gen': 'masc',   'num': 'sing', 'dim': 'animo',    'pol': 'neg', 'sev': 'alto'},
    'deprimida':    {'cat': 'adj', 'gen': 'fem',    'num': 'sing', 'dim': 'animo',    'pol': 'neg', 'sev': 'alto'},
    'desesperado':  {'cat': 'adj', 'gen': 'masc',   'num': 'sing', 'dim': 'animo',    'pol': 'neg', 'sev': 'alto'},
    'desesperada':  {'cat': 'adj', 'gen': 'fem',    'num': 'sing', 'dim': 'animo',    'pol': 'neg', 'sev': 'alto'},
    'angustiado':   {'cat': 'adj', 'gen': 'masc',   'num': 'sing', 'dim': 'ansiedad', 'pol': 'neg', 'sev': 'alto'},
    'angustiada':   {'cat': 'adj', 'gen': 'fem',    'num': 'sing', 'dim': 'ansiedad', 'pol': 'neg', 'sev': 'alto'},
    'agotado':      {'cat': 'adj', 'gen': 'masc',   'num': 'sing', 'dim': 'fisico',   'pol': 'neg', 'sev': 'medio'},
    'agotada':      {'cat': 'adj', 'gen': 'fem',    'num': 'sing', 'dim': 'fisico',   'pol': 'neg', 'sev': 'medio'},
    'solo':         {'cat': 'adj', 'gen': 'masc',   'num': 'sing', 'dim': 'animo',    'pol': 'neg', 'sev': 'medio'},
    'sola':         {'cat': 'adj', 'gen': 'fem',    'num': 'sing', 'dim': 'animo',    'pol': 'neg', 'sev': 'medio'},
    'vacío':        {'cat': 'adj', 'gen': 'masc',   'num': 'sing', 'dim': 'animo',    'pol': 'neg', 'sev': 'medio'},
    'vacía':        {'cat': 'adj', 'gen': 'fem',    'num': 'sing', 'dim': 'animo',    'pol': 'neg', 'sev': 'medio'},
    'perdido':      {'cat': 'adj', 'gen': 'masc',   'num': 'sing', 'dim': 'animo',    'pol': 'neg', 'sev': 'medio'},
    'perdida':      {'cat': 'adj', 'gen': 'fem',    'num': 'sing', 'dim': 'animo',    'pol': 'neg', 'sev': 'medio'},

    # ── Adjetivos — dim: ansiedad ─────────────────────────────────────
    'ansioso':  {'cat': 'adj', 'gen': 'masc', 'num': 'sing', 'dim': 'ansiedad', 'pol': 'neg', 'sev': 'medio'},
    'ansiosa':  {'cat': 'adj', 'gen': 'fem',  'num': 'sing', 'dim': 'ansiedad', 'pol': 'neg', 'sev': 'medio'},
    'nervioso': {'cat': 'adj', 'gen': 'masc', 'num': 'sing', 'dim': 'ansiedad', 'pol': 'neg', 'sev': 'bajo'},
    'nerviosa': {'cat': 'adj', 'gen': 'fem',  'num': 'sing', 'dim': 'ansiedad', 'pol': 'neg', 'sev': 'bajo'},
    'asustado': {'cat': 'adj', 'gen': 'masc', 'num': 'sing', 'dim': 'ansiedad', 'pol': 'neg', 'sev': 'medio'},
    'asustada': {'cat': 'adj', 'gen': 'fem',  'num': 'sing', 'dim': 'ansiedad', 'pol': 'neg', 'sev': 'medio'},
    'abrumado': {'cat': 'adj', 'gen': 'masc', 'num': 'sing', 'dim': 'ansiedad', 'pol': 'neg', 'sev': 'alto'},
    'abrumada': {'cat': 'adj', 'gen': 'fem',  'num': 'sing', 'dim': 'ansiedad', 'pol': 'neg', 'sev': 'alto'},

    # ── Adjetivos — estado general ────────────────────────────────────
    'mal':    {'cat': 'adj', 'gen': 'neutro', 'num': 'sing', 'dim': 'animo', 'pol': 'neg', 'sev': 'medio'},
    'bien':   {'cat': 'adj', 'gen': 'neutro', 'num': 'sing', 'dim': 'animo', 'pol': 'pos', 'sev': 'neutro'},
    'peor':   {'cat': 'adj', 'gen': 'neutro', 'num': 'sing', 'dim': 'animo', 'pol': 'neg', 'sev': 'alto'},
    'mejor':  {'cat': 'adj', 'gen': 'neutro', 'num': 'sing', 'dim': 'animo', 'pol': 'pos', 'sev': 'neutro'},

    # ── Adjetivos — dim: cognitivo ────────────────────────────────────
    'confundido': {'cat': 'adj', 'gen': 'masc', 'num': 'sing', 'dim': 'cognitivo', 'pol': 'neg', 'sev': 'bajo'},
    'confundida': {'cat': 'adj', 'gen': 'fem',  'num': 'sing', 'dim': 'cognitivo', 'pol': 'neg', 'sev': 'bajo'},
    'bloqueado':  {'cat': 'adj', 'gen': 'masc', 'num': 'sing', 'dim': 'cognitivo', 'pol': 'neg', 'sev': 'medio'},
    'bloqueada':  {'cat': 'adj', 'gen': 'fem',  'num': 'sing', 'dim': 'cognitivo', 'pol': 'neg', 'sev': 'medio'},

    # ── Adjetivos — otros ─────────────────────────────────────────────
    'irritable': {'cat': 'adj', 'gen': 'neutro', 'num': 'sing', 'dim': 'animo',  'pol': 'neg', 'sev': 'medio'},
    'inútil':    {'cat': 'adj', 'gen': 'neutro', 'num': 'sing', 'dim': 'animo',  'pol': 'neg', 'sev': 'alto'},
    'cansado':   {'cat': 'adj', 'gen': 'masc',   'num': 'sing', 'dim': 'fisico', 'pol': 'neg', 'sev': 'bajo'},
    'cansada':   {'cat': 'adj', 'gen': 'fem',    'num': 'sing', 'dim': 'fisico', 'pol': 'neg', 'sev': 'bajo'},

    # ── Adverbios de intensidad ───────────────────────────────────────
    'muy':            {'cat': 'adv_int', 'grado': 'alto'},
    'bastante':       {'cat': 'adv_int', 'grado': 'alto'},
    'demasiado':      {'cat': 'adv_int', 'grado': 'muy_alto'},   # señal de alarma
    'poco':           {'cat': 'adv_int', 'grado': 'bajo'},
    'extremadamente': {'cat': 'adv_int', 'grado': 'muy_alto'},   # señal de alarma
    'casi':           {'cat': 'adv_int', 'grado': 'medio'},
    'tan':            {'cat': 'adv_int', 'grado': 'alto'},

    # ── Adverbios de frecuencia ───────────────────────────────────────
    # Nota: "a veces" y "todo el tiempo" se manejan como bitokens/tritokens
    # en la CFG. Aquí cada token lleva su rasgo individual.
    'siempre':        {'cat': 'adv_frec', 'frec': 'siempre'},
    'nunca':          {'cat': 'adv_frec', 'frec': 'nunca'},
    'constantemente': {'cat': 'adv_frec', 'frec': 'alto'},
    'frecuentemente': {'cat': 'adv_frec', 'frec': 'alto'},
    'continuamente':  {'cat': 'adv_frec', 'frec': 'alto'},
    'veces':          {'cat': 'adv_frec', 'frec': 'bajo'},   # segundo token de "a veces"

    # ── Verbos copulativos ────────────────────────────────────────────
    'estoy': {'cat': 'vcop', 'num': 'sing', 'pers': '1'},
    'soy':   {'cat': 'vcop', 'num': 'sing', 'pers': '1'},
    'ando':  {'cat': 'vcop', 'num': 'sing', 'pers': '1'},

    # ── Verbos de percepción / emoción (requieren clítico 'me') ───────
    'siento':    {'cat': 'vsent', 'num': 'sing', 'pers': '1'},
    'encuentro': {'cat': 'vsent', 'num': 'sing', 'pers': '1'},
    'noto':      {'cat': 'vsent', 'num': 'sing', 'pers': '1'},

    # ── Verbos de dificultad (requieren clítico 'me') ─────────────────
    'cuesta':  {'cat': 'vcuesta', 'num': 'sing', 'pers': '3'},
    'resulta': {'cat': 'vcuesta', 'num': 'sing', 'pers': '3'},

    # ── Verbos transitivos ────────────────────────────────────────────
    'tengo':       {'cat': 'vtrans', 'num': 'sing', 'pers': '1'},
    'necesito':    {'cat': 'vtrans', 'num': 'sing', 'pers': '1'},
    'experimento': {'cat': 'vtrans', 'num': 'sing', 'pers': '1'},
    'busco':       {'cat': 'vtrans', 'num': 'sing', 'pers': '1'},

    # ── Verbos modales ────────────────────────────────────────────────
    'puedo':   {'cat': 'vmod', 'num': 'sing', 'pers': '1', 'tipo': 'capacidad'},
    'quiero':  {'cat': 'vmod', 'num': 'sing', 'pers': '1', 'tipo': 'deseo'},
    'logro':   {'cat': 'vmod', 'num': 'sing', 'pers': '1', 'tipo': 'logro'},
    'consigo': {'cat': 'vmod', 'num': 'sing', 'pers': '1', 'tipo': 'logro'},
    'debo':    {'cat': 'vmod', 'num': 'sing', 'pers': '1', 'tipo': 'obligacion'},
    'deseo':   {'cat': 'vmod', 'num': 'sing', 'pers': '1', 'tipo': 'deseo'},

    # ── Verbos intransitivos ──────────────────────────────────────────
    'lloro':    {'cat': 'vintr', 'num': 'sing', 'pers': '1', 'dim': 'animo',    'sev': 'medio'},
    'pienso':   {'cat': 'vintr', 'num': 'sing', 'pers': '1', 'dim': 'cognitivo','sev': 'bajo'},
    'duermo':   {'cat': 'vintr', 'num': 'sing', 'pers': '1', 'dim': 'fisico',   'sev': 'neutro'},
    'como':     {'cat': 'vintr', 'num': 'sing', 'pers': '1', 'dim': 'fisico',   'sev': 'neutro'},
    'vivo':     {'cat': 'vintr', 'num': 'sing', 'pers': '1', 'dim': 'neutro',   'sev': 'neutro'},
    'trabajo':  {'cat': 'vintr', 'num': 'sing', 'pers': '1', 'dim': 'neutro',   'sev': 'neutro'},
    'funciono': {'cat': 'vintr', 'num': 'sing', 'pers': '1', 'dim': 'fisico',   'sev': 'neutro'},
    'descanso': {'cat': 'vintr', 'num': 'sing', 'pers': '1', 'dim': 'fisico',   'sev': 'neutro'},

    # ── Verbos en infinitivo ──────────────────────────────────────────
    'dormir':        {'cat': 'vinf', 'dim': 'fisico',    'sev': 'neutro'},
    'comer':         {'cat': 'vinf', 'dim': 'fisico',    'sev': 'neutro'},
    'trabajar':      {'cat': 'vinf', 'dim': 'neutro',    'sev': 'neutro'},
    'vivir':         {'cat': 'vinf', 'dim': 'neutro',    'sev': 'neutro'},
    'funcionar':     {'cat': 'vinf', 'dim': 'fisico',    'sev': 'neutro'},
    'concentrarme':  {'cat': 'vinf', 'dim': 'cognitivo', 'sev': 'neutro'},
    'relacionarme':  {'cat': 'vinf', 'dim': 'social',    'sev': 'neutro'},
    'levantarme':    {'cat': 'vinf', 'dim': 'fisico',    'sev': 'neutro'},
    'continuar':     {'cat': 'vinf', 'dim': 'neutro',    'sev': 'neutro'},
    'controlar':     {'cat': 'vinf', 'dim': 'cognitivo', 'sev': 'neutro'},
    'pensar':        {'cat': 'vinf', 'dim': 'cognitivo', 'sev': 'neutro'},
    'salir':         {'cat': 'vinf', 'dim': 'social',    'sev': 'neutro'},
    'descansar':     {'cat': 'vinf', 'dim': 'fisico',    'sev': 'neutro'},

    # ── Infinitivos de crisis — ACTIVAN PROTOCOLO URGENTE ─────────────
    'hacerme':    {'cat': 'vcris', 'dim': 'crisis', 'sev': 'critico'},
    'quitarme':   {'cat': 'vcris', 'dim': 'crisis', 'sev': 'critico'},
    'lastimarme': {'cat': 'vcris', 'dim': 'crisis', 'sev': 'critico'},
    'suicidarme': {'cat': 'vcris', 'dim': 'crisis', 'sev': 'critico'},
    'morirme':    {'cat': 'vcris', 'dim': 'crisis', 'sev': 'critico'},
}


# =======================================================================
# EJEMPLOS DE ORACIONES QUE LA GRAMÁTICA CUBRE
# =======================================================================

# Formato: (tokens, descripcion, nivel_triage_esperado)
oraciones_ejemplo = [

    # — Severidad BAJA —
    ("me siento un poco nervioso".split(),
     "Ansiedad leve, sujeto tácito",           "bajo"),

    ("a veces me cuesta dormir".split(),
     "Síntoma físico con frecuencia baja",      "bajo"),

    # — Severidad MEDIA —
    ("estoy muy triste desde hace semanas".split(),
     "Ánimo deprimido con cronicidad",          "medio"),

    ("no puedo concentrarme".split(),
     "Síntoma cognitivo + negación",            "medio"),

    ("tengo mucho miedo".split(),
     "Ansiedad con cuantificador",              "medio"),

    ("lloro constantemente".split(),
     "Síntoma conductual con frecuencia alta",  "medio"),

    ("yo no tengo ganas de nada".split(),
     "Apatía con sujeto explícito y negación",  "medio"),

    ("me siento muy solo desde hace meses".split(),
     "Ánimo + soledad + cronicidad larga",      "medio"),

    # — Severidad ALTA —
    ("estoy desesperado".split(),
     "Ánimo deprimido severo",                  "alto"),

    ("me siento extremadamente abrumado".split(),
     "Ansiedad severa con intensidad máxima",   "alto"),

    ("tengo pensamientos de muerte".split(),
     "Ideación pasiva (sin plan explícito)",    "alto"),

    ("nunca duermo y no como".split(),
     "Síntomas físicos graves + negación",      "alto"),

    # — Severidad CRÍTICA —
    ("quiero hacerme daño".split(),
     "Ideación activa de autolesión",           "critico"),

    ("quiero quitarme la vida".split(),
     "Ideación suicida activa",                 "critico"),

    ("deseo suicidarme".split(),
     "Ideación suicida directa",               "critico"),
    
]

if __name__ == '__main__':
    print("=" * 65)
    print("GRAMÁTICA CFG — No terminales:", len(gramatica_cfg))
    print("=" * 65)
    for nt, producciones in gramatica_cfg.items():
        for p in producciones:
            print(f"  {nt:12s} → {' '.join(p)}")

    print("\n" + "=" * 65)
    print("GRAMÁTICA DCG — Reglas estructurales:", len(gramatica_dcg))
    print("=" * 65)
    for nt, producciones in gramatica_dcg.items():
        for p in producciones:
            print(f"  {nt:12s} → {' '.join(p)}")

    print("\n" + "=" * 65)
    print(f"LÉXICO DCG — Entradas: {len(lexico)}")
    print("=" * 65)
    for palabra, rasgos in lexico.items():
        print(f"  '{palabra}': {rasgos}")

    print("\n" + "=" * 65)
    print("ORACIONES DE PRUEBA")
    print("=" * 65)
    for tokens, desc, nivel in oraciones_ejemplo:
        print(f"  [{nivel.upper():8s}] '{' '.join(tokens)}'")
        print(f"           → {desc}")