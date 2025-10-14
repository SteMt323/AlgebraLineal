from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from ..utils import (
    Matrix, Number, TOL, isclose, to_augmented, shape, normalize_neg_zero,
    log_init, log_pivot, log_swap_rows, log_row_op, log_upper, format_number, clone_with,
    matrix_as_fraction
)
from ..parametric import parametric_from_rref

# -------------------------------
# API de Gauss
# -------------------------------

def gauss_api(
        *,
        A: Optional[Matrix] = None,
        b: Optional[List[Number]] = None,
        Ab: Optional[Matrix] = None,
        options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    opt = options or {}
    pivoting = opt.get("pivoting", "partial")  # "none" | "partial"

    # 0) Normalizar entrada a Ab
    original_b = None
    if Ab is None:
        if A is None or b is None:
            raise ValueError("Debes enviar Ab, o A y b.")
        Ab = to_augmented(A, b)
        original_b = list(b)
    else:
        Ab = clone_with(Ab)
        # Si recibimos Ab “solo”, inferimos b inicial
        original_b = [row[-1] for row in Ab] if Ab else []

    m, n1 = shape(Ab)
    if n1 < 2:
        raise ValueError("La matriz aumentada debe tener al menos 2 columnas.")
    n = n1 - 1

    steps: List[Dict[str, Any]] = []
    log_init(steps, Ab)

    # 1) Eliminación hacia adelante → U (triangular superior)
    pivots = forward_elimination_to_U(Ab, steps, pivoting=pivoting)
    log_upper(steps, Ab)

    # 2) Analizar (rank, básicas/libres, consistencia) y resolver
    info = analyze_from_upper(Ab)
    solution = None
    if info["status"] != "inconsistent":
        solution = back_substitution_particular(Ab, info["pivots"])

    Ab_rref = clone_with(Ab)
    if info["status"] != "inconsistent":
        u_to_rref_inplace(Ab_rref, info["pivots"])
        parametric = parametric_from_rref(Ab_rref, {
            "basic_vars": info["basic_vars"],
            "free_vars": info["free_vars"]
        })
    else:
        parametric = {"params": [], "vars": [], "pretty": []}

    # 3) Construir summary incluyendo TUS 3 campos extra
    rankA = info["rank"]
    rankAb = rankA + (1 if info["inconsistent_rows"] else 0)

    homogeneous = all(isclose(x, 0.0) for x in (original_b or []))
    dependence = "independientes" if rankA == n else "dependientes"
    trivial_solution = bool(solution) and all(isclose(v, 0.0) for v in solution)

    # Format solution and RREF to avoid floats
    formatted_solution = None
    if solution is not None:
        formatted_solution = [format_number(x) for x in solution]
    formatted_rref = matrix_as_fraction(Ab_rref)

    summary = {
        "ranks": {"rankA": rankA, "rankAb": rankAb},
        "solution_type": (
            "sin_solucion" if info["status"] == "inconsistent"
            else ("unica" if info["status"] == "unique" else "infinitas")
        ),
        "homogeneous": homogeneous,
        "dependence": dependence,
        "trivial_solution": trivial_solution,
        "variables": {"basic": info["basic_vars"], "free": info["free_vars"]},
        "parametric_form": {
            "exists": info["status"] == "infinite",
            "particular": solution,
            "particular_pretty": formatted_solution,
            "free_basis": None,
            "pretty": parametric["pretty"],   # <---- NUEVO
            "symbolic": parametric, 
        },
        "reduced_form": {
            "U": matrix_as_fraction(clone_with(Ab)), 
            "RREF": formatted_rref if info["status"] != "inconsistent" else None,
            "note": "Triangular superior (U)"},
    }

    return {
        "input": {"method": "gauss", "A": A, "b": b},
        "steps": steps,
        "summary": summary,
    }


def select_pivot_row(Ab: Matrix, start_row: int, col: int) -> Optional[int]:
    m, _ = shape(Ab)
    sel = None
    best = 0.0
    for r in range(start_row, m):
        v = abs(Ab[r][col])
        if v > best and not isclose(v, 0.0):
            best = v
            sel = r
    return sel

def forward_elimination_to_U(Ab: Matrix, steps: List[Dict[str, Any]], pivoting: str = "partial") -> List[Tuple[int, int]]:
    m, n1 = shape(Ab)
    n = n1 - 1
    row = 0
    pivots: List[Tuple[int, int]] = []

    for col in range(n):
        if row >= m:
            break

        # 1) Selección pivote
        pivot_row = None
        if pivoting == "partial":
            pivot_row = select_pivot_row(Ab, row, col)
        else:
            for r in range(row, m):
                if not isclose(Ab[r][col], 0.0):
                    pivot_row = r
                    break

        # 2) Sin pivote útil → sigue
        if pivot_row is None or isclose(Ab[pivot_row][col], 0.0):
            continue

        # 3) Swap si corresponde
        if pivot_row != row:
            Ab[row], Ab[pivot_row] = Ab[pivot_row], Ab[row]
            log_swap_rows(steps, row, pivot_row, Ab)

        pivot_val = Ab[row][col]
        log_pivot(steps, row, col, pivot_val)

        # 4) Eliminar debajo del pivote
        for r in range(row + 1, m):
            if isclose(Ab[r][col], 0.0):
                continue
            factor = Ab[r][col] / pivot_val
            for c in range(col, n + 1):
                Ab[r][c] -= factor * Ab[row][c]
            normalize_neg_zero(Ab)
            log_row_op(steps, f"R{r+1} ← R{r+1} - ({format_number(factor)})·R{row+1}", Ab)

        pivots.append((row, col))
        row += 1

    return pivots

def analyze_from_upper(U: Matrix, tol: float = TOL) -> Dict[str, Any]:
    m, n1 = shape(U)
    n = n1 - 1

    pivots: List[Tuple[int, int]] = []
    pivot_cols = [False] * n

    # Primer coeficiente no-cero por fila (en la parte de A)
    for r in range(m):
        pc = -1
        for c in range(n):
            if not isclose(U[r][c], 0.0, tol):
                pc = c
                break
        if pc != -1:
            pivots.append((r, pc))
            pivot_cols[pc] = True

    # Inconsistencias: 0..0 | d != 0
    inconsistent_rows: List[int] = []
    for r in range(m):
        if all(isclose(U[r][c], 0.0, tol) for c in range(n)) and not isclose(U[r][n], 0.0, tol):
            inconsistent_rows.append(r)

    rank = len(pivots)
    basic_vars = [c for c in range(n) if pivot_cols[c]]
    free_vars = [c for c in range(n) if not pivot_cols[c]]

    if inconsistent_rows:
        status = "inconsistent"
    elif rank == n:
        status = "unique"
    else:
        status = "infinite"

    return {
        "m": m,
        "n": n,
        "rank": rank,
        "pivots": pivots,
        "basic_vars": basic_vars,
        "free_vars": free_vars,
        "inconsistent_rows": inconsistent_rows,
        "status": status,
    }

def back_substitution_particular(U: Matrix, pivots: List[Tuple[int, int]], tol: float = TOL) -> List[float]:
    """
    Sustitución hacia atrás fijando libres=0. Devuelve solución particular.
    """
    m, n1 = shape(U)
    n = n1 - 1
    x = [0.0] * n
    pivots_sorted = sorted(pivots, key=lambda rc: rc[0])

    for (r, c) in reversed(pivots_sorted):
        rhs = U[r][n]
        s = rhs
        for j in range(c + 1, n):
            s -= U[r][j] * x[j]
        pv = U[r][c]
        x[c] = 0.0 if isclose(pv, 0.0, tol) else s / pv
    return x

def u_to_rref_inplace(U: List[List[float]], pivots: List[Tuple[int,int]], tol: float = TOL) -> None:
    """Normaliza a RREF en sitio utilizando los pivotes detectados (fila, col)."""
    m, n1 = shape(U)
    n = n1 - 1
    # Normaliza cada pivote a 1 y elimina arriba
    for (r, c) in reversed(sorted(pivots, key=lambda rc: rc[0])):
        pv = U[r][c]
        if not isclose(pv, 0.0, tol) and not isclose(pv, 1.0, tol):
            for j in range(c, n + 1):
                U[r][j] /= pv
        for rr in range(0, r):
            if isclose(U[rr][c], 0.0, tol):
                continue
            factor = U[rr][c]
            for j in range(c, n + 1):
                U[rr][j] -= factor * U[r][j]
