# sdd_rules.py
# Item 3: la gramática y el SDD (definición dirigida por la sintaxis),
# guardados como DATOS. El evaluador (sdd.py) no sabe nada de este SDD:
# para cambiar el SDD solo hay que cambiar este archivo.
#
# Lenguaje: números escritos con un prefijo que indica su base:
#   b = binario (base 2), o = octal (base 8), d = decimal (base 10).
# Ejemplos: b101 vale 5, o17 vale 15, d2026 vale 2026.
# Si un dígito no es válido en la base (por ejemplo, el 2 en b102),
# el valor es "error".
#
# Atributos:
#   S.val   sintetizado  valor del número (entero o "error")
#   B.base  sintetizado  la base que indica el prefijo (2, 8 o 10)
#   N.base  heredado     la base en que se leen los dígitos
#   N.val   sintetizado  valor de los dígitos
#   R.base  heredado     la base en que se leen los dígitos
#   R.acc   heredado     valor de los dígitos que están a la izquierda de R
#   R.val   sintetizado  valor de todos los dígitos
#   D.val   sintetizado  valor de un dígito
#   lexval  sintetizado  (de los terminales) el propio carácter
#
# Cómo se escribe una regla: (atributo que define, atributos que usa, función).
# Un atributo se escribe (posición, nombre): la posición 0 es la cabeza de la
# producción y 1, 2, ... son los símbolos del cuerpo, de izquierda a derecha.
# Por ejemplo, en R -> DR:  (0, "acc") es R.acc,  (1, "val") es D.val  y
# (2, "acc") es R1.acc (la R del cuerpo).
# La función recibe los valores de los atributos que usa, en el mismo orden.

# La gramática, en el formato de la sección 2.2 del enunciado
GRAMMAR = [
    "S -> BN",
    "B -> b o d",
    "N -> DR",
    "R -> DR e",
    "D -> 0 1 2 3 4 5 6 7 8 9",
]

# El atributo principal del símbolo inicial: S.val
MAIN_ATTRIBUTE = "val"

ERROR = "error"


# Funciones semánticas

def copy(value):
    return value


def base_of(letter):
    bases = {"b": 2, "o": 8, "d": 10}
    return bases[letter]


def digit_value(char):
    return int(char)


def accumulate(acc, digit, base):
    """Agrega un dígito a la derecha del valor acumulado: acc * base + digit."""
    if acc == ERROR or digit >= base:
        return ERROR
    return acc * base + digit


def first_digit(digit, base):
    """El valor acumulado después del primer dígito (es como acumular sobre 0)."""
    return accumulate(0, digit, base)


# Reglas semánticas de cada producción (como la tabla de la figura 5.1)
RULES = {
    "S -> BN": [
        ((2, "base"), [(1, "base")], copy),                          # N.base = B.base
        ((0, "val"), [(2, "val")], copy),                            # S.val = N.val
    ],
    "B -> b": [
        ((0, "base"), [(1, "lexval")], base_of),                     # B.base = base_of(b.lexval)
    ],
    "B -> o": [
        ((0, "base"), [(1, "lexval")], base_of),                     # B.base = base_of(o.lexval)
    ],
    "B -> d": [
        ((0, "base"), [(1, "lexval")], base_of),                     # B.base = base_of(d.lexval)
    ],
    "N -> DR": [
        ((2, "base"), [(0, "base")], copy),                          # R.base = N.base
        ((2, "acc"), [(1, "val"), (0, "base")], first_digit),        # R.acc = first_digit(D.val, N.base)
        # Paso 6 (SDD circular): para probar que el evaluador detecta los
        # ciclos, cambie temporalmente la regla anterior por esta:
        # ((2, "acc"), [(2, "val")], copy),                          # R.acc = R.val
        ((0, "val"), [(2, "val")], copy),                            # N.val = R.val
    ],
    "R -> DR": [
        ((2, "base"), [(0, "base")], copy),                          # R1.base = R.base
        ((2, "acc"), [(0, "acc"), (1, "val"), (0, "base")], accumulate),  # R1.acc = accumulate(R.acc, D.val, R.base)
        ((0, "val"), [(2, "val")], copy),                            # R.val = R1.val
    ],
    "R -> e": [
        ((0, "val"), [(0, "acc")], copy),                            # R.val = R.acc
    ],
}

# D -> 0, D -> 1, ..., D -> 9 tienen la misma regla: D.val = digit_value(lexval)
for digit in "0123456789":
    RULES["D -> " + digit] = [
        ((0, "val"), [(1, "lexval")], digit_value),
    ]
