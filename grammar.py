# grammar.py
# Lectura y representación de una gramática libre de contexto.
#
# Convenciones del enunciado (sección 2.2):
#   - Los no terminales son letras mayúsculas y 'S' es el símbolo inicial.
#   - Los terminales son caracteres que NO son letras mayúsculas.
#   - La letra 'e' representa la cadena vacía (ε).
#   - El símbolo '$' marca el final de la cadena de entrada.
#
# Formato de entrada:
#   3
#   S -> AB
#   A -> aA d
#   B -> bBc e

EPSILON = 'e'
END = '$'
START = 'S'


class Grammar:
    def __init__(self):
        self.nonterminals = []   # en el orden en que aparecen en la entrada
        self.terminals = []      # ordenados en ASCII
        self.productions = []    # lista de parejas (cabeza, cuerpo)
        self.start = START

        # Cada producción es una pareja (cabeza, cuerpo), donde el cuerpo es
        # una lista de símbolos. Por ejemplo:
        #   B -> bBc   se guarda como   ('B', ['b', 'B', 'c'])
        #   B -> e     se guarda como   ('B', [])      (cuerpo vacío = ε)
        # El número de una producción es su posición en la lista.

    def is_nonterminal(self, symbol):
        return symbol in self.nonterminals

    def is_terminal(self, symbol):
        return symbol in self.terminals

    def productions_of(self, nonterminal):
        """Devuelve los números de las producciones cuya cabeza es 'nonterminal'."""
        numbers = []
        for number in range(len(self.productions)):
            head, body = self.productions[number]
            if head == nonterminal:
                numbers.append(number)
        return numbers

    def production_text(self, number):
        """Devuelve una producción como texto, por ejemplo 'B -> bBc' o 'B -> e'."""
        head, body = self.productions[number]
        if len(body) == 0:
            return head + " -> " + EPSILON
        return head + " -> " + "".join(body)

    def only_terminals(self, string):
        """
        Devuelve True si todos los caracteres de la cadena son terminales de
        la gramática. Si no lo son, la cadena no puede ser generada por la
        gramática (por ejemplo, si trae una mayúscula o el símbolo '$').
        """
        for symbol in string:
            if not self.is_terminal(symbol):
                return False
        return True


class Node:
    """
    Nodo del árbol de derivación (parse tree). Guarda:
      symbol      el símbolo de la gramática del nodo
      production  el número de la producción usada (None si es una hoja)
      children    la lista de hijos, de izquierda a derecha
      attrs       los valores de los atributos, por ejemplo {'val': 5}
      number      un número para identificar el nodo al imprimirlo (lo pone el SDD)
    """

    def __init__(self, symbol):
        self.symbol = symbol
        self.production = None
        self.children = []
        self.attrs = {}
        self.number = None


def read_line():
    """
    Lee una línea de la entrada estándar y le quita los espacios y saltos
    de línea de los extremos (incluido el '\\r' de los archivos de Windows).
    Si la entrada se acabó, devuelve None.
    """
    try:
        line = input()
    except EOFError:
        return None
    return line.strip()


def build_grammar(lines):
    """
    Construye la gramática a partir de una lista con las líneas de las
    producciones, por ejemplo ["S -> AB", "A -> aA d", "B -> bBc e"].
    """
    grammar = Grammar()

    for line in lines:
        parts = line.split()        # "B -> bBc e"  ->  ['B', '->', 'bBc', 'e']
        head = parts[0]
        alternatives = parts[2:]    # parts[1] es la flecha '->'
        grammar.nonterminals.append(head)

        for alternative in alternatives:
            if alternative == EPSILON:
                body = []
            else:
                body = list(alternative)    # "bBc"  ->  ['b', 'B', 'c']
            grammar.productions.append((head, body))

    # Los terminales son los símbolos de los cuerpos que no son mayúsculas
    for head, body in grammar.productions:
        for symbol in body:
            if not symbol.isupper() and symbol not in grammar.terminals:
                grammar.terminals.append(symbol)
    grammar.terminals.sort()

    return grammar


def read_grammar():
    """Lee el número n y luego las n líneas de producciones de la entrada estándar."""
    n = int(read_line())
    lines = []
    for i in range(n):
        lines.append(read_line())
    return build_grammar(lines)


# Prueba rápida:  python grammar.py
# Lee una gramática y muestra sus producciones numeradas.
if __name__ == "__main__":
    grammar = read_grammar()
    print("No terminales:", grammar.nonterminals)
    print("Terminales:", grammar.terminals)
    for number in range(len(grammar.productions)):
        print(number, ":", grammar.production_text(number))
