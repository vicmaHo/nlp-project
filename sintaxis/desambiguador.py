
import re
import os
from collections import defaultdict

# ── PARTE 1: Léxico clínico ambiguo ──────────────────────────────────
# Mapeo de palabras que presentan ambigüedad categorial clínica
lexico_ambiguo = {
    "siento": ["Vsent", "Vtrans"],  # me siento (Vsent) vs siento dolor (Vtrans)
    "bajo":   ["Adj", "Prep", "Vintr"],     # ánimo bajo (Adj) vs bajo presión (Prep) vs bajo peso (V)
    "sobre":  ["Prep", "N"],        # sobre mi ansiedad (Prep) vs sobre de pastillas (N)
    "como":   ["Conj", "Vintr"],    # triste como la noche (Conj) vs como poco (V)
}

def categorias(token):
    return lexico_ambiguo.get(token, [])

def es_ambiguo(token):
    return len(categorias(token)) > 1

def detectar_ambiguedad(oracion):
    tokens = re.findall(r'\b\w+\b', oracion.lower())
    return [(t, categorias(t)) for t in tokens if es_ambiguo(t)]


# ── PARTE 2: Frecuencias y probabilidades desde corpus clínico ───────
def construir_frecuencias(ruta_corpus):
    conteos = defaultdict(lambda: defaultdict(int))
    
    if not os.path.exists(ruta_corpus):
        raise FileNotFoundError(f"No se encontró el archivo de corpus en {ruta_corpus}")
        
    with open(ruta_corpus, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            partes = linea.split()
            if len(partes) == 2:
                palabra, categoria = partes
                conteos[palabra.lower()][categoria] += 1
                
    return {palabra: dict(cats) for palabra, cats in conteos.items()}

# Frecuencias de fallback si el corpus no está disponible
frecuencias_default = {
    "siento": {"Vsent": 420, "Vtrans": 110},   # Vsent es 79% más probable
    "bajo":   {"Adj": 350, "Prep": 120, "Vintr": 30}, # Adj es 70% más probable
    "sobre":  {"Prep": 280, "N": 40},          # Prep es 87% más probable
    "como":   {"Conj": 190, "Vintr": 110},     # Conj es 63% más probable
}

# Intentar cargar frecuencias desde el archivo del proyecto
dir_actual = os.path.dirname(os.path.abspath(__file__))
ruta_corpus_def = os.path.join(os.path.dirname(dir_actual), "corpus_clinico_ambiguo.txt")

try:
    frecuencias = construir_frecuencias(ruta_corpus_def)
except FileNotFoundError:
    frecuencias = frecuencias_default


def prob_categoria(palabra, categoria):
    if palabra not in frecuencias:
        return 0.0
    conteos = frecuencias[palabra]
    return conteos.get(categoria, 0) / sum(conteos.values())

def categoria_mas_probable(palabra):
    if palabra not in frecuencias:
        cats = categorias(palabra)
        return cats[0] if cats else None
    return max(frecuencias[palabra], key=frecuencias[palabra].get)


# ── PARTE 3: Desambiguador completo ──────────────────────────────────
def desambiguar(oracion):
    res_lineas = []
    tokens = re.findall(r'\b\w+\b', oracion.lower())
    for token in tokens:
        if es_ambiguo(token):
            cat = categoria_mas_probable(token)
            p = prob_categoria(token, cat)
            res_lineas.append(f"  {token:10s} -> {cat:6s}  (P={p:.2f})  *ambiguo*")
        elif categorias(token):
            res_lineas.append(f"  {token:10s} -> {categorias(token)[0]}")
        else:
            # Intentar ver si está en el léxico principal del triaje
            from gramatica import lexico as lexico_principal
            lex_p = lexico_principal.get(token)
            if lex_p:
                cat_p = lex_p.get('cat', 'DESCONOCIDO').upper()
                res_lineas.append(f"  {token:10s} -> {cat_p}")
            else:
                res_lineas.append(f"  {token:10s} -> DESCONOCIDO")
    return "\n".join(res_lineas)


# ── PARTE 4: Estadísticas de ambigüedad ──────────────────────────────
def estadisticas(oracion):
    tokens = re.findall(r'\b\w+\b', oracion.lower())
    if not tokens:
        return "  Oración vacía."
        
    ambiguos     = [t for t in tokens if es_ambiguo(t)]
    
    from gramatica import lexico as lexico_principal
    desconocidos = [t for t in tokens if not categorias(t) and t not in lexico_principal]
    conocidos    = [t for t in tokens if (categorias(t) or t in lexico_principal) and not es_ambiguo(t)]
    
    total = len(tokens)
    res = (
        f"  Total tokens:   {total}\n"
        f"  No ambiguos:    {len(conocidos):3d}  ({100*len(conocidos)/total:.0f}%)\n"
        f"  Ambiguos:       {len(ambiguos):3d}  ({100*len(ambiguos)/total:.0f}%)\n"
        f"  Desconocidos:   {len(desconocidos):3d}  ({100*len(desconocidos)/total:.0f}%)"
    )
    return res


# ── MAIN DE PRUEBA ────────────────────────────────────────────────────
if __name__ == "__main__":

    oraciones_prueba = [
        "me siento muy triste",
        "siento dolor en el pecho",
        "tengo el animo bajo",
        "estoy bajo mucha presion",
        "hablamos sobre mi ansiedad",
        "guarde el sobre de pastillas",
        "estoy triste como la noche",
        "como poco ultimamente",
        "me siento bajo presion y hablo sobre mi ansiedad"
    ]

    for i, oracion in enumerate(oraciones_prueba, start=1):
        print("=" * 70)
        print(f"ORACIÓN {i}: {oracion}")

        print("\n[1] Ambigüedades detectadas:")
        amb = detectar_ambiguedad(oracion)

        if amb:
            for palabra, cats in amb:
                print(f"  {palabra} -> {cats}")
        else:
            print("  No se encontraron palabras ambiguas.")

        print("\n[2] Desambiguación:")
        print(desambiguar(oracion))

        print("\n[3] Estadísticas:")
        print(estadisticas(oracion))

        print()