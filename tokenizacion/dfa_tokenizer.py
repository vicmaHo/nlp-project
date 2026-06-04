# -*- coding: utf-8 -*-
# =======================================================================
# TOKENIZADOR — AUTOMATA FINITO DETERMINISTA (DFA)
# Universidad del Valle — Procesamiento de Lenguaje Natural
# =======================================================================

class TokenizerDFA:
    """
    Automato Finito Determinista (DFA) para Tokenización y Normalización.
    Limpia signos de puntuación, pasa a minúsculas y separa palabras.
    Mantiene acentos en español (á, é, í, ó, ú, ü, ñ).

    Formalismo:
        Q = {0, 1}  (q_space, q_word)
        Σ = {a-z, 0-9, áéíóúüñ, espacio, puntuación}
        δ: función de transición
        q0 = 0 (estado inicial)
        F = {0} (estado final)
    """
    def __init__(self):
        self.state = 0

    def is_word_char(self, char):
        return char.isalnum() or char in "áéíóúüñ"

    def tokenize(self, text):
        if not text:
            return []

        text = text.lower().strip()
        tokens = []
        current_word = []
        self.state = 0

        for char in text:
            if self.state == 0:
                if self.is_word_char(char):
                    self.state = 1
                    current_word.append(char)
            elif self.state == 1:
                if self.is_word_char(char):
                    current_word.append(char)
                else:
                    tokens.append("".join(current_word))
                    current_word = []
                    self.state = 0

        if current_word:
            tokens.append("".join(current_word))

        return tokens

# =======================================================================
# PRUEBA DEL TOKENIZADOR
# =======================================================================
if __name__ == "__main__":
    tokenizer = TokenizerDFA()

    test_cases = [
        "Estoy muy feliz y emocionado hoy.",
        "Siento una tristeza profunda en mi corazón.",
        "¡Qué rabia tan grande me da esta situación!",
        "Tengo miedo de lo que pueda pasar mañana.",
        "Me siento tranquilo, sereno y en paz.",
        "La nostalgia me invade al recordar esos momentos.",
        "Estoy ansioso y nervioso por los resultados.",
        "Qué alegría tan inmensa ver a mi familia.",
    ]

    print("=" * 60)
    print("  PRUEBA DEL TOKENIZADOR DFA — EMOCIONES")
    print("=" * 60)

    for i, text in enumerate(test_cases, 1):
        tokens = tokenizer.tokenize(text)
        print(f"\nCaso {i}: {repr(text)}")
        print(f"Tokens : {tokens}")
        print(f"Total  : {len(tokens)} token(s)")

    print("\n" + "=" * 60)
    print("  MODO INTERACTIVO (escribe 'salir' para terminar)")
    print("=" * 60)

    while True:
        user_input = input("\nDescribe cómo te sientes: ")
        if user_input.strip().lower() == "salir":
            print("¡Hasta luego!")
            break
        result = tokenizer.tokenize(user_input)
        print(f"Tokens : {result}")
        print(f"Total  : {len(result)} token(s)")