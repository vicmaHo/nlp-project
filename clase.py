# "el" > determinante, masculino, singular
dag_el = {
    "cat": "det",
    "gen": "masc",
    "num": "sing"
}

# "las" -> det, femenino, plural

dag_las = {
    "cat": "deg",
    "gen": "fem",
    "num": "plur"
}

# DAG anidado
dag_np_complejo = {
    "cat": "np",
    "num": "sing",
    "acuerdo": {
        "gen": "masc",
        "num": "sing"
    }
}

print(f"dag_ejemplo {dag_el}")
print(f"dag_ejemplo {dag_las}")
print(f"dag_ejemplo {dag_np_complejo}")

# =======================
# PARTE 2: algoritmo de unificación
# =======================


# Combinar DAGs en uno.
# So los dos tiene el mismo rasgo con el mismo

def unificar(dag1, dag2):
    resultado = dict(dag1)
    
    for rasgo, valor in dag2.items():
        # El rasgo ya existe en resultado - hay
        if rasgo in resultado:
            if isinstance(resultado[rasgo], dict) and isinstance(valor, dict):
                sub = unificar(resultado[rasgo], valor)
                if sub is None:
                    return None
                resultado[rasgo] = sub
                
            elif resultado[rasgo] != valor:
                return None
                
            
            # si los valores son iguales
        else:
            # el rasgo no exista en dag1, solo se adiciona en el dag2
            resultado[rasgo] = valor
            
    else:
        return resultado
    
    
print(f"PRUEBA UNIFICACION")


# Caso 1: mismo genero y mismo numero

a = {
    "gen": "masc",
    "num": "sing",
}

b = {
    "gen": "masc",
    "num": "sing",
}


print(f"resultado = {unificar(a, b)}")

# Caso 2: rasgos distintos pero no sean contradictorios
a = {
    "cat": "det",
    "gen": "masc",
}

b = {
    "num": "sing",
}

print(f"resultado = {unificar(a, b)}")


# Caso 3: el mismo rasgo con valores diferetnes

a = {
    "gen": "masc",
    "num": "sing",
}

b = {
    "gen": "fem",
    "num": "sing",
}

print(f"resultado = {unificar(a, b)}")


# Caso 3

a = {
    "gen": "masc",
    "num": "sing",
}

b = {
    "gen": "masc",
    "num": "plur",
}

print(f"resultado = {unificar(a, b)}")


# =======================
# PARTE 3: lexico con estructuras DAGs
# =======================

# Cada palabra del vocabulario tiene su propio DAG con sus rasgos
# Cuando el parser analiza una oración, consulta aqui los rasgos de cada token

lexico = {
    # Determinantes - cada uno lleva su género y número
    "el": {"cat": "det", "gen": "masc", "num": "sing"},
    "la": {"cat": "det", "gen": "fem", "num": "sing"},
    "los": {"cat": "det", "gen": "masc", "num": "plur"},
    "las": {"cat": "det", "gen": "fem", "num": "plur"},
    
    # Sustantivos - también llevan género y número
    "gato": {"cat": "n", "gen": "masc", "num": "sing"},
    "gata": {"cat": "n", "gen": "fem", "num": "sing"},
    "gatos": {"cat": "n", "gen": "masc", "num": "plur"},
    "perros": {"cat": "n", "gen": "masc", "num": "plur"},
    "niña": {"cat": "n", "gen": "fem", "num": "sing"},
    "niñas": {"cat": "n", "gen": "fem", "num": "plur"},
    
    # Verbos - Llevan número para concordar con los sujetos
    "corre": {"cat": "v", "num": "sing", "accion": "correr"},
    "corren": {"cat": "v", "num": "plur", "accion": "correr"},
    "duerme": {"cat": "v", "num": "sing", "accion": "dormir"},
    "duermen": {"cat": "v", "num": "plur", "accion": "dormir"},
    "juegan": {"cat": "v", "num": "plur", "accion": "jugar"}
    
}

print("LEXICO CON DAGs")
for palabra, rasgos in lexico.items()



def parse_np(tokens, pos):
    if pos + 1 >= len(tokens):
        return None, pos
    
    # tomamos los dos candidatos en la posicion actual
    # palabra_det = tokens [0] = 'el'
    
    palabra_det = tokens[pos]
    palabra_n = tokens[pos + 1]
    
    # Ambas palabras tiene nque estar en el lexico - 
    if palabra_det not in lexico or palabra_n not in lexico:
        print(f"{palabra_det} o {palabra_n} no estan en el elxico")
        return None, pos
    # consultamos los ragos de cada palabra en el lexico
    
    rasgos_det = lexico[palabra_det]
    rasgos_n = lexico[palabra_n]
    
    # verificaciones
    if rasgos_det.get("cat") != "det":
        print(f"{rasgos_det.get("cat")} No es un determinante")
        return None, pos
        
        
    if rasgos_det.get("cat") != "n":
        print(f" {rasgos_det.get("cat")} no es un sustantivo")
        return None, pos
    
    concord_det = {'gen': rasgos_det['gen'], 'num': rasgos_det['num']}
    concord_n = {'gen': rasgos_n['gen'], 'num': rasgos_det['num']}
    
    unificado = unificar(concord_det, concord_n)
    
    if unificado is None:
        print("Conflicto: lso rasgos no tiene concordancia")
        return None, pos
    
    # todo concodó -armamos la estructura del DAG
    
    np = {
        "cat": "np",
        "gen": unificado["gen"],
        "num": unificado["num"],
        "det": palabra_det,
        "n": palabra_n
    }
    
    
    print(f" NP: {palabra_det} + {palabra_n} rasgos = {np}")
    
    
    return np, pos + 2



    



