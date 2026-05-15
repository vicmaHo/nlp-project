import nltk

# Definición de la gramática libre de contexto.
grammar = nltk.CFG.fromstring(
    """
        S  -> NP VP
        VP -> V NP | VP PP
        PP -> P NP
        V  -> "vi"
        NP -> Det N | Det N PP | "yo"
        Det -> "al" | "los"
        N  -> "profesor" | "binoculares"
        P  -> "con"
    """
)

# Creación del parser tipo ChartParser
parser = nltk.ChartParser(grammar)

# Oración de prueba convertida en lista de tokens.
# split() separa cada palabra por espacios.
sentece = "yo vi al profesor con los binoculares".split()

# El parser puede generar más de un árbol
# si la oración tiene ambigüedad sintáctica.
for tree in parser.parse(sentece):
    # Imprimimos el árbol en formato texto.
    print(tree)

    # Muestra el árbol de derivación
    # de forma más visual en consola.
    tree.pretty_print()