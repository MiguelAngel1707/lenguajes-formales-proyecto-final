# ll1.py
# Item 2: parser LL(1) (secciones 4.4.3 y 4.4.4 del libro).
#
#   is_ll1           condición para que una gramática sea LL(1) (inicio de la sección 4.4.3)
#   build_ll1_table  Algoritmo 4.31: construcción de la tabla de análisis predictivo M
#   ll1_parse        Algoritmo 4.34: análisis predictivo dirigido por tabla (no recursivo)
#
# La gramática NO se transforma antes de revisar si es LL(1): si tiene
# recursión por la izquierda, simplemente no cumple la condición.

from grammar import EPSILON, END, Node, read_grammar, read_line
from first_follow import compute_first, compute_follow, first_of_string


def is_ll1(grammar, first, follow):
    """
    Condición de la sección 4.4.3. La gramática es LL(1) si y solo si para
    cada par de producciones distintas A -> α | β se cumple que:
      1. α y β no derivan cadenas que empiecen con el mismo terminal a.
      2. A lo sumo una de las dos deriva la cadena vacía.
      3. Si β =>* ε, entonces α no deriva ninguna cadena que empiece con un
         terminal de FOLLOW(A). Y lo mismo cambiando α por β.
    Las condiciones 1 y 2 juntas equivalen a que FIRST(α) y FIRST(β) no
    tengan ningún elemento en común (contando ε como un elemento más).
    """
    for nonterminal in grammar.nonterminals:
        numbers = grammar.productions_of(nonterminal)

        for i in range(len(numbers)):
            for j in range(i + 1, len(numbers)):
                alpha = grammar.productions[numbers[i]][1]
                beta = grammar.productions[numbers[j]][1]
                first_alpha = first_of_string(alpha, first)
                first_beta = first_of_string(beta, first)

                # Condiciones 1 y 2
                if len(first_alpha & first_beta) > 0:
                    return False

                # Condición 3
                if EPSILON in first_beta and len(first_alpha & follow[nonterminal]) > 0:
                    return False
                if EPSILON in first_alpha and len(first_beta & follow[nonterminal]) > 0:
                    return False

    return True


def build_ll1_table(grammar, first, follow):
    """
    Algoritmo 4.31. Para cada producción A -> α:
      1. Para cada terminal a de FIRST(α), se agrega A -> α a M[A, a].
      2. Si ε está en FIRST(α), para cada terminal b de FOLLOW(A) se agrega
         A -> α a M[A, b] (b también puede ser $).
    La tabla es un diccionario: table[(A, a)] = número de la producción.
    Las casillas que no están en el diccionario son errores.
    Si la gramática es LL(1), a ninguna casilla le llegan dos producciones.
    """
    table = {}

    for number in range(len(grammar.productions)):
        head, body = grammar.productions[number]
        first_body = first_of_string(body, first)

        # Regla 1
        for terminal in first_body:
            if terminal != EPSILON:
                table[(head, terminal)] = number

        # Regla 2
        if EPSILON in first_body:
            for terminal in follow[head]:
                table[(head, terminal)] = number

    return table


def ll1_parse(grammar, table, string, show_steps=False):
    """
    Algoritmo 4.34 (figura 4.20): análisis predictivo no recursivo.

    La pila empieza con $ en el fondo y S encima, y a la entrada se le
    agrega $ al final. En cada paso, con X en el tope de la pila y a como
    símbolo actual de la entrada:
      - si X = a, se saca X de la pila y se avanza en la entrada;
      - si X es un terminal distinto de a, o M[X, a] está vacía, hay error;
      - si M[X, a] = X -> Y1 Y2 ... Yk, se saca X y se meten Yk, ..., Y2, Y1
        (Y1 queda en el tope).
    Se termina cuando en el tope queda $.

    La pila no guarda solo símbolos sino nodos del árbol de derivación. El
    libro dice que en el paso de la producción "se puede ejecutar código
    adicional, por ejemplo, para construir un nodo del árbol": al reemplazar
    X por Y1 Y2 ... Yk, los nodos de los Yi se cuelgan como hijos del nodo
    de X. Al final, 'root' es el árbol de toda la cadena (se usa en el Item 3).

    Devuelve (True, raíz del árbol) si la cadena es aceptada y (False, None) si no.
    Si show_steps es True, imprime los pasos como en la figura 4.21: cada fila
    muestra la configuración que queda DESPUÉS de la acción de esa fila.
    """
    w = string + END
    position = 0                     # el símbolo actual de la entrada es w[position]
    root = Node(grammar.start)
    stack = [Node(END), root]        # el tope de la pila es el último elemento

    if show_steps:
        print(f"{'MATCHED':<20}{'STACK':<20}{'INPUT':<20}ACTION")
        print(configuration(w, position, stack))

    while stack[-1].symbol != END:
        node = stack[-1]
        X = node.symbol
        a = w[position]

        if X == a:
            # El terminal del tope coincide con el de la entrada
            stack.pop()
            position += 1
            action = "match " + a
        elif grammar.is_terminal(X) or (X, a) not in table:
            # Terminal que no coincide, o casilla vacía de la tabla: error
            if show_steps:
                print(f"{'':<60}error")
            return False, None
        else:
            # Se reemplaza X por el cuerpo de la producción M[X, a]
            number = table[(X, a)]
            node.production = number
            stack.pop()
            for symbol in grammar.productions[number][1]:
                node.children.append(Node(symbol))
            for child in reversed(node.children):
                stack.append(child)
            action = "output " + grammar.production_text(number)

        if show_steps:
            print(configuration(w, position, stack) + action)

    # En la pila solo queda $. La cadena se acepta si también se acabó la
    # entrada (por ejemplo, con S -> a y la cadena "aa" la pila se vacía
    # cuando todavía falta una a por leer).
    if w[position] != END:
        if show_steps:
            print(f"{'':<60}error")
        return False, None
    return True, root


def configuration(w, position, stack):
    """
    Texto de una fila de la figura 4.21: lo ya reconocido (MATCHED), la pila
    (con el tope a la izquierda, como en el libro) y lo que falta de la entrada.
    """
    stack_text = ""
    for node in reversed(stack):
        stack_text += node.symbol
    return f"{w[:position]:<20}{stack_text:<20}{w[position:]:<20}"


# Prueba rápida:  python ll1.py < gramatica.txt
# Lee una gramática y, en la línea siguiente, una cadena. Dice si la gramática
# es LL(1), imprime la tabla M y analiza la cadena paso a paso.
if __name__ == "__main__":
    grammar = read_grammar()
    first = compute_first(grammar)
    follow = compute_follow(grammar, first)

    if not is_ll1(grammar, first, follow):
        print("The grammar is not LL(1).")
    else:
        table = build_ll1_table(grammar, first, follow)

        # Tabla M: una fila por no terminal y una columna por terminal (y $)
        columns = grammar.terminals + [END]
        header = f"{'':<6}"
        for terminal in columns:
            header += f"{terminal:<12}"
        print(header)
        for nonterminal in sorted(grammar.nonterminals):
            row = f"{nonterminal:<6}"
            for terminal in columns:
                if (nonterminal, terminal) in table:
                    row += f"{grammar.production_text(table[(nonterminal, terminal)]):<12}"
                else:
                    row += f"{'':<12}"
            print(row)

        line = read_line()
        if line:
            print()
            string = line
            if line == EPSILON:
                string = ""
            accepted, root = ll1_parse(grammar, table, string, show_steps=True)
            if accepted:
                print("yes")
            else:
                print("no")
