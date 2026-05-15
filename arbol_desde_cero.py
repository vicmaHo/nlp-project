import matplotlib.pyplot as plt

# Clase que representa cada nodo del árbol sintáctico.
# Cada nodo tiene una etiqueta (por ejemplo S, NP, VP)
# y una lista de hijos que corresponden a las derivaciones.
class Nodo:
    def __init__(self, etiqueta, hijos=None):
        self.etiqueta = etiqueta
        self.hijos = hijos if hijos else []

# Gramática libre de contexto utilizada para el análisis.
# Cada clave representa un símbolo no terminal y
# las listas internas representan sus posibles producciones.
# gramatica = {
#     'S':   [['NP', 'VP']],
#     'NP':  [['Det', 'N'], ['N']],
#     'VP':  [['V', 'NP'], ['V']],
#     'Det': [['la'], ['el'], ['un']],
#     'N':   [['estudiante'], ['libro'], ['cafe']],
#     'V':   [['lee'], ['veo']]
# }

gramatica = {
    'S':   [['NP', 'VP']],
    'VP':  [['V', 'NP'], ['VP', 'PP']],
    'PP':  [['P', 'NP']],
    'V':   [['vi']],
    'NP':  [['Det', 'N'], ['Det', 'N', 'PP'], ['yo']],
    'Det': [['al'], ['los']],
    'N':   [['profesor'], ['binoculares']],
    'P':   [['con']]
}

# Función recursiva encargada de analizar la cadena.
# Recibe:
# - simbolo: símbolo actual a analizar
# - tokens: lista de palabras de la oración
# - pos: posición actual dentro de la lista
# - gramatica: reglas definidas anteriormente
def parse(simbolo, tokens, pos, gramatica):
    # Si el símbolo no está en la gramática,
    # entonces se trata de un terminal.
    if simbolo not in gramatica:
        # Verifica si el token actual coincide
        # con el terminal esperado.
        if pos < len(tokens) and tokens[pos] == simbolo:
            return tokens[pos], pos + 1
        return None, pos

    # Recorre todas las producciones posibles
    # asociadas al símbolo actual.
    for produccion in gramatica[simbolo]:
        # Se crea un nodo para representar
        # el símbolo analizado.
        nodo_actual = Nodo(simbolo)

        # Posición temporal para ir avanzando
        # durante el análisis.
        pos_actual  = pos

        # Variable de control para saber
        # si toda la producción fue válida.
        exito       = True

        # Analiza cada sub-símbolo de la producción.
        for subsimbolo in produccion:
            # Llamado recursivo para continuar
            # el análisis descendente.
            hijo, pos_actual = parse(subsimbolo, tokens,
                                     pos_actual, gramatica)
            
            # Si algún subanálisis falla,
            # se abandona esta producción.
            if hijo is None:
                exito = False
                break

            # Si fue exitoso, el hijo se agrega
            # al nodo actual.
            nodo_actual.hijos.append(hijo)

        # Si toda la producción fue válida,
        # se retorna el nodo construido.
        if exito:
            return nodo_actual, pos_actual
        
    # Si ninguna producción funcionó
    return None, pos

# Función para dibujar el árbol sintáctico.
# Utiliza matplotlib para representar nodos y conexiones.
def dibujar_arbol(nodo, ax, x, y, ancho):
    # Caso base:
    # si no es un objeto Nodo, entonces es un terminal.
    if not isinstance(nodo, Nodo):
        # Dibuja el terminal en color diferente.
        ax.text(x, y, nodo, ha='center', va='center', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='lightgreen'))
        return

    # Dibuja los símbolos no terminales.
    ax.text(x, y, nodo.etiqueta, ha='center', va='center', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='lightblue'))

    # Si el nodo no tiene hijos,
    # no hay nada más que dibujar.
    if not nodo.hijos:
        return

    # Cantidad de hijos del nodo actual.
    n      = len(nodo.hijos)

    # Punto inicial desde donde se distribuyen
    # horizontalmente los hijos.
    x_ini  = x - ancho / 2

    # Recorre y dibuja cada hijo.
    for hijo in nodo.hijos:
        ancho_hijo = ancho / n
        x_hijo     = x_ini + ancho_hijo / 2
        y_hijo     = y - 1
        ax.plot([x, x_hijo], [y - 0.15, y_hijo + 0.15], 'k-', lw=1.5)
        dibujar_arbol(hijo, ax, x_hijo, y_hijo, ancho_hijo)
        x_ini += ancho_hijo

# =========================
# PRUEBA
# =========================

# Oración a analizar.
#tokens = "la estudiante lee el libro".split()
tokens = "yo vi al profesor con los binoculares".split()

# Se inicia el análisis desde el símbolo inicial S.
arbol, pos_final = parse('S', tokens, 0, gramatica)

# Se verifica si toda la cadena fue reconocida.
if arbol and pos_final == len(tokens):
    print("Cadena valida")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    dibujar_arbol(arbol, ax, 5, 5.5, 10)
    plt.title("Árbol de Derivación", fontsize=12)
    plt.tight_layout()
    plt.show()
else:
    print("Cadena invalida o no reconocida")
