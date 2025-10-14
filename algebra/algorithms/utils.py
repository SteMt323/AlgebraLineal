from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from copy import deepcopy
from math import isclose as _isclose
from fractions import Fraction

Number = float
Matrix = List[List[Number]]

TOL = 1e-12

def isclose(a:float, b: float = 0.0, tol:float = TOL) -> bool:
    return _isclose(a, b, abs_tol=tol)

def deepcopy_mat(M: Optional[Matrix]) -> Matrix:
    return [] if M is None else deepcopy(M)

def format_number(x: float) -> str:
    # Entero si es exacto, fraccion si no lo es
    if abs(x - int(round(x))) < TOL:
        return str(int(round(x)))
    frac = Fraction(x).limit_denominator()
    return str(frac)


def matrix_as_fraction(M: Matrix) -> List[List[str]]:
    return [[format_number(v) for v in row] for row in (M or [])]

def to_augmented(A: Matrix, b: List[Number]) -> Matrix:
    if len(A) != len(b):
        raise ValueError("Dimensiones inconsistentes entre A y b.")
    return [row + [b[i]] for i, row in enumerate(A)]

def shape(M: Matrix) -> Tuple[int, int]:
    if not M:
        return (0, 0)
    return (len(M), len(M[0]))

def normalize_neg_zero(M: Matrix, tol: float = TOL) -> None:
    for i in range(len(M)):
        for j in range(len(M[0])):
            if isclose(M[i][j], 0.0, tol):
                M[i][j] = 0.0

def clone_with(M: Matrix) -> Matrix:
    C = deepcopy(M)
    normalize_neg_zero(C)
    return C


''' Registro de Pasos '''
def log_init(steps: List[Dict[str, Any]], Ab: Matrix) -> None:
    steps.append({
        "index": len(steps),
        "operation": "Inicial",
        "matrix": {
            "augmented":matrix_as_fraction(Ab),
            "shape": shape(Ab)},
        "note": "Matriz aumentada inicial"
    })

def log_pivot(steps: List[Dict[str, Any]], r: int, c: int, val: float) -> None:
    steps.append({
        "index": len(steps),
        "operation": f"Pivot @ ({r+1},{c+1}) = {format_number(val)}",
        "pivot": {"row": r, "col": c, "value": {"as_float": float(val), "as_fraction": format_number(val)}},
    })

def log_swap_rows(steps: List[Dict[str, Any]], i: int, j:int, Ab: Matrix) -> None:
    steps.append({
        "index": len(steps),
        "operation": f"Intercambio filas: F{i+1} <-> F{j+1}",
        "swap": {"type": "rows", "i": i, "j": j},
        "matrix": { "augmented": matrix_as_fraction(Ab)},
        "tag": "swap_rows",
        })
    
def log_row_op(steps: List[Dict[str, Any]], text: str, Ab: Matrix) -> None:
    steps.append({
        "index": len(steps),
        "operation": text,
        "row_op": {"text": text},
        "matrix": {
            "augmented": matrix_as_fraction(Ab),
                   },
        "tag": "elim",
    })

def log_upper(steps: List[Dict[str, Any]], Ab: Matrix) -> None:
    steps.append({
        "index": len(steps),
        "operation": "Triangulación superior (U)",
        "matrix": {
            "augmented": matrix_as_fraction(Ab),
            },
        "tag": "upper",
    })

def log_rref(steps: List[Dict[str, Any]], Ab: Matrix) -> None:
    steps.append({
        "index": len(steps),
        "operation": "Forma reducida por filas (RREF)",
        "matrix": {
            "augmented": matrix_as_fraction(Ab),
            },
        "tag": "rref",
    })