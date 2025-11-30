from __future__ import annotations
from typing import Any, Dict, List, Optional

from ...utils.algebraic_support import isclose, TOL, format_number
from ..reduce.gauss_jordan import gauss_jordan_api

Number = float
Vec = List[Number]

# -------------------------------------------
# B) Combinación lineal / Ecuación vectorial (API)
# -------------------------------------------
def linear_combination_api(
    *,
    A: List[List[Number]],
    b: List[Number],
    options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    # 1) Gauss-Jordan (obtendremos steps y summary con forma paramétrica)
    gj = gauss_jordan_api(A=A, b=b, options=options or {})
    summary = gj["summary"]
    sol_type = summary["solution_type"]
    x_part = summary["parametric_form"]["particular"]  # puede ser None

    # 2) Verificación Ax = b con x_part (si existe)
    ax, ok = [], False
    if x_part is not None:
        m = len(A); n = len(A[0]) if m else 0
        ax = [sum(A[i][j] * x_part[j] for j in range(n)) for i in range(m)]
        ok = len(b) == len(ax) and all(isclose(ax[i], b[i], TOL) for i in range(len(b)))

    is_lin_comb = sol_type in ("unica", "infinitas")
    stmt = ("b es una combinación lineal de las columnas de A"
            if is_lin_comb else
            "b NO es una combinación lineal de las columnas de A")

    return {
        "input": {"A": A, "b": b, "A_pretty": [[format_number(x) for x in row] for row in A], "b_pretty": [format_number(x) for x in b]},
        "gauss_jordan": {"steps": gj["steps"], "summary": summary},
        "check": {
            "Ax": ax,
            "Ax_pretty": [format_number(x) for x in ax] if ax else None,
            "b_pretty": [format_number(x) for x in b],
            "ok": ok
        },
        "result": {
            "is_linear_combination": is_lin_comb,
            "solution_type": sol_type,
            "coefficients_particular": x_part,
            "coefficients_particular_pretty": [format_number(x) for x in x_part] if x_part is not None else None,
            "columns_statement": stmt
        }
    }