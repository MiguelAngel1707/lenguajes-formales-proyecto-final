# main.py
# Programa principal de los Items 1 y 2 (entrada y salida de la sección 2.2
# del enunciado).
#
# Uso:   python main.py < entrada.txt
#        python main.py --sets < entrada.txt     (imprime también FIRST y FOLLOW)

import sys

from grammar import EPSILON, read_grammar, read_line
from first_follow import compute_first, compute_follow, print_sets
from ll1 import is_ll1, build_ll1_table, ll1_parse
from slr1 import augment, canonical_collection, build_slr_table, slr1_parse


def parse_strings(parser, grammar, ll1_table, productions, action, goto_table):
    """
    Lee cadenas, una por línea, hasta recibir una línea vacía, y para cada una
    imprime yes si la gramática la genera y no si no la genera.
    La línea "e" representa la cadena vacía.
    parser es "T" para usar el parser LL(1) o "B" para usar el SLR(1).
    """
    while True:
        line = read_line()
        if not line:                # línea vacía (o fin de la entrada)
            return

        string = line
        if line == EPSILON:
            string = ""

        if not grammar.only_terminals(string):
            accepted = False
        elif parser == "T":
            accepted, tree = ll1_parse(grammar, ll1_table, string)
        else:
            accepted = slr1_parse(productions, action, goto_table, string)

        if accepted:
            print("yes")
        else:
            print("no")


def main():
    grammar = read_grammar()

    # Item 1: FIRST y FOLLOW
    first = compute_first(grammar)
    follow = compute_follow(grammar, first)
    if "--sets" in sys.argv:
        print_sets(grammar, first, follow)

    # Item 2: LL(1)
    is_ll1_grammar = is_ll1(grammar, first, follow)
    ll1_table = build_ll1_table(grammar, first, follow)

    # Item 2: SLR(1)
    productions = augment(grammar)
    states, transitions = canonical_collection(grammar, productions)
    action, goto_table, is_slr1_grammar = build_slr_table(grammar, productions, states, transitions, follow)

    # Los cuatro casos de la sección 2.2.2
    if is_ll1_grammar and is_slr1_grammar:
        while True:
            print("Select a parser (T: for LL(1), B: for SLR(1), Q: quit):")
            letter = read_line()
            if letter is None or letter == "Q":
                return
            if letter == "T" or letter == "B":
                parse_strings(letter, grammar, ll1_table, productions, action, goto_table)
    elif is_ll1_grammar:
        print("Grammar is LL(1).")
        parse_strings("T", grammar, ll1_table, productions, action, goto_table)
    elif is_slr1_grammar:
        print("Grammar is SLR(1).")
        parse_strings("B", grammar, ll1_table, productions, action, goto_table)
    else:
        print("Grammar is neither LL(1) nor SLR(1).")


main()
