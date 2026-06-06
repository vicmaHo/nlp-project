
# Modulación de severidad según adverbio de intensidad
# Formato: (grado_adv, sev_adj) -> nueva_sev
MODULACION_SEVERIDAD = {
    ('muy_alto', 'alto'): 'alto',
    ('muy_alto', 'medio'): 'alto',
    ('muy_alto', 'bajo'): 'medio',
    ('alto', 'alto'): 'alto',
    ('alto', 'medio'): 'medio',
    ('alto', 'bajo'): 'medio',
    ('bajo', 'alto'): 'medio',
    ('bajo', 'medio'): 'bajo',
    ('bajo', 'bajo'): 'bajo',
}

# Precedencia de severidad
SEV_PRECEDENCE = {'critico': 5, 'alto': 4, 'medio': 3, 'bajo': 2, 'neutro': 1, None: 1}


def escalar_severidad(sev_actual, num_sintomas_negativos):
    """
    Escala la severidad según el número de síntomas negativos acumulados.
    """
    if num_sintomas_negativos >= 2 and sev_actual == 'medio':
        return 'alto'
    elif num_sintomas_negativos >= 3:
        return 'alto'
    return sev_actual


def actualizar_severidad_global(sev_actual, sev_nueva):
    """
    Actualiza la severidad global manteniendo la de mayor precedencia.
    """
    if SEV_PRECEDENCE.get(sev_nueva, 1) > SEV_PRECEDENCE.get(sev_actual, 1):
        return sev_nueva
    return sev_actual
