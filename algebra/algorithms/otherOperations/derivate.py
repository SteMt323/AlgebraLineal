from __future__ import annotations

from typing import Dict, Any

from sympy import Expr, Symbol, diff, latex as sympy_latex


def compute_derivative(expr: Expr, var_symbol: Symbol) -> Dict[str, Any]:
    """
    Calcula la derivada primera de `expr` respecto a `var_symbol`.

    Devuelve:
    {
        "result_latex": "<latex de la derivada>",
        "variable": "x"
    }
    """
    deriv = diff(expr, var_symbol)

    return {
        "result_latex": sympy_latex(deriv),
        "variable": str(var_symbol),
    }
