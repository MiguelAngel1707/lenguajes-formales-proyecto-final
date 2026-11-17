# tree.py
# Dibuja el árbol de derivación de una cadena con Graphviz.
#
# No cambia nada del resto del proyecto: usa el parser LL(1) de ll1.py, que
# ya construye el árbol con nodos de la clase Node (grammar.py). Este archivo
# solo recorre ese árbol y lo escribe en el lenguaje DOT de Graphviz, donde
# cada línea  "n1" -> "n2"  es una arista del padre n1 al hijo n2.
#
# Uso:  python tree.py CADENA < gramatica.txt
#       (la línea "e" como CADENA es la cadena vacía)
# Escribe el archivo tree.dot. La imagen se genera con:
#       dot -Tpng tree.dot -o tree.png
#
# Como el árbol lo construye el parser LL(1), la gramática debe ser LL(1).

import sys

from grammar import EPSILON, read_grammar
from first_follow import compute_first, compute_follow
from ll1 import is_ll1, build_ll1_table, ll1_parse


def number_nodes(node, nodes):
    """Agrega a 'nodes' todos los nodos del árbol, en preorden, y los numera desde 1."""
    nodes.append(node)
    node.number = len(nodes)
    for child in node.children:
        number_nodes(child, nodes)


def label(symbol):
    """El símbolo como texto para DOT: las comillas y la barra \\ se escapan."""
    return symbol.replace("\\", "\\\\").replace('"', '\\"')


def write_dot(root, file_name):
    """
    Escribe el árbol en formato DOT. Cada nodo se llama n1, n2, ... (su
    número) y muestra su símbolo. Por cada hijo se escribe una arista desde
    el padre. Si en un nodo se usó una producción vacía, se le cuelga una
    hoja con ε, como en los árboles del libro.
    """
    nodes = []
    number_nodes(root, nodes)

    lines = ["digraph tree {"]
    for node in nodes:
        lines.append(f'    n{node.number} [label="{label(node.symbol)}"];')
        for child in node.children:
            lines.append(f"    n{node.number} -> n{child.number};")
        if node.production is not None and len(node.children) == 0:
            lines.append(f'    e{node.number} [label="ε"];')
            lines.append(f"    n{node.number} -> e{node.number};")
    lines.append("}")

    with open(file_name, "w", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python tree.py STRING < grammar.txt")
        return
    string = sys.argv[1]
    if string == EPSILON:
        string = ""

    grammar = read_grammar()
    first = compute_first(grammar)
    follow = compute_follow(grammar, first)
    if not is_ll1(grammar, first, follow):
        print("The grammar is not LL(1).")
        return
    table = build_ll1_table(grammar, first, follow)

    accepted = False
    if grammar.only_terminals(string):
        accepted, root = ll1_parse(grammar, table, string)
    if not accepted:
        print("no")
        return

    write_dot(root, "tree.dot")
    print("yes")
    print("Tree written to tree.dot. To draw it:  dot -Tpng tree.dot -o tree.png")


main()
