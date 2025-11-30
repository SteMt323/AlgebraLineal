from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple

from ...utils.algebraic_support import (
    isclose, format_number, matrix_as_fraction, shape, normalize_neg_zero, clone_with, TOL
)

Number = float
Matrix = List[List[Number]]


# --------------------------
# Operaciones básicas sobre matrices (implementadas localmente)
# --------------------------
def _shape(M: Matrix) -> Tuple[int, int]:
    return shape(M)


def add_matrices(A: Matrix, B: Matrix) -> Tuple[Matrix, str]:
    if _shape(A) != _shape(B):
        raise ValueError("Dimensiones incompatibles para suma/resta (mismas filas y columnas).")
    m, n = _shape(A)
    C = [[A[i][j] + B[i][j] for j in range(n)] for i in range(m)]
    steps = []
    for i in range(m):
        row_terms = []
        for j in range(n):
            row_terms.append(f"({format_number(A[i][j])}) + ({format_number(B[i][j])}) = {format_number(C[i][j])}")
        steps.append(f"  Fila {i+1}: " + " | ".join(row_terms))
    return C, "\n".join(steps)


def sub_matrices(A: Matrix, B: Matrix) -> Tuple[Matrix, str]:
    if _shape(A) != _shape(B):
        raise ValueError("Dimensiones incompatibles para suma/resta (mismas filas y columnas).")
    m, n = _shape(A)
    C = [[A[i][j] - B[i][j] for j in range(n)] for i in range(m)]
    steps = []
    for i in range(m):
        row_terms = []
        for j in range(n):
            row_terms.append(f"({format_number(A[i][j])}) - ({format_number(B[i][j])}) = {format_number(C[i][j])}")
        steps.append(f"  Fila {i+1}: " + " | ".join(row_terms))
    return C, "\n".join(steps)


def scalar_mult(alpha: float, A: Matrix) -> Tuple[Matrix, str]:
    m, n = _shape(A)
    C = [[alpha * A[i][j] for j in range(n)] for i in range(m)]
    steps = []
    for i in range(m):
        row_terms = []
        for j in range(n):
            row_terms.append(f"{format_number(alpha)}·({format_number(A[i][j])}) = {format_number(C[i][j])}")
        steps.append(f"  Fila {i+1}: " + " | ".join(row_terms))
    return C, "\n".join(steps)


def transpose(A: Matrix) -> Tuple[Matrix, str]:
    m, n = _shape(A)
    T = [[A[i][j] for i in range(m)] for j in range(n)]
    lines = []
    for j in range(n):
        moved = ", ".join(f"a_{i+1}{j+1}→t_{j+1}{i+1}" for i in range(m))
        lines.append(f"  Columna {j+1} de A pasa a Fila {j+1} de Aᵀ ({moved})")
    return T, "\n".join(lines)


def matmul(A: Matrix, B: Matrix) -> Tuple[Matrix, str]:
    if _shape(A)[1] != _shape(B)[0]:
        raise ValueError("Dimensiones incompatibles para multiplicación (cols(A) = filas(B)).")
    m, p = _shape(A)[0], _shape(B)[1]
    n = _shape(A)[1]
    C = [[0.0 for _ in range(p)] for _ in range(m)]
    steps = []
    for i in range(m):
        for j in range(p):
            terms = [f"{format_number(A[i][k])}·{format_number(B[k][j])}" for k in range(n)]
            val = sum(A[i][k] * B[k][j] for k in range(n))
            C[i][j] = val
            steps.append(f"  c_{i+1}{j+1} = " + " + ".join(terms) + f" = {format_number(val)}")
    return C, "\n".join(steps)


# --------------------------
# Operaciones con varias matrices
# --------------------------
def sum_many(mats: List[Matrix]) -> Tuple[Matrix, str]:
    if len(mats) < 2:
        raise ValueError("Se requieren al menos 2 matrices para la suma.")
    base = mats[0]
    for M in mats[1:]:
        if _shape(base) != _shape(M):
            raise ValueError("Todas las matrices deben tener la misma dimensión para sumar.")
    m, n = _shape(base)
    C = [[0.0 for _ in range(n)] for _ in range(m)]
    steps = []
    for i in range(m):
        for j in range(n):
            terms = [format_number(M[i][j]) for M in mats]
            val = sum(M[i][j] for M in mats)
            C[i][j] = val
            steps.append(f"  s_{i+1}{j+1} = " + " + ".join(terms) + f" = {format_number(val)}")
    return C, "\n".join(steps)


def sub_many(first: Matrix, rest: List[Matrix]) -> Tuple[Matrix, str]:
    if not rest:
        raise ValueError("Se necesita al menos una matriz para restar a la primera.")
    for M in rest:
        if _shape(first) != _shape(M):
            raise ValueError("Todas las matrices deben tener la misma dimensión para restar.")
    m, n = _shape(first)
    C = [[0.0 for _ in range(n)] for _ in range(m)]
    steps = []
    for i in range(m):
        for j in range(n):
            terms = [format_number(first[i][j])] + [f"({format_number(M[i][j])})" for M in rest]
            val = first[i][j] - sum(M[i][j] for M in rest)
            C[i][j] = val
            steps.append(f"  r_{i+1}{j+1} = " + " - ".join(terms) + f" = {format_number(val)}")
    return C, "\n".join(steps)


def matmul_chain(mats: List[Matrix]) -> Tuple[Matrix, str]:
    if len(mats) < 2:
        raise ValueError("Se requieren al menos 2 matrices para multiplicar.")
    current = mats[0]
    all_steps = []
    for idx, M in enumerate(mats[1:], start=2):
        C, steps = matmul(current, M)
        all_steps.append(f"Paso {idx-1}: resultado anterior · M{idx}\n" + steps)
        current = C
    return current, "\n\n".join(all_steps)


# --------------------------
# Determinante e inversa (usando eliminación Gaussiana)
# --------------------------
def determinant(A: Matrix, tol: float = TOL) -> float:
    m, n = _shape(A)
    if m != n:
        raise ValueError("Determinante sólo definido para matrices cuadradas.")

    M = [row[:] for row in A]
    det = 1.0
    row = 0
    swaps = 0
    for col in range(n):
        if row >= n:
            break
        sel = row
        best = abs(M[row][col])
        for r in range(row + 1, n):
            v = abs(M[r][col])
            if v > best:
                best = v
                sel = r

        if best <= tol:
            # columna nula -> pivote no disponible
            continue

        if sel != row:
            M[row], M[sel] = M[sel], M[row]
            swaps += 1

        pivot = M[row][col]
        det *= pivot

        # escalar fila
        if not isclose(pivot, 1.0, tol):
            for j in range(col, n):
                M[row][j] /= pivot

        # eliminación completa (arriba y abajo)
        for r in range(n):
            if r == row:
                continue
            factor = M[r][col]
            if abs(factor) <= tol:
                continue
            for j in range(col, n):
                M[r][j] -= factor * M[row][j]
            normalize_neg_zero(M)

        row += 1

    if swaps % 2 != 0:
        det = -det
    return 0.0 if abs(det) <= tol else det


def inverse(A: Matrix, tol: float = TOL, frame: dict | None = None, check_props: bool = True) -> Tuple[Matrix, str]:
    m, n = _shape(A)
    if m != n:
        raise ValueError("La inversa sólo está definida para matrices cuadradas.")

    detA = determinant(A, tol=tol)
    if abs(detA) <= tol:
        raise ValueError(f"Matriz singular: det(A) = {format_number(detA)}")

    # construir matriz aumentada [A | I]
    M = [list(map(float, row)) + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate([r[:] for r in A])]
    steps: List[str] = []
    # If a frame dict is provided, prepare both a backwards-compatible
    # `states` list (used previously) and a new `step_states` list that will
    # contain a snapshot of the matrix after each textual step. This allows the
    # API consumer to align text_steps[i] with step_states[i].
    if frame is not None:
        frame['states'] = []
        frame['step_states'] = []
        frame['states'].append({'tag': 'initial', 'matrix': clone_with(M)})

    row = 0
    for col in range(n):
        if row >= n:
            break
        # seleccionar pivote por valor absoluto
        sel = row
        best = abs(M[row][col])
        for r in range(row + 1, n):
            v = abs(M[r][col])
            if v > best:
                best = v
                sel = r

        if best <= tol:
            raise ValueError("No se pudo encontrar pivote no nulo durante la inversión.")

        if sel != row:
            M[row], M[sel] = M[sel], M[row]
            steps.append(f"Intercambio filas: F{row+1} <-> F{sel+1}")
            # record snapshot after swap so clients can align text steps -> matrices
            if frame is not None:
                frame['step_states'].append({'tag': f'swap_{row}_{sel}', 'matrix': clone_with(M)})

        pivot = M[row][col]
        # escalar fila para pivot = 1
        if abs(pivot - 1.0) > tol:
            for j in range(col, 2 * n):
                M[row][j] /= pivot
            steps.append(f"R{row+1} ← R{row+1} / {format_number(pivot)}")
            normalize_neg_zero(M)
            # snapshot after scaling pivot row
            if frame is not None:
                frame['step_states'].append({'tag': f'scale_{row}', 'matrix': clone_with(M)})

        # eliminar en otras filas
        for r in range(n):
            if r == row:
                continue
            factor = M[r][col]
            if abs(factor) <= tol:
                continue
            for j in range(col, 2 * n):
                M[r][j] -= factor * M[row][j]
            steps.append(f"R{r+1} ← R{r+1} - ({format_number(factor)})·R{row+1}")
            normalize_neg_zero(M)
            # snapshot after eliminating row r using current pivot
            if frame is not None:
                frame['step_states'].append({'tag': f'elim_r{r}_c{col}', 'matrix': clone_with(M)})

        if frame is not None:
            frame['states'].append({'tag': f'pivot_{row}_{col}', 'matrix': clone_with(M)})

        row += 1

    Ainv = [[M[i][j] for j in range(n, 2 * n)] for i in range(n)]
    if frame is not None:
        frame['states'].append({'tag': 'result', 'matrix': clone_with(Ainv)})

    return Ainv, "\n".join(steps)
