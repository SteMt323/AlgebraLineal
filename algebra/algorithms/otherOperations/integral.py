# algebra/algorithms/integral.py

from __future__ import annotations

from typing import Dict, Any

from sympy import Expr, Symbol, integrate, latex as sympy_latex


def compute_integral(expr: Expr, var_symbol: Symbol) -> Dict[str, Any]:
    """
    Calcula la integral indefinida de `expr` respecto a `var_symbol`.

    Devuelve:
    {
        "result_latex": "<latex de la integral>",
        "variable": "x"
    }

    Nota: SymPy no agrega "+ C"; si quieres, puedes ponérselo en el frontend.
    """
    integ = integrate(expr, var_symbol)

    return {
        "result_latex": sympy_latex(integ),
        "variable": str(var_symbol),
    }
