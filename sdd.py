# sdd.py
# Item 3: evaluación de un SDD sobre el árbol de derivación de una cadena,
# usando el grafo de dependencias (secciones 5.1 y 5.2 del libro).
#
#   collect_nodes      numera los nodos del árbol (para poder nombrar los atributos)
#   build_graph        sección 5.2.1: grafo de dependencias
#   topological_order  sección 5.2.2: orden topológico (o None si hay un ciclo)
#   evaluate           evalúa los atributos en ese orden
#   print_tree         imprime el árbol anotado
#
# Este archivo no sabe nada del SDD concreto: la gramática y las reglas
# están en sdd_rules.py. Para cambiar el SDD solo hay que cambiar ese archivo.
#
# Uso:  python sdd.py           lee cadenas, una por línea, hasta una línea vacía
#       python sdd.py --step    además muestra el grafo y evalúa un atributo
#                               cada vez que se presiona Enter (visualizador)

import sys

from grammar import EPSILON, build_grammar, read_line
from first_follow import compute_first, compute_follow
from ll1 import is_ll1, build_ll1_table, ll1_parse
from sdd_rules import GRAMMAR, RULES, MAIN_ATTRIBUTE


def collect_nodes(node, nodes):
    """Agrega a la lista 'nodes' todos los nodos del árbol, en preorden, y los numera desde 1."""
    nodes.append(node)
    node.number = len(nodes)
    for child in node.children:
        collect_nodes(child, nodes)


def attribute_at(node, position, name):
    """
    El vértice del grafo para el atributo (posición, nombre) de una regla
    aplicada en 'node': la posición 0 es el propio nodo (la cabeza de la
    producción) y la posición i es su i-ésimo hijo.
    """
    if position == 0:
        return (node, name)
    return (node.children[position - 1], name)


def build_graph(grammar, rules, nodes):
    """
    Sección 5.2.1. El grafo tiene un vértice por cada atributo de cada nodo
    del árbol; un vértice es la pareja (nodo, nombre del atributo).
    Para cada nodo interior se toman las reglas de la producción que se usó
    en ese nodo y, por cada regla, se agrega una arista desde cada atributo
    que la regla usa hacia el atributo que la regla define.
    Las hojas (los terminales) aportan su lexval, que es el propio carácter.

    Devuelve:
      vertices  la lista de vértices, en el orden en que se crearon
      edges     edges[v] = lista de los vértices w con una arista v -> w
      rule_of   rule_of[w] = (función, lista de vértices que usa) para calcular w
    """
    vertices = []
    edges = {}
    rule_of = {}

    for node in nodes:
        if node.production is None:
            # Hoja: el lexval ya se conoce. (Su vértice puede existir ya,
            # si lo creó una regla del padre que lo usa.)
            node.attrs["lexval"] = node.symbol
            vertex = (node, "lexval")
            if vertex not in edges:
                vertices.append(vertex)
                edges[vertex] = []
            continue

        for defines, uses, function in rules[grammar.production_text(node.production)]:
            target = attribute_at(node, defines[0], defines[1])
            sources = []
            for position, name in uses:
                sources.append(attribute_at(node, position, name))

            for vertex in [target] + sources:
                if vertex not in edges:
                    vertices.append(vertex)
                    edges[vertex] = []

            rule_of[target] = (function, sources)
            for source in sources:
                edges[source].append(target)

    return vertices, edges, rule_of


def topological_order(vertices, edges):
    """
    Sección 5.2.2. Un orden topológico es un orden de los vértices en el que,
    si hay una arista de M a N, M va antes que N. Se construye como lo
    explica el libro: se toma un vértice al que no le llega ninguna arista,
    se pone de siguiente en el orden, se quita del grafo y se repite.
    Para "quitarlo" se lleva la cuenta de cuántas aristas le llegan a cada
    vértice desde vértices que todavía no están en el orden.

    Si el grafo tiene un ciclo, en algún momento no hay ningún vértice sin
    aristas de entrada y quedan vértices sin ordenar: se devuelve None.
    """
    incoming = {}
    for vertex in vertices:
        incoming[vertex] = 0
    for vertex in vertices:
        for target in edges[vertex]:
            incoming[target] += 1

    ready = []                       # vértices a los que ya no les llega ninguna arista
    for vertex in vertices:
        if incoming[vertex] == 0:
            ready.append(vertex)

    order = []
    while len(ready) > 0:
        vertex = ready.pop(0)
        order.append(vertex)
        for target in edges[vertex]:
            incoming[target] -= 1
            if incoming[target] == 0:
                ready.append(target)

    if len(order) < len(vertices):
        return None
    return order


def vertex_name(vertex):
    """Nombre de un atributo para imprimirlo, por ejemplo R[7].acc (7 es el número del nodo)."""
    node, name = vertex
    return f"{node.symbol}[{node.number}].{name}"


def evaluate(order, rule_of, root, step):
    """
    Evalúa los atributos en el orden topológico. Los lexval de las hojas ya
    se conocen; cada uno de los demás se calcula con la función de su regla,
    a partir de los valores de los atributos que usa (que ya están calculados,
    porque van antes en el orden).
    Si step es True, espera un Enter antes de cada atributo y muestra el árbol.
    """
    for i in range(len(order)):
        node, name = order[i]
        if order[i] in rule_of:
            function, sources = rule_of[order[i]]
            values = []
            for source_node, source_name in sources:
                values.append(source_node.attrs[source_name])
            node.attrs[name] = function(*values)

        if step:
            read_line()
            print(f"Step {i + 1}: {vertex_name(order[i])} = {node.attrs[name]}")
            print_tree(root, 0)


def print_tree(node, depth):
    """Imprime el árbol anotado: un nodo por línea, con sangría según la profundidad."""
    values = []
    for name in node.attrs:
        values.append(f"{name}={node.attrs[name]}")
    print("    " * depth + f"{node.symbol}[{node.number}]  " + ", ".join(values))

    for child in node.children:
        print_tree(child, depth + 1)
    if node.production is not None and len(node.children) == 0:
        print("    " * (depth + 1) + EPSILON)         # producción vacía


def main():
    step = "--step" in sys.argv

    grammar = build_grammar(GRAMMAR)
    first = compute_first(grammar)
    follow = compute_follow(grammar, first)
    if not is_ll1(grammar, first, follow):
        print("The grammar of the SDD is not LL(1).")
        return
    table = build_ll1_table(grammar, first, follow)

    while True:
        line = read_line()
        if not line:                    # línea vacía (o fin de la entrada)
            return
        string = line
        if line == EPSILON:
            string = ""

        # 1. Árbol de derivación, con el parser LL(1) del Item 2
        accepted = False
        if grammar.only_terminals(string):
            accepted, root = ll1_parse(grammar, table, string)
        if not accepted:
            print("no")
            continue

        # 2. Grafo de dependencias y orden topológico
        nodes = []
        collect_nodes(root, nodes)
        vertices, edges, rule_of = build_graph(grammar, RULES, nodes)
        order = topological_order(vertices, edges)
        if order is None:
            print("Error: the SDD is circular (the dependency graph has a cycle).")
            return

        if step:
            print("Dependency graph edges:")
            for vertex in vertices:
                for target in edges[vertex]:
                    print(f"    {vertex_name(vertex)} -> {vertex_name(target)}")
            print("Press Enter to evaluate each attribute.")

        # 3. Evaluación en orden topológico
        evaluate(order, rule_of, root, step)

        # 4. Salida
        print("Annotated parse tree:")
        print_tree(root, 0)
        print("Evaluation order:")
        for i in range(len(order)):
            print(f"    {i + 1}. {vertex_name(order[i])}")
        print(f"{root.symbol}.{MAIN_ATTRIBUTE} = {root.attrs[MAIN_ATTRIBUTE]}")
        print()


main()
