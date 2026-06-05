
class Nodo:
    """
    Representa un nodo en el Árbol de Derivación Sintáctica.
    Almacena la etiqueta (símbolo), hijos y rasgos unificados/sintetizados.
    """
    def __init__(self, etiqueta, hijos=None, rasgos=None):
        self.etiqueta = etiqueta
        self.hijos = hijos if hijos else []
        self.rasgos = rasgos if rasgos else {}

    def is_terminal(self):
        return len(self.hijos) == 1 and isinstance(self.hijos[0], str)

    def get_text(self):
        if self.is_terminal():
            return self.hijos[0]
        return " ".join([h.get_text() if isinstance(h, Nodo) else str(h) for h in self.hijos])

    def __repr__(self):
        return f"({self.etiqueta} {self.rasgos})"


class TreeVisualizer:
    """
    Dibuja el Árbol de Derivación Sintáctica en dos formatos:
    - Representación en Consola (Texto ASCII jerárquico).
    - Diagrama Gráfico interactivo usando Matplotlib (guardable como imagen).
    """
    @staticmethod
    def print_ascii(nodo, prefix="", is_last=True):
        if nodo is None:
            return ""

        connector = "+-- " if is_last else "|-- "
        res = prefix + connector + f"[{nodo.etiqueta}]"

        rasgos_str = []
        for k in ['dim', 'sev', 'pol', 'escala']:
            if k in nodo.rasgos and nodo.rasgos[k] is not None:
                rasgos_str.append(f"{k}={nodo.rasgos[k]}")
        if rasgos_str:
            res += " (" + ", ".join(rasgos_str) + ")"

        res += "\n"

        new_prefix = prefix + ("    " if is_last else "|   ")

        if nodo.is_terminal():
            res += new_prefix + f"+-- \"{nodo.hijos[0]}\"\n"
        else:
            for idx, hijo in enumerate(nodo.hijos):
                last_child = (idx == len(nodo.hijos) - 1)
                res += TreeVisualizer.print_ascii(hijo, new_prefix, last_child)

        return res

    @staticmethod
    def draw_matplotlib(nodo, file_path="arbol_derivacion.png"):
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("  [Aviso] Matplotlib no esta instalado. Solo se mostrara el arbol en ASCII.")
            return False

        fig, ax = plt.subplots(figsize=(12, 7))
        ax.axis('off')

        def get_coords(node, depth=0, x_left=0.0, x_right=1.0):
            if not isinstance(node, Nodo):
                return {}

            x_mid = (x_left + x_right) / 2.0
            y = 10.0 - depth * 1.5

            coords = {node: (x_mid, y)}

            if node.is_terminal():
                coords[node.hijos[0]] = (x_mid, y - 1.0)
            else:
                n = len(node.hijos)
                dx = (x_right - x_left) / n
                for idx, hijo in enumerate(node.hijos):
                    sub_left = x_left + idx * dx
                    sub_right = sub_left + dx
                    coords.update(get_coords(hijo, depth + 1, sub_left, sub_right))
            return coords

        coords = get_coords(nodo)

        def plot_tree(node):
            if not isinstance(node, Nodo):
                return

            x, y = coords[node]

            lbl = node.etiqueta
            if node.etiqueta in ['S', 'NP', 'VP', 'AP'] and any(k in node.rasgos for k in ['dim', 'sev']):
                dim = node.rasgos.get('dim', 'neutro')
                sev = node.rasgos.get('sev', 'neutro')
                if dim != 'neutro' or sev != 'neutro':
                    lbl += f"\n({dim}:{sev})"

            box_color = 'lightblue'
            if node.rasgos.get('dim') == 'crisis':
                box_color = '#ff9999'
            elif node.rasgos.get('sev') == 'alto':
                box_color = '#ffcc99'

            ax.text(x, y, lbl, ha='center', va='center', fontsize=9, weight='bold',
                    bbox=dict(boxstyle='round,pad=0.4', facecolor=box_color, alpha=0.9, edgecolor='gray'))

            if node.is_terminal():
                tx, ty = coords[node.hijos[0]]
                ax.plot([x, tx], [y - 0.2, ty + 0.2], 'k-', lw=1.0, color='gray')
                ax.text(tx, ty, f'"{node.hijos[0]}"', ha='center', va='center', fontsize=10,
                        bbox=dict(boxstyle='square,pad=0.3', facecolor='#e6ffe6', edgecolor='green'))
            else:
                for hijo in node.hijos:
                    hx, hy = coords[hijo]
                    ax.plot([x, hx], [y - 0.3, hy + 0.3], 'k-', lw=1.2)
                    plot_tree(hijo)

        plot_tree(nodo)
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(10.0 - len(coords) * 0.2, 10.5)

        plt.title("Arbol de Derivacion Sintactico-Clinico (DCG)", fontsize=13, weight='bold', pad=15)
        plt.tight_layout()
        plt.savefig(file_path, dpi=150)
        plt.close()
        return True


# =======================================================================
# PRUEBAS
# =======================================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PRUEBA DEL ÁRBOL DE DERIVACIÓN SINTÁCTICA")
    print("=" * 60)

    # ---------------------------------------------------------------
    # Ejemplo 1: "Paciente presenta fiebre severa"
    # ---------------------------------------------------------------

    det = Nodo("DET", ["Paciente"])

    nombre = Nodo(
        "NP",
        [det],
        rasgos={
            "dim": "neutro",
            "sev": "neutro"
        }
    )

    verbo = Nodo("V", ["presenta"])

    sustantivo = Nodo(
        "N",
        ["fiebre"],
        rasgos={
            "dim": "sintoma",
            "sev": "medio"
        }
    )

    adjetivo = Nodo(
        "ADJ",
        ["severa"],
        rasgos={
            "sev": "alto"
        }
    )

    ap = Nodo(
        "AP",
        [adjetivo],
        rasgos={
            "sev": "alto"
        }
    )

    objeto = Nodo(
        "NP",
        [sustantivo, ap],
        rasgos={
            "dim": "sintoma",
            "sev": "alto"
        }
    )

    vp = Nodo(
        "VP",
        [verbo, objeto],
        rasgos={
            "dim": "sintoma",
            "sev": "alto"
        }
    )

    raiz = Nodo(
        "S",
        [nombre, vp],
        rasgos={
            "dim": "sintoma",
            "sev": "alto"
        }
    )

    print("\nÁRBOL ASCII:\n")
    print(TreeVisualizer.print_ascii(raiz))

    archivo = "ejemplo_arbol.png"
    ok = TreeVisualizer.draw_matplotlib(raiz, archivo)

    if ok:
        print(f"✓ Imagen generada correctamente: {archivo}")
    else:
        print("✗ No fue posible generar la imagen.")

    # ---------------------------------------------------------------
    # Prueba de métodos auxiliares
    # ---------------------------------------------------------------

    print("\nPRUEBA DE MÉTODOS")
    print("-" * 40)

    print("Texto recuperado:")
    print(raiz.get_text())

    print("\nNodo raíz:")
    print(raiz)

    print("\n¿'DET' es terminal?:", det.is_terminal())
    print("¿'S' es terminal?:", raiz.is_terminal())

    # ---------------------------------------------------------------
    # Ejemplo 2: Caso de crisis
    # ---------------------------------------------------------------

    print("\n" + "=" * 60)
    print("SEGUNDO EJEMPLO (CRISIS)")
    print("=" * 60)

    sujeto2 = Nodo("NP", [Nodo("N", ["Paciente"])])

    verbo2 = Nodo("V", ["presenta"])

    crisis = Nodo(
        "N",
        ["shock"],
        rasgos={
            "dim": "crisis",
            "sev": "alto"
        }
    )

    objeto2 = Nodo(
        "NP",
        [crisis],
        rasgos={
            "dim": "crisis",
            "sev": "alto"
        }
    )

    vp2 = Nodo(
        "VP",
        [verbo2, objeto2],
        rasgos={
            "dim": "crisis",
            "sev": "alto"
        }
    )

    raiz2 = Nodo(
        "S",
        [sujeto2, vp2],
        rasgos={
            "dim": "crisis",
            "sev": "alto"
        }
    )

    print(TreeVisualizer.print_ascii(raiz2))

    TreeVisualizer.draw_matplotlib(
        raiz2,
        "ejemplo_crisis.png"
    )

    print("✓ Imagen ejemplo_crisis.png generada.")
    

# =======================================================================
# PRUEBAS PSICOLÓGICAS
# =======================================================================

if __name__ == "__main__":

    ejemplos = []

    # ---------------------------------------------------------------
    # Caso 1: "me siento un poco nervioso"
    # Severidad baja
    # ---------------------------------------------------------------

    arbol1 = Nodo(
        "S",
        [
            Nodo("PRON", ["me"]),
            Nodo(
                "VP",
                [
                    Nodo("V", ["siento"]),
                    Nodo(
                        "AP",
                        [
                            Nodo("INT", ["un poco"]),
                            Nodo("ADJ", ["nervioso"])
                        ],
                        rasgos={
                            "dim": "ansiedad",
                            "sev": "bajo"
                        }
                    )
                ],
                rasgos={
                    "dim": "ansiedad",
                    "sev": "bajo"
                }
            )
        ],
        rasgos={
            "dim": "ansiedad",
            "sev": "bajo"
        }
    )

    ejemplos.append(
        ("me siento un poco nervioso", arbol1, "bajo")
    )

    # ---------------------------------------------------------------
    # Caso 2: "estoy muy triste desde hace semanas"
    # Severidad media
    # ---------------------------------------------------------------

    arbol2 = Nodo(
        "S",
        [
            Nodo("V", ["estoy"]),
            Nodo(
                "AP",
                [
                    Nodo("INT", ["muy"]),
                    Nodo("ADJ", ["triste"])
                ]
            ),
            Nodo(
                "TEMP",
                ["desde hace semanas"]
            )
        ],
        rasgos={
            "dim": "depresion",
            "sev": "medio"
        }
    )

    ejemplos.append(
        ("estoy muy triste desde hace semanas",
         arbol2,
         "medio")
    )

    # ---------------------------------------------------------------
    # Caso 3: "tengo mucho miedo"
    # Severidad media
    # ---------------------------------------------------------------

    arbol3 = Nodo(
        "S",
        [
            Nodo("V", ["tengo"]),
            Nodo(
                "NP",
                [
                    Nodo("INT", ["mucho"]),
                    Nodo("N", ["miedo"])
                ]
            )
        ],
        rasgos={
            "dim": "ansiedad",
            "sev": "medio"
        }
    )

    ejemplos.append(
        ("tengo mucho miedo",
         arbol3,
         "medio")
    )

    # ---------------------------------------------------------------
    # Caso 4: "me siento extremadamente abrumado"
    # Severidad alta
    # ---------------------------------------------------------------

    arbol4 = Nodo(
        "S",
        [
            Nodo("PRON", ["me"]),
            Nodo(
                "VP",
                [
                    Nodo("V", ["siento"]),
                    Nodo(
                        "AP",
                        [
                            Nodo("INT", ["extremadamente"]),
                            Nodo("ADJ", ["abrumado"])
                        ]
                    )
                ]
            )
        ],
        rasgos={
            "dim": "ansiedad",
            "sev": "alto"
        }
    )

    ejemplos.append(
        ("me siento extremadamente abrumado",
         arbol4,
         "alto")
    )

    # ---------------------------------------------------------------
    # Caso 5: "quiero quitarme la vida"
    # CRÍTICO
    # ---------------------------------------------------------------

    arbol5 = Nodo(
        "S",
        [
            Nodo("V", ["quiero"]),
            Nodo(
                "VP",
                [
                    Nodo("V", ["quitarme"]),
                    Nodo(
                        "NP",
                        [
                            Nodo("DET", ["la"]),
                            Nodo("N", ["vida"])
                        ]
                    )
                ]
            )
        ],
        rasgos={
            "dim": "suicidio",
            "sev": "alto",
            "escala": "critico"
        }
    )

    ejemplos.append(
        ("quiero quitarme la vida",
         arbol5,
         "critico")
    )

    # ---------------------------------------------------------------
    # Ejecutar todas las pruebas
    # ---------------------------------------------------------------

    for i, (texto, arbol, nivel) in enumerate(ejemplos, start=1):

        print("\n" + "=" * 70)
        print(f"CASO {i}")
        print("=" * 70)

        print("Oración:")
        print(texto)

        print("\nTriage esperado:")
        print(nivel)

        print("\nÁrbol ASCII:\n")
        print(TreeVisualizer.print_ascii(arbol))

        nombre_archivo = f"caso_{i}_{nivel}.png"

        if TreeVisualizer.draw_matplotlib(arbol, nombre_archivo):
            print(f"Imagen generada: {nombre_archivo}")

        print("\nTexto reconstruido:")
        print(arbol.get_text())