# algebra/utils/latex_parser.py
from __future__ import annotations
import re
from typing import Iterable, Tuple, Set
from sympy.parsing.latex import parse_latex
from sympy import Symbol


class LatexParsingError(Exception):
    pass


def _clean_latex_string(latex: str) -> str:
    """Normalizar cosas típicas de MathQuill antes de parsear."""
    if latex is None:
        raise LatexParsingError("No se recibió ninguna expresión en LaTeX.")

    s = str(latex).strip()
    if not s:
        raise LatexParsingError("La expresión en LaTeX está vacía.")

    # Quitar delimitadores tipo $...$, \(...\), \[...\]
    s = re.sub(r"^\$+|\$+$", "", s)
    s = re.sub(r"^\\\(|\\\)$", "", s)
    s = re.sub(r"^\\\[|\\\]$", "", s)

    # Eliminar \left y \right pero respetar |...|
    s = s.replace(r"\left", "").replace(r"\right", "")

    # No aceptar porcentaje aquí
    if r"\%" in s:
        raise LatexParsingError(
            "El símbolo de porcentaje (\\%) no está permitido en esta expresión."
        )

    return s


def latex_to_sympy_expr(latex: str) -> Tuple["sympy.Expr", Set[Symbol]]:
    """
    Parser LaTeX GLOBAL.
    - Devuelve: (expresión_sympy, conjunto_variables_libres)
    - Lanza LatexParsingError con mensajes amigables en caso de fallo.
    """
    cleaned = _clean_latex_string(latex)

    try:
        expr = parse_latex(cleaned)
    except Exception as e:
        raise LatexParsingError(
            f"No se pudo interpretar la expresión LaTeX: {str(e)}"
        )

    free_syms: Set[Symbol] = set(expr.free_symbols)

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
