# -*- coding: utf-8 -*-
# =======================================================================
# UNIFICACIÓN DE RASGOS SINTÁCTICOS Y CLÍNICOS
# Universidad del Valle — Procesamiento de Lenguaje Natural
# =======================================================================

# =======================================================================
# ALGORITMO DE UNIFICACIÓN GENERAL DE DAGs (Clase 7)
# =======================================================================

def unificar(dag1, dag2):
    """
    Algoritmo de unificación general para estructuras de rasgos (DAGs).
    Implementación idéntica a la vista en la Clase 7 del curso.

    Reglas:
    1. Copia dag1 en el resultado.
    2. Para cada rasgo (r, v) en dag2:
       - Si r no está en el resultado: agrega (r, v).
       - Si r sí está con valor v':
         * Si v == v': continúa (compatible).
         * Si v != v': falla → retorna None (conflicto).
       - Si ambos valores son diccionarios (DAGs anidados): unifica recursivamente.
    3. Retorna el resultado combinado.

    Ejemplo:
      dag1 = {'gen': 'masc', 'num': 'sing'}
      dag2 = {'gen': 'masc', 'cat': 'det'}
      Resultado → {'gen': 'masc', 'num': 'sing', 'cat': 'det'}
    """
    resultado = dict(dag1)

    for rasgo, valor in dag2.items():
        if rasgo in resultado:
            # Si ambos valores son sub-DAGs → unificamos recursivamente hacia adentro
            if isinstance(resultado[rasgo], dict) and isinstance(valor, dict):
                sub = unificar(resultado[rasgo], valor)
                if sub is None:
                    return None       # el conflicto está en la sub-estructura
                resultado[rasgo] = sub
            elif resultado[rasgo] != valor:
                # Mismo rasgo, valores distintos → CONFLICTO.
                return None
            # Si los valores son iguales, no hay nada que hacer — ya está en resultado
        else:
            # El rasgo no existía en dag1, simplemente lo agregamos
            resultado[rasgo] = valor

    return resultado


# =======================================================================
# UNIFICACIÓN DE CONCORDANCIA SINTÁCTICA (Adaptación para Triaje)
# =======================================================================

def unificar_concordancia(dag1, dag2, rasgos_concordancia=('gen', 'num', 'pers')):
    """
    Unifica rasgos de concordancia sintáctica (género, número, persona).
    Soporta 'neutro' como comodín (wildcard).
    Retorna el diccionario unificado si es compatible, de lo contrario None.
    """
    res = {}
    for r in rasgos_concordancia:
        v1 = dag1.get(r)
        v2 = dag2.get(r)

        if v1 is None or v1 == 'neutro':
            res[r] = v2 if v2 is not None else 'neutro'
        elif v2 is None or v2 == 'neutro':
            res[r] = v1
        elif v1 == v2:
            res[r] = v1
        else:
            return None
    return res


def combinar_rasgos_clinicos(dict_list):
    """
    Combina y sintetiza rasgos clínicos a través de las ramas del árbol sintáctico.
    Escala severidad cuando se detectan múltiples síntomas negativos.
    """
    dim_precedence = {'crisis': 6, 'ansiedad': 5, 'animo': 4, 'social': 3, 'fisico': 2, 'cognitivo': 2, 'neutro': 1}
    sev_precedence = {'critico': 5, 'alto': 4, 'medio': 3, 'bajo': 2, 'neutro': 1, None: 1}
    escala_precedence = {'muy_largo': 4, 'largo': 3, 'medio': 2, 'corto': 1, None: 0}

    final_dim = 'neutro'
    final_sev = 'neutro'
    final_pol = 'neutro'
    final_escala = None

    has_neg = False
    has_pos = False
    num_sintomas_negativos = 0

    for d in dict_list:
        if not d:
            continue

        dim = d.get('dim')
        if dim and dim_precedence.get(dim, 1) > dim_precedence.get(final_dim, 1):
            final_dim = dim

        sev = d.get('sev')
        if sev and sev_precedence.get(sev, 1) > sev_precedence.get(final_sev, 1):
            final_sev = sev

        pol = d.get('pol')
        if pol == 'neg':
            has_neg = True
            num_sintomas_negativos += 1
        elif pol == 'pos':
            has_pos = True

        escala = d.get('escala')
        if escala and escala_precedence.get(escala, 0) > escala_precedence.get(final_escala, 0):
            final_escala = escala

    if num_sintomas_negativos >= 2 and final_sev == 'medio':
        final_sev = 'alto'
    elif num_sintomas_negativos >= 3:
        final_sev = 'alto'

    if has_neg:
        final_pol = 'neg'
    elif has_pos:
        final_pol = 'pos'
    else:
        final_pol = 'neutro'

    return {
        'dim': final_dim,
        'sev': final_sev,
        'pol': final_pol,
        'escala': final_escala
    }
