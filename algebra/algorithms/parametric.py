from __future__ import annotations
from typing import Any, Dict, List 
from .utils import (
    isclose, format_number, shape,
    clone_with, TOL 
)

from .utils import format_number
from ..Constants.SubDigits import SUBDIGITS

def xsub(i: int) ->str:
    s = str(i)
    return "x" + "".join(SUBDIGITS[ch] for ch in s)

def parametric_from_rref(Ab: List[List[float]], info: Dict[str, Any], param_base:str = "s", tol:float=TOL) -> Dict[str, Any]:
    R = clone_with(Ab)
    m, n1 = shape(R)
    n = n1 - 1
    basic = info.get("basic_vars", [])
    free  = info.get("free_vars", [])

    # asigna nombres de parámetros a variables libres en orden
    params = [f"{param_base}{i+1}" for i in range(len(free))]
    param_of_col = {col: params[k] for k, col in enumerate(free)}

    # mapa fila->col_pivote (en RREF cada básica tiene su fila con 1 en el pivote)
    pivot_row_of_col = {c: None for c in basic}
    for r in range(m):
        for c in basic:
            if isclose(R[r][c], 1.0, tol) and all(isclose(R[r][k], 0.0, tol) for k in range(c)):
                if all(isclose(R[k][c], 0.0, tol) for k in range(m) if k != r):
                    pivot_row_of_col[c] = r
                    break

    out_vars = []
    for col in range(n):
        if col in basic:
            r = pivot_row_of_col[col]
            if r is None:
                # fallback: constante 0
                out_vars.append({"col": col, "constant": format_number(0.0), "terms": [], "pretty": f"{xsub(col+1)} = 0"})
                continue

            const = R[r][n]
            terms = []
            pieces = [format_number(const)]
            for j in range(n):
                if j == col: 
                    continue
                a = R[r][j]
                if isclose(a, 0.0, tol):
                    continue
                # x_col = b - sum_j a*r_j * x_j  -> coef(param) = -a
                sign = "-" if a > 0 else "+"
                mag = abs(a)
                pname = param_of_col.get(j, xsub(j+1))
                mag_str = "" if abs(mag - 1.0) <= tol else format_number(mag)
                pieces.append(f"{sign} {mag_str} {pname}".strip())
                terms.append({"param": param_of_col.get(j, f"x{j+1}"), "coef": -a})

            pretty = f"{xsub(col+1)} = " + " ".join(pieces).replace("  ", " ").strip()
            out_vars.append({"col": col, "constant": format_number(const), "terms": terms, "pretty": pretty})
        else:
            pname = param_of_col[col]
            out_vars.append({"col": col, "constant": format_number(0.0), "terms": [{"param": pname, "coef": 1.0}], "pretty": f"{xsub(col+1)} = {pname}"})

    return {
        "params": params,
        "vars": out_vars,
        "pretty": [v["pretty"] for v in out_vars],
    }