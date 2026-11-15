# slr1.py
# Item 2: parser SLR(1) (secciones 4.5 y 4.6 del libro).
#
#   augment               sección 4.6.2: gramática aumentada, con S' -> S
#   closure               figura 4.32: CLOSURE(I)
#   goto                  sección 4.6.2: GOTO(I, X)
#   canonical_collection  figura 4.33: colección canónica de conjuntos de ítems LR(0)
#   build_slr_table       Algoritmo 4.46: tablas ACTION y GOTO del SLR
#   slr1_parse            Algoritmo 4.44 (figura 4.36): algoritmo de análisis LR
#
# Un ítem LR(0), por ejemplo A -> X.YZ, se guarda como la pareja
# (número de producción, posición del punto); en el ejemplo, el punto está
# en la posición 1. Un conjunto de ítems es un set de Python con esas parejas.

from grammar import EPSILON, END, read_grammar, read_line
from first_follow import compute_first, compute_follow

AUGMENTED_START = "S'"


def augment(grammar):
    """
    Sección 4.6.2: la gramática aumentada G' tiene un símbolo inicial nuevo
    S' y la producción S' -> S. Como en el libro, S' -> S es la producción 0
    y las de la gramática quedan numeradas desde 1 (figura 4.37).
    Devuelve la lista de producciones (cabeza, cuerpo) de G'.
    """
    return [(AUGMENTED_START, [grammar.start])] + grammar.productions


def closure(items, productions, grammar):
    """
    Figura 4.32. Si A -> α.Bβ está en el conjunto y B -> γ es una producción,
    se agrega B -> .γ. Se repite hasta que en una vuelta no se agregue nada.
    """
    result = set(items)
    changed = True
    while changed:
        changed = False
        for number, dot in list(result):
            body = productions[number][1]
            if dot < len(body) and grammar.is_nonterminal(body[dot]):
                B = body[dot]
                for k in range(len(productions)):
                    if productions[k][0] == B and (k, 0) not in result:
                        result.add((k, 0))
                        changed = True
    return result


def goto(items, X, productions, grammar):
    """
    Sección 4.6.2. GOTO(I, X) es la clausura del conjunto de ítems A -> αX.β
    tales que A -> α.Xβ está en I (se pasa el punto por encima de X).
    """
    moved = set()
    for number, dot in items:
        body = productions[number][1]
        if dot < len(body) and body[dot] == X:
            moved.add((number, dot + 1))
    return closure(moved, productions, grammar)


def canonical_collection(grammar, productions):
    """
    Figura 4.33. Se empieza con C = { CLOSURE({S' -> .S}) } y, para cada
    conjunto I de C y cada símbolo X, se agrega GOTO(I, X) a C si no es
    vacío y no está ya en C.

    Los conjuntos se guardan en la lista 'states' (el estado i es states[i]).
    Recorrer la lista mientras crece es lo mismo que el "repeat ... until no
    new sets" del libro: cada conjunto se revisa una vez, también los nuevos.
    Solo se prueban los símbolos X que aparecen después de un punto (con
    los demás GOTO es vacío), en el orden de los ítems. Así los estados
    quedan numerados como en la figura 4.31 del libro.

    Devuelve states y transitions, donde transitions[(i, X)] = j significa
    GOTO(Ii, X) = Ij.
    """
    states = [closure({(0, 0)}, productions, grammar)]
    transitions = {}

    i = 0
    while i < len(states):
        symbols = []
        for number, dot in sorted(states[i]):
            body = productions[number][1]
            if dot < len(body) and body[dot] not in symbols:
                symbols.append(body[dot])

        for X in symbols:
            J = goto(states[i], X, productions, grammar)
            if J not in states:
                states.append(J)
            transitions[(i, X)] = states.index(J)
        i += 1

    return states, transitions


def build_slr_table(grammar, productions, states, transitions, follow):
    """
    Algoritmo 4.46. Para cada estado i:
      (a) Si A -> α.aβ está en Ii (a terminal) y GOTO(Ii, a) = Ij,
          ACTION[i, a] = shift j.
      (b) Si A -> α. está en Ii (A distinto de S'),
          ACTION[i, a] = reduce A -> α para todo a en FOLLOW(A).
      (c) Si S' -> S. está en Ii, ACTION[i, $] = accept.
      GOTO[i, A] = j si GOTO(Ii, A) = Ij, para cada no terminal A.
    Las casillas que no se llenan son errores.

    Si alguna casilla de ACTION recibe dos acciones distintas, hay un
    conflicto (sección 4.5.4) y la gramática no es SLR(1).

    Las acciones se guardan como ("shift", j), ("reduce", número de
    producción) o ("accept",).
    Devuelve (action, goto_table, is_slr).
    """
    action = {}
    goto_table = {}
    is_slr = True

    for i in range(len(states)):
        for number, dot in states[i]:
            head, body = productions[number]

            new_actions = []        # parejas (terminal, acción) que pide este ítem
            if dot < len(body):
                if grammar.is_terminal(body[dot]):                  # regla (a)
                    a = body[dot]
                    new_actions.append((a, ("shift", transitions[(i, a)])))
            elif number == 0:                                       # regla (c)
                new_actions.append((END, ("accept",)))
            else:                                                   # regla (b)
                for a in follow[head]:
                    new_actions.append((a, ("reduce", number)))

            for a, new_action in new_actions:
                if (i, a) in action and action[(i, a)] != new_action:
                    is_slr = False                                  # conflicto
                action[(i, a)] = new_action

        for A in grammar.nonterminals:
            if (i, A) in transitions:
                goto_table[(i, A)] = transitions[(i, A)]

    return action, goto_table, is_slr


def slr1_parse(productions, action, goto_table, string, show_steps=False):
    """
    Algoritmo 4.44 (figura 4.36). La pila empieza con el estado 0 y a la
    entrada se le agrega $. Con s en el tope de la pila y a como símbolo
    actual de la entrada:
      - ACTION[s, a] = shift t: se mete t en la pila y se avanza en la entrada;
      - ACTION[s, a] = reduce A -> β: se sacan |β| estados, queda t en el tope
        y se mete GOTO[t, A];
      - ACTION[s, a] = accept: la cadena es aceptada;
      - casilla vacía: error.
    Devuelve True si la cadena es aceptada y False si no.

    La lista 'symbols' guarda los símbolos que corresponden a los estados de
    la pila; solo se usa para mostrar los pasos como en la figura 4.38.
    """
    w = string + END
    position = 0                    # el símbolo actual de la entrada es w[position]
    stack = [0]
    symbols = []

    if show_steps:
        print(f"{'STACK':<25}{'SYMBOLS':<20}{'INPUT':<20}ACTION")

    while True:
        s = stack[-1]
        a = w[position]
        current = action.get((s, a))        # None si la casilla está vacía

        if show_steps:
            stack_text = " ".join(str(state) for state in stack)
            row = f"{stack_text:<25}{''.join(symbols):<20}{w[position:]:<20}"
            if current is None:
                print(row + "error")
            elif current[0] == "shift":
                print(row + "shift " + str(current[1]))
            elif current[0] == "reduce":
                head, body = productions[current[1]]
                body_text = "".join(body)
                if body_text == "":
                    body_text = EPSILON
                print(row + "reduce by " + head + " -> " + body_text)
            else:
                print(row + "accept")

        if current is None:
            return False

        if current[0] == "shift":
            stack.append(current[1])
            symbols.append(a)
            position += 1
        elif current[0] == "reduce":
            head, body = productions[current[1]]
            for k in range(len(body)):
                stack.pop()
                symbols.pop()
            t = stack[-1]
            stack.append(goto_table[(t, head)])
            symbols.append(head)
        else:
            return True


def item_text(productions, item):
    """Un ítem como texto, por ejemplo  E -> E.+T  (solo para imprimir)."""
    number, dot = item
    head, body = productions[number]
    return head + " -> " + "".join(body[:dot]) + "." + "".join(body[dot:])


# Prueba rápida:  python slr1.py < gramatica.txt
# Lee una gramática y, en la línea siguiente, una cadena. Imprime los
# conjuntos de ítems LR(0), las transiciones, la tabla SLR y analiza la
# cadena paso a paso.
if __name__ == "__main__":
    grammar = read_grammar()
    first = compute_first(grammar)
    follow = compute_follow(grammar, first)
    productions = augment(grammar)
    states, transitions = canonical_collection(grammar, productions)

    for i in range(len(states)):
        print(f"I{i}:")
        for item in sorted(states[i]):
            print("    " + item_text(productions, item))
    print()
    for (i, X), j in transitions.items():
        print(f"GOTO(I{i}, {X}) = I{j}")
    print()

    action, goto_table, is_slr = build_slr_table(grammar, productions, states, transitions, follow)
    if not is_slr:
        print("The grammar is not SLR(1) (the table has conflicts).")
    else:
        # Tabla como la figura 4.37: si = shift i, rj = reduce por la producción j
        for number in range(1, len(productions)):
            print(f"({number}) {grammar.production_text(number - 1)}")
        print()
        terminals = grammar.terminals + [END]
        nonterminals = sorted(grammar.nonterminals)
        header = f"{'STATE':<7}"
        for symbol in terminals + nonterminals:
            header += f"{symbol:<6}"
        print(header)
        for i in range(len(states)):
            row = f"{i:<7}"
            for a in terminals:
                cell = ""
                if (i, a) in action:
                    if action[(i, a)][0] == "shift":
                        cell = "s" + str(action[(i, a)][1])
                    elif action[(i, a)][0] == "reduce":
                        cell = "r" + str(action[(i, a)][1])
                    else:
                        cell = "acc"
                row += f"{cell:<6}"
            for A in nonterminals:
                cell = ""
                if (i, A) in goto_table:
                    cell = str(goto_table[(i, A)])
                row += f"{cell:<6}"
            print(row)

        line = read_line()
        if line:
            print()
            string = line
            if line == EPSILON:
                string = ""
            if slr1_parse(productions, action, goto_table, string, show_steps=True):
                print("yes")
            else:
                print("no")
