
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gramatica import gramatica_dcg, lexico
from tokenizacion.dfa_tokenizer import TokenizerDFA
from sintaxis.arbol import Nodo
from sintaxis.unificacion import unificar_concordancia, combinar_rasgos_clinicos
from util.severidad import MODULACION_SEVERIDAD


class ParserDCG:
    """
    Parser Descendente con Backtracking y Unificación de Rasgos (DCG).
    Reconoce la gramática de triaje psicológico, valida concordancia
    sintáctica y realiza extracción semántica clínica.
    """
    def __init__(self):
        self.map_categorias = {
            'Det': 'det', 'Pro': 'pro', 'Clit': 'clit', 'Neg': 'neg',
            'Prep': 'prep', 'Prep_temp': 'prep_temp', 'Num': 'num',
            'Tunidad': 'tunidad', 'N': 'n', 'Adj': 'adj',
            'Adv_int': 'adv_int', 'Adv_frec': 'adv_frec',
            'Vcop': 'vcop', 'Vsent': 'vsent', 'Vcuesta': 'vcuesta',
            'Vtrans': 'vtrans', 'Vmod': 'vmod', 'Vintr': 'vintr',
            'V_inf': 'vinf', 'Vcris': 'vcris'
        }

    def consultar_lexico(self, token, simbolo=None):
        if token == "a veces":
            return {'cat': 'adv_frec', 'frec': 'bajo', 'texto': 'a veces'}
        if token == "todo el tiempo":
            return {'cat': 'adv_frec', 'frec': 'alto', 'texto': 'todo el tiempo'}
        if token == "un poco":
            return {'cat': 'adv_int', 'grado': 'bajo', 'texto': 'un poco'}
        if token == "mucho":
            return {'cat': 'det', 'gen': 'neutro', 'num': 'sing', 'grado': 'alto'}
        
        # Manejo de ambigüedad léxica resolviendo dinámicamente según el símbolo del parser
        cat_buscada = self.map_categorias.get(simbolo) if simbolo else None
        
        lexico_ambiguo_rasgos = {
            "siento": {
                "vsent": {'cat': 'vsent', 'num': 'sing', 'pers': '1'},
                "vtrans": {'cat': 'vtrans', 'num': 'sing', 'pers': '1'}
            },
            "bajo": {
                "adj": {'cat': 'adj', 'gen': 'masc', 'num': 'sing', 'dim': 'animo', 'pol': 'neg', 'sev': 'medio'},
                "prep": {'cat': 'prep', 'tipo': 'posicion'},
                "vintr": {'cat': 'vintr', 'num': 'sing', 'pers': '1'}
            },
            "sobre": {
                "prep": {'cat': 'prep', 'tipo': 'locativo'},
                "n": {'cat': 'n', 'gen': 'masc', 'num': 'sing', 'dim': 'neutro'}
            },
            "un": {
                "det": {'cat': 'det', 'gen': 'masc', 'num': 'sing'},
                "num": {'cat': 'num', 'val': 1}
            },
            "una": {
                "det": {'cat': 'det', 'gen': 'fem', 'num': 'sing'},
                "num": {'cat': 'num', 'val': 1}
            }
        }
        
        if token in lexico_ambiguo_rasgos:
            if cat_buscada and cat_buscada in lexico_ambiguo_rasgos[token]:
                return lexico_ambiguo_rasgos[token][cat_buscada]
            first_cat = list(lexico_ambiguo_rasgos[token].keys())[0]
            return lexico_ambiguo_rasgos[token][first_cat]

        # Búsqueda normal
        res = lexico.get(token, None)
        if res is not None:
            return res
            
        # Normalizar acentos y probar
        def normalizar(s):
            replacements = {
                'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ü': 'u'
            }
            return "".join(replacements.get(c, c) for c in s)
            
        token_norm = normalizar(token)
        for k, v in lexico.items():
            if normalizar(k) == token_norm:
                return v
                
        # Probar mapeando ñ a n y viceversa
        token_norm_n = token_norm.replace('ñ', 'n')
        for k, v in lexico.items():
            k_norm = normalizar(k).replace('ñ', 'n')
            if k_norm == token_norm_n:
                return v
                
        return None

    def parse_simbolo(self, simbolo, tokens, pos):
        if simbolo in self.map_categorias:
            if pos < len(tokens):
                token = tokens[pos]
                rasgos_palabra = self.consultar_lexico(token, simbolo)
                if rasgos_palabra and rasgos_palabra.get('cat') == self.map_categorias[simbolo]:
                    nodo = Nodo(simbolo, hijos=[token], rasgos=rasgos_palabra.copy())
                    return nodo, pos + 1
            return None, pos

        if simbolo in gramatica_dcg:
            mejor_nodo = None
            mejor_pos = pos

            for produccion in gramatica_dcg[simbolo]:
                hijos = []
                pos_actual = pos
                exito = True

                for subsimbolo in produccion:
                    hijo, pos_actual = self.parse_simbolo(subsimbolo, tokens, pos_actual)
                    if hijo is None:
                        exito = False
                        break
                    hijos.append(hijo)

                if exito:
                    nodo_padre = self.procesar_unificacion_y_rasgos(simbolo, produccion, hijos)
                    if nodo_padre is not None and pos_actual > mejor_pos:
                        mejor_nodo = nodo_padre
                        mejor_pos = pos_actual
                        if mejor_pos == len(tokens):
                            return mejor_nodo, mejor_pos

            if mejor_nodo is not None:
                return mejor_nodo, mejor_pos

        return None, pos

    def procesar_unificacion_y_rasgos(self, simbolo, produccion, hijos):
        rasgos_sintetizados = {}

        if simbolo == 'S':
            if produccion == ['NP', 'VP']:
                np, vp = hijos[0], hijos[1]
                unif = unificar_concordancia(np.rasgos, vp.rasgos, ['num'])
                if unif is None: return None
                rasgos_sintetizados = combinar_rasgos_clinicos([np.rasgos, vp.rasgos])
            elif produccion == ['NP', 'Neg', 'VP']:
                np, neg, vp = hijos[0], hijos[1], hijos[2]
                unif = unificar_concordancia(np.rasgos, vp.rasgos, ['num'])
                if unif is None: return None
                rasgos_sintetizados = combinar_rasgos_clinicos([np.rasgos, vp.rasgos])
                rasgos_sintetizados = self.aplicar_negacion_a_rasgos(rasgos_sintetizados, vp)
            elif len(hijos) == 1 and produccion == ['VP']:
                rasgos_sintetizados = hijos[0].rasgos.copy()
            elif produccion == ['Neg', 'VP']:
                rasgos_sintetizados = hijos[1].rasgos.copy()
                rasgos_sintetizados = self.aplicar_negacion_a_rasgos(rasgos_sintetizados, hijos[1])
            elif 'Adv_frec' in produccion:
                adv = hijos[0]
                vp = hijos[2] if 'Neg' in produccion else hijos[1]
                rasgos_sintetizados = combinar_rasgos_clinicos([h.rasgos for h in hijos])
                if adv.rasgos.get('frec') == 'alto' and rasgos_sintetizados.get('sev') == 'medio':
                    rasgos_sintetizados['sev'] = 'alto'
                if adv.rasgos.get('frec') == 'bajo' and rasgos_sintetizados.get('sev') in ['medio', 'neutro', None]:
                    rasgos_sintetizados['sev'] = 'bajo'
                if adv.rasgos.get('frec') == 'nunca' or adv.rasgos.get('tipo') == 'temporal':
                    rasgos_sintetizados = self.aplicar_negacion_a_rasgos(rasgos_sintetizados, vp)
                elif 'Neg' in produccion:
                    rasgos_sintetizados = self.aplicar_negacion_a_rasgos(rasgos_sintetizados, vp)

        elif simbolo == 'NP':
            if produccion == ['Det', 'N'] or produccion == ['Det', 'N', 'SP']:
                det, n = hijos[0], hijos[1]
                unif = unificar_concordancia(det.rasgos, n.rasgos, ['gen', 'num'])
                if unif is None: return None
                sp_rasgos = hijos[2].rasgos if len(hijos) == 3 else {}
                rasgos_sintetizados = combinar_rasgos_clinicos([n.rasgos, sp_rasgos])
                rasgos_sintetizados.update(unif)
                
                # Modulación de severidad por determinante si tiene grado (ej: mucho/mucha)
                if det.rasgos.get('grado') is not None:
                    grado = det.rasgos.get('grado')
                    sev_original = n.rasgos.get('sev', 'medio')
                    nueva_sev = MODULACION_SEVERIDAD.get((grado, sev_original), sev_original)
                    rasgos_sintetizados['sev'] = nueva_sev
                    
                # Propagar persona
                if 'pers' in n.rasgos:
                    rasgos_sintetizados['pers'] = n.rasgos['pers']
            else:
                rasgos_sintetizados = combinar_rasgos_clinicos([h.rasgos for h in hijos])
                if len(hijos) == 1:
                    rasgos_sintetizados.update(hijos[0].rasgos)

        elif simbolo == 'VP':
            if 'Vcop' in produccion:
                vcop, ap = hijos[0], hijos[1]
                unif = unificar_concordancia(vcop.rasgos, ap.rasgos, ['num'])
                if unif is None: return None
                sp_rasgos = hijos[2].rasgos if len(hijos) == 3 else {}
                rasgos_sintetizados = combinar_rasgos_clinicos([ap.rasgos, sp_rasgos])
            elif 'Vsent' in produccion:
                clit, vsent, ap = hijos[0], hijos[1], hijos[2]
                unif_v = unificar_concordancia(clit.rasgos, vsent.rasgos, ['num', 'pers'])
                if unif_v is None: return None
                unif_ap = unificar_concordancia(vsent.rasgos, ap.rasgos, ['num'])
                if unif_ap is None: return None
                sp_rasgos = hijos[3].rasgos if len(hijos) == 4 else {}
                rasgos_sintetizados = combinar_rasgos_clinicos([ap.rasgos, sp_rasgos])
            elif 'Vcuesta' in produccion:
                clit, vcuesta, vinf = hijos[0], hijos[1], hijos[2]
                np_rasgos = hijos[3].rasgos if len(hijos) == 4 else {}
                rasgos_sintetizados = combinar_rasgos_clinicos([vinf.rasgos, np_rasgos])
            elif 'Vmod' in produccion:
                vmod, v_sec = hijos[0], hijos[1]
                np_rasgos = hijos[2].rasgos if len(hijos) == 3 else {}
                rasgos_sintetizados = combinar_rasgos_clinicos([v_sec.rasgos, np_rasgos])
                if vmod.rasgos.get('tipo') == 'deseo' and v_sec.rasgos.get('dim') == 'crisis':
                    rasgos_sintetizados['dim'] = 'crisis'
                    rasgos_sintetizados['sev'] = 'critico'
                    rasgos_sintetizados['pol'] = 'neg'
            else:
                rasgos_sintetizados = combinar_rasgos_clinicos([h.rasgos for h in hijos])

        elif simbolo == 'AP':
            if produccion == ['Adj']:
                rasgos_sintetizados = hijos[0].rasgos.copy()
            elif produccion == ['Adv_int', 'Adj'] or produccion == ['Adv_int', 'Adj', 'SP']:
                adv, adj = hijos[0], hijos[1]
                sp_rasgos = hijos[2].rasgos if len(hijos) == 3 else {}
                rasgos_sintetizados = combinar_rasgos_clinicos([adj.rasgos, sp_rasgos])
                grado = adv.rasgos.get('grado')
                sev_original = adj.rasgos.get('sev', 'medio')
                nueva_sev = MODULACION_SEVERIDAD.get((grado, sev_original), sev_original)
                rasgos_sintetizados['sev'] = nueva_sev
            elif produccion == ['Adj', 'SP']:
                rasgos_sintetizados = combinar_rasgos_clinicos([hijos[0].rasgos, hijos[1].rasgos])

        elif simbolo == 'SP':
            rasgos_sintetizados = combinar_rasgos_clinicos([h.rasgos for h in hijos])

        elif simbolo == 'Exp_temp':
            rasgos_sintetizados = combinar_rasgos_clinicos([h.rasgos for h in hijos])

        elif simbolo == 'Vinf':
            rasgos_sintetizados = combinar_rasgos_clinicos([h.rasgos for h in hijos])

        return Nodo(simbolo, hijos=hijos, rasgos=rasgos_sintetizados)

    def aplicar_negacion_a_rasgos(self, rasgos, nodo_vp):
        res = rasgos.copy()
        texto_vp = nodo_vp.get_text().lower()

        if any(w in texto_vp for w in ["muerte", "suicidarme", "daño", "quitarme", "lastimarme", "morirme"]):
            res['dim'] = 'crisis'
            res['sev'] = 'bajo'
            res['pol'] = 'pos'
        elif any(w in texto_vp for w in ["bien", "mejor"]):
            res['pol'] = 'neg'
            res['sev'] = 'medio'
            res['dim'] = 'animo'
        elif any(w in texto_vp for w in ["dormir", "duermo", "duerma", "duerme", "sueño"]):
            res['dim'] = 'fisico'
            res['sev'] = 'medio'
            res['pol'] = 'neg'
        elif any(w in texto_vp for w in ["comer", "como", "coma", "apetito"]):
            res['dim'] = 'fisico'
            res['sev'] = 'medio'
            res['pol'] = 'neg'
        elif any(w in texto_vp for w in ["concentr", "pensar", "pienso"]):
            res['dim'] = 'cognitivo'
            res['sev'] = 'medio'
            res['pol'] = 'neg'
        elif any(w in texto_vp for w in ["miedo", "ansiedad", "triste", "siento"]):
            res['pol'] = 'neg'
            if res.get('sev') in ['neutro', None]:
                res['sev'] = 'medio'

        return res

    def parsear_oracion(self, oracion_texto):
        dfa = TokenizerDFA()
        tokens_sucios = dfa.tokenize(oracion_texto)

        tokens_procesados = []
        i = 0
        n = len(tokens_sucios)
        while i < n:
            if i + 2 < n and tokens_sucios[i] == "todo" and tokens_sucios[i+1] == "el" and tokens_sucios[i+2] == "tiempo":
                tokens_procesados.append("todo el tiempo")
                i += 3
            elif i + 1 < n and tokens_sucios[i] == "un" and tokens_sucios[i+1] == "poco":
                tokens_procesados.append("un poco")
                i += 2
            elif i + 1 < n and tokens_sucios[i] == "a" and tokens_sucios[i+1] == "veces":
                tokens_procesados.append("a veces")
                i += 2
            else:
                tokens_procesados.append(tokens_sucios[i])
                i += 1

        if "y" in tokens_procesados:
            idx_y = tokens_procesados.index("y")
            parte_izq = tokens_procesados[:idx_y]
            parte_der = tokens_procesados[idx_y + 1:]

            arbol_izq, pos_izq = self.parse_simbolo('S', parte_izq, 0)
            arbol_der, pos_der = self.parse_simbolo('S', parte_der, 0)

            if (arbol_izq and pos_izq == len(parte_izq) and
                arbol_der and pos_der == len(parte_der)):
                rasgos_comb = combinar_rasgos_clinicos([arbol_izq.rasgos, arbol_der.rasgos])
                nodo_conj = Nodo('S', hijos=[arbol_izq, Nodo('Conj', hijos=['y']), arbol_der], rasgos=rasgos_comb)
                return nodo_conj

        arbol, pos_final = self.parse_simbolo('S', tokens_procesados, 0)

        if arbol is not None and pos_final == len(tokens_procesados):
            return arbol
        return None
