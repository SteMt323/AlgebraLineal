from __future__ import annotations
from typing import Any, List, Tuple, Dict, Optional
from ..utils import(
    Matrix, Number, TOL, isclose, to_augmented, shape, 
    normalize_neg_zero, log_init, log_pivot, log_swap_rows, 
    log_row_op, log_upper, log_rref, format_number, clone_with,
    matrix_as_fraction
)

from ..parametric import parametric_from_rref
from algebra.Constants.subDigits import SUBDIGITS

# -------------------------------
# API de Gauss-Jordan
# -------------------------------
def gauss_jordan_api(
    *,
    A: Optional[Matrix] = None,
    b: Optional[List[Number]] = None,
    Ab: Optional[Matrix] = None,
    options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    opt = options or {}
    pivoting = opt.get("pivoting", "partial")    # "none" | "partial"
    keep_fractions = bool(opt.get("keep_fractions", False))  # reservado

    # Normaliza entrada a Ab y guarda b original para 'homogeneous'
    if Ab is None:
        if A is None or b is None:
            raise ValueError("Debes enviar Ab, o A y b.")
        Ab = to_augmented(A, b)
        original_b = list(b)
    else:
        Ab = clone_with(Ab)
        original_b = [row[-1] for row in Ab] if Ab else []

    m, n_plus_1 = shape(Ab)
    if n_plus_1 < 2:
        raise ValueError("La matriz aumentada debe tener al menos 2 columnas.")

    steps: List[Dict[str, Any]] = []
    log_init(steps, Ab)

    # 1) Forward → U
    pivots = forward_elimination(Ab, steps, pivoting=pivoting)
    log_upper(steps, Ab)

    # 2) Backward → RREF
    backward_to_rref(Ab, steps, pivots)
    log_rref(steps, Ab)

    # 3) Análisis en RREF + solución particular
    info = analyze_augmented(Ab)
    solution = None
    if info["status"] != "inconsistent":
        solution = particular_solution_from_rref(Ab, info)

    # 4) Resumen alineado con Gauss (incluye los 3 campos + has_non_trivial)
    m2, n1 = shape(Ab)
    n = n1 - 1
    rankA = info["rank"]
    rankAb = rankA + (1 if info["inconsistent_rows"] else 0)

    homogeneous = all(isclose(x, 0.0) for x in (original_b or []))
    dependence = "independientes" if rankA == n else "dependientes"
    trivial_solution = (solution is not None) and all(isclose(v, 0.0) for v in solution)
    parametric = parametric_from_rref(Ab, info, param_base="s")


    # Format solution and RREF to avoid floats
    formatted_solution = None
    if solution is not None:
        formatted_solution = [format_number(x) for x in solution]
    formatted_rref = matrix_as_fraction(clone_with(Ab))

    summary = {
        "ranks": {"rankA": rankA, "rankAb": rankAb},
        "solution_type": (
            "sin_solucion" if info["status"] == "inconsistent"
            else ("unica" if info["status"] == "unica" else "infinitas")
        ),
        "homogeneous": homogeneous,
        "dependence": dependence,
        "trivial_solution": trivial_solution,
        "variables": {"basic": info["basic_vars"], "free": info["free_vars"]},
        "parametric_form": {
            "exists": info["status"] == "infinitas",
            # keep numeric particular for programmatic use, provide a *_pretty for display
            "particular": solution,
            "particular_pretty": formatted_solution,
            "free_basis": None,
            "pretty": parametric["pretty"],
            "symbolic": parametric,
        },
        "reduced_form": {"RREF": formatted_rref, "note": ""},
    }

    return {
        "input": {"method": "gauss-jordan", "A": A, "b": b},
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

def forward_elimination(Ab: Matrix, steps: List[Dict[str, Any]], pivoting: str = "partial") -> List[Tuple[int, int]]:
    """
    Convierte Ab a triangular superior. Devuelve lista de pivotes (fila,col).
    """
    m, n1 = shape(Ab)
    n = n1 - 1
    row = 0
    pivots: List[Tuple[int, int]] = []

    for col in range(n):
        if row >= m:
            break

        # Selección de pivote
        pivot_row = None
        if pivoting == "partial":
            pivot_row = select_pivot_row(Ab, row, col)
        else:
            # "none": usa el primero no-cero
            for r in range(row, m):
                if not isclose(Ab[r][col], 0.0):
                    pivot_row = r
                    break

        if pivot_row is None or isclose(Ab[pivot_row][col], 0.0):
            # No hay pivote útil en esta columna
            continue

        if pivot_row != row:
            Ab[row], Ab[pivot_row] = Ab[pivot_row], Ab[row]
            log_swap_rows(steps, row, pivot_row, Ab)

        pivot_val = Ab[row][col]
        log_pivot(steps, row, col, pivot_val)

        # Eliminar por debajo
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

def backward_to_rref(Ab: Matrix, steps: List[Dict[str, Any]], pivots: List[Tuple[int, int]]) -> None:
    """
    A partir de la forma superior, normaliza pivotes a 1 y elimina arriba de cada pivote.
    Deja Ab en RREF.
    """
    m, n1 = shape(Ab)
    n = n1 - 1

    for (r, c) in reversed(pivots):
        pv = Ab[r][c]
        if isclose(pv, 0.0):
            continue
        # Normalizar fila del pivote
        if not isclose(pv, 1.0):
            for j in range(c, n + 1):
                Ab[r][j] /= pv
            normalize_neg_zero(Ab)
            log_row_op(steps, f"R{r+1} ← R{r+1} / {format_number(pv)}", Ab)

        # Eliminar arriba del pivote
        for rr in range(0, r):
            if isclose(Ab[rr][c], 0.0):
                continue
            factor = Ab[rr][c]
            for j in range(c, n + 1):
                Ab[rr][j] -= factor * Ab[r][j]
            normalize_neg_zero(Ab)
            log_row_op(steps, f"R{rr+1} ← R{rr+1} - ({format_number(factor)})·R{r+1}", Ab)

def analyze_augmented(Ab: Matrix, tol: float = TOL) -> Dict[str, Any]:
    m, n1 = shape(Ab)
    n = n1 - 1
    pivots: List[Tuple[int, int]] = []
    pivot_cols = [False] * n

    # Detectar pivotes (en RREF: 1 con ceros alrededor en su columna)
    for r in range(m):
        pivot_c = None
        for c in range(n):
            if isclose(Ab[r][c], 1.0, tol) and all(isclose(Ab[r][k], 0.0, tol) for k in range(c)) \
               and all(isclose(Ab[k][c], 0.0, tol) for k in range(m) if k != r):
                pivot_c = c
                break
        if pivot_c is not None:
            pivots.append((r, pivot_c))
            pivot_cols[pivot_c] = True

    # Filas inconsistentes: 0..0 | d ≠ 0
    inconsistent_rows = []
    for r in range(m):
        if all(isclose(Ab[r][c], 0.0, tol) for c in range(n)) and not isclose(Ab[r][n], 0.0, tol):
            inconsistent_rows.append(r)

    rank = len(pivots)
    basic_vars = [c for c in range(n) if pivot_cols[c]]
    free_vars = [c for c in range(n) if not pivot_cols[c]]

    if inconsistent_rows:
        status = "inconsistent"
    elif rank == n:
        status = "unica"
    else:
        status = "infinitas"

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

def particular_solution_from_rref(Ab: Matrix, info: Dict[str, Any], tol: float = TOL) -> Optional[List[float]]:
    """
    Toma Ab en RREF. Fija variables libres = 0 y lee variables básicas del RHS.
    """
    if info["status"] == "inconsistent":
        return None
    n = info["n"]
    x = [0.0] * n
    rhs = [row[-1] for row in Ab]

    for (r, c) in info["pivots"]:
        # fila del pivote debe ser [0..0, 1, 0.. | value]
        x[c] = rhs[r]
    return x