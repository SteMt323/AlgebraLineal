# algebra/utils/latex_parser.py
from __future__ import annotations
import re
from typing import Iterable, Tuple, Set
from sympy.parsing.latex import parse_latex
from sympy import Symbol, E


class LatexParsingError(Exception):
    pass


def _clean_latex_string(latex: str) -> str:
    s = latex.strip()

    # Quitar $...$ si llegan así
    if s.startswith("$") and s.endswith("$"):
        s = s[1:-1].strip()

    # Quitar \left \right por comodidad
    s = s.replace(r"\left", "").replace(r"\right", "")

    # (aquí puedes tener otros sanitizados que ya usabas)

    return s


def latex_to_sympy_expr(latex: str):
    s = _clean_latex_string(latex)

    try:
        expr = parse_latex(s)
    except Exception as e:
        raise LatexParsingError(
            f"Error al interpretar la expresión LaTeX: {e}"
        ) from e

    # --- AQUÍ VIENE LA MAGIA: tratar 'e' como constante de Euler ---

    # Si existe un símbolo 'e' en la expresión, lo reemplazamos por E
    e_sym = Symbol("e")
    if e_sym in expr.free_symbols:
        expr = expr.subs(e_sym, E)

    # Volvemos a calcular símbolos libres (ahora sin 'e')
    free_syms = set(expr.free_symbols)

    return expr, free_syms


# ---------- Versión especializada para MÉTODO DE BISECCIÓN ----------

def latex_to_sympy_expr_for_bisection(latex: str):
    """
    Parser LaTeX pensado específicamente para el método de bisección.

    Restricciones:
    - Solo se permite UNA variable libre.
    - La variable debe llamarse 'x'.
    - No se permiten operadores de cálculo (Integral, Derivative, Sum, Product, Limit).
    """
    from sympy import Integral, Derivative, Sum, Product, Limit

    expr, free_syms = latex_to_sympy_expr(latex)

    if not free_syms:
        raise LatexParsingError("La función debe depender de la variable x.")
    if len(free_syms) > 1:
        raise LatexParsingError(
            "Para el método de bisección solo se permite una variable (x)."
        )

    x_symbol = next(iter(free_syms))
    if str(x_symbol) != "x":
        raise LatexParsingError(
            "La variable de la función debe ser x (por ejemplo f(x) = x^2 - 3x + 1)."
        )

    # Bloquear integrales, derivadas, sumatorias, productos, límites…
    forbidden_types = (Integral, Derivative, Sum, Product, Limit)
    if expr.has(*forbidden_types):
        raise LatexParsingError(
            "La expresión contiene operadores de cálculo "
            "(integrales, derivadas, sumatorias, productos o límites) "
            "que no están permitidos en el método de bisección."
        )

    return expr, x_symbol
