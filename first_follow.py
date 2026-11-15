# first_follow.py
# Item 1: cálculo de los conjuntos FIRST y FOLLOW (sección 4.4.2 del libro).
#
# Los conjuntos se guardan en diccionarios:
#   first[X]  = conjunto de terminales con que empiezan las cadenas derivadas de X
#               (incluye 'e' si X puede derivar la cadena vacía)
#   follow[A] = conjunto de terminales que pueden aparecer justo a la derecha de A
#               (incluye '$' si A puede quedar al final)
#
# Ambos se calculan aplicando las reglas del libro una y otra vez hasta que
# ningún conjunto cambie. No se usa recursión porque con gramáticas recursivas
# por la izquierda (como S -> SS a) una función recursiva nunca terminaría.

from grammar import EPSILON, END, read_grammar


def first_of_string(symbols, first):
    """
    Calcula FIRST(X1 X2 ... Xn) para una lista de símbolos.

    Se agrega lo de FIRST(X1) sin ε; si X1 puede derivar ε, también lo de
    FIRST(X2) sin ε, y así sucesivamente. Si todos los Xi pueden derivar ε
    (o la lista está vacía), se agrega ε al resultado.
    """
    result = set()

    for symbol in symbols:
        for terminal in first[symbol]:
            if terminal != EPSILON:
                result.add(terminal)

        # Si este símbolo no puede derivar ε, los siguientes no aportan nada
        if EPSILON not in first[symbol]:
            return result

    # Todos los símbolos pueden derivar ε (o la lista estaba vacía)
    result.add(EPSILON)
    return result


def compute_first(grammar):
    """Devuelve el diccionario FIRST para todos los símbolos de la gramática."""
    first = {}

    # Regla 1: si X es terminal, FIRST(X) = {X}
    for terminal in grammar.terminals:
        first[terminal] = {terminal}

    # Los no terminales empiezan con el conjunto vacío
    for nonterminal in grammar.nonterminals:
        first[nonterminal] = set()

    # Reglas 2 y 3: para cada producción X -> Y1 Y2 ... Yk se agrega
    # FIRST(Y1 Y2 ... Yk) a FIRST(X). La regla 3 (X -> ε) queda incluida,
    # porque first_of_string([]) devuelve {'e'}.
    changed = True
    while changed:
        changed = False
        for head, body in grammar.productions:
            size_before = len(first[head])
            first[head] = first[head] | first_of_string(body, first)
            if len(first[head]) > size_before:
                changed = True

    return first


def compute_follow(grammar, first):
    """Devuelve el diccionario FOLLOW para todos los no terminales."""
    follow = {}
    for nonterminal in grammar.nonterminals:
        follow[nonterminal] = set()

    # Regla 1: '$' está en FOLLOW(S)
    follow[grammar.start].add(END)

    changed = True
    while changed:
        changed = False
        for head, body in grammar.productions:
            for i in range(len(body)):
                symbol = body[i]

                if grammar.is_nonterminal(symbol):
                    size_before = len(follow[symbol])

                    # beta es lo que sigue a 'symbol' en el cuerpo
                    beta = body[i + 1:]
                    first_beta = first_of_string(beta, first)

                    # Regla 2: A -> α B β  =>  FIRST(β) sin ε está en FOLLOW(B)
                    for terminal in first_beta:
                        if terminal != EPSILON:
                            follow[symbol].add(terminal)

                    # Regla 3: si β puede derivar ε (o B está al final),
                    # todo FOLLOW(A) está en FOLLOW(B)
                    if EPSILON in first_beta:
                        for terminal in follow[head]:
                            follow[symbol].add(terminal)

                    if len(follow[symbol]) > size_before:
                        changed = True

    return follow


def format_set(symbols):
    """
    Convierte un conjunto en texto con el formato del enunciado: primero los
    terminales en orden ASCII, luego 'e' (si está) y por último '$' (si está).
    Ejemplo: {'$', 'b', 'e'}  ->  '{b, e, $}'

    'e' y '$' se agregan aparte porque, si se ordenaran junto con los
    terminales, '$' (ASCII 36) quedaría antes que símbolos como '(' (ASCII 40).
    """
    ordered = []
    for symbol in symbols:
        if symbol != EPSILON and symbol != END:
            ordered.append(symbol)
    ordered.sort()

    if EPSILON in symbols:
        ordered.append(EPSILON)
    if END in symbols:
        ordered.append(END)

    return "{" + ", ".join(ordered) + "}"


def print_sets(grammar, first, follow):
    """Imprime todos los First y después todos los Follow, en orden alfabético."""
    names = sorted(grammar.nonterminals)
    for nonterminal in names:
        print(f"First({nonterminal}) = {format_set(first[nonterminal])}")
    for nonterminal in names:
        print(f"Follow({nonterminal}) = {format_set(follow[nonterminal])}")


# Prueba rápida:  python first_follow.py
# Lee una gramática y muestra sus conjuntos FIRST y FOLLOW.
if __name__ == "__main__":
    grammar = read_grammar()
    first = compute_first(grammar)
    follow = compute_follow(grammar, first)
    print_sets(grammar, first, follow)
