from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from copy import deepcopy
from math import isclose as _isclose
from fractions import Fraction

Number = float
Matrix = List[List[Number]]
DetSteps = Dict[str, Any]  # {"frame":{"states":[...]}, "text_steps":[...]}

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


''' Registro de Pasos Para Vectores, Matrices y Reducciones'''
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


''' Registro de Pasos para Determinantes (Sarrus, Cofactors) '''

def det_steps_init() -> DetSteps:
    return {"frame": {"states": []}, "text_steps": []}

def _push_state(steps: DetSteps, *, tag: str, operation: str, matrix: Optional[List[List[float]]] = None, note: Optional[str] = None, extra: Optional[Dict[str, Any]] = None):
    st = {
        "index": len(steps["frame"]["states"]),
        "tag": tag,
        "operation": operation,
    }
    if matrix is not None:
        st["matrix"] = {"square": matrix_as_fraction(matrix), "shape": shape(matrix)}
    if note:
        st["note"] = note
    if extra:
        st.update(extra)
    steps["frame"]["states"].append(st)

def log_det_init(steps: DetSteps, A: List[List[float]], method_name: str):
    _push_state(
        steps,
        tag="initial",
        operation=f"Inicio determinante ({method_name})",
        matrix=A,
        note="Matriz cuadrada inicial"
    )

def log_sarrus_extended(steps: DetSteps, A_ext: List[List[float]]):
    _push_state(
        steps,
        tag="sarrus_extended",
        operation="Extensión de matriz: se agregan las 2 primeras columnas al final",
        matrix=A_ext
    )
    steps["text_steps"].append("Extender A copiando dos primeras columnas al final.")

def log_sarrus_diag(steps: DetSteps, kind: str, triples: List[Tuple[float,float,float]], partial_sum: float):
    """
    kind: "principal" | "secundaria"
    triples: lista de (a,b,c) para cada diagonal
    """
    terms_pretty = [f"({format_number(a)})·({format_number(b)})·({format_number(c)})" for (a,b,c) in triples]
    _push_state(
        steps,
        tag=f"sarrus_{'pos' if kind=='principal' else 'neg'}",
        operation=f"Diagonales {kind}",
        note=" + ".join(terms_pretty) + f" = {format_number(sum(a*b*c for (a,b,c) in triples))}",
        extra={"partials": [{"triple": [format_number(a), format_number(b), format_number(c)],
                             "value": format_number(a*b*c)} for (a,b,c) in triples],
               "sum": {"as_float": float(partial_sum), "as_fraction": format_number(partial_sum)}}
    )
    steps["text_steps"].append(f"Sumar diagonales {kind}: " + " + ".join(terms_pretty))

def log_det_result(steps: DetSteps, det: float, method_name: str, pos_sum: Optional[float] = None, neg_sum: Optional[float] = None):
    extra = {"determinant": {"as_float": float(det), "as_fraction": format_number(det)}}
    if pos_sum is not None:
        extra["positive_sum"] = {"as_float": float(pos_sum), "as_fraction": format_number(pos_sum)}
    if neg_sum is not None:
        extra["negative_sum"] = {"as_float": float(neg_sum), "as_fraction": format_number(neg_sum)}
    _push_state(
        steps,
        tag="result",
        operation=f"Resultado determinante ({method_name})",
        extra=extra
    )
    if pos_sum is not None and neg_sum is not None:
        steps["text_steps"].append(f"det(A) = {format_number(pos_sum)} − {format_number(neg_sum)} = {format_number(det)}")
    else:
        steps["text_steps"].append(f"det(A) = {format_number(det)}")

def log_cofactor_minor(steps: DetSteps, j: int, M1j: List[List[float]]):
    _push_state(
        steps,
        tag="cofactor_minor",
        operation=f"Menor M₁{j+1}: eliminar fila 1 y columna {j+1}",
        matrix=M1j
    )
    steps["text_steps"].append(f"Construir M₁{j+1} eliminando fila 1 y col {j+1}.")

def log_subdet_2x2(steps: DetSteps, M: List[List[float]], det2: float):
    a,b = M[0][0], M[0][1]
    c,d = M[1][0], M[1][1]
    _push_state(
        steps,
        tag="minor_2x2",
        operation="Determinante 2×2",
        matrix=M,
        note=f"({format_number(a)})·({format_number(d)}) − ({format_number(b)})·({format_number(c)}) = {format_number(det2)}",
        extra={"det2": {"as_float": float(det2), "as_fraction": format_number(det2)}}
    )
    steps["text_steps"].append(f"det(2×2) = ({format_number(a)})·({format_number(d)}) − ({format_number(b)})·({format_number(c)})")

def log_cofactor_value(steps: DetSteps, j: int, sign: int, a1j: float, sub_det: float, cofactor: float):
    sign_str = "+" if sign > 0 else "−"
    _push_state(
        steps,
        tag="cofactor_value",
        operation=f"Cofactor C₁{j+1}",
        note=f"({sign_str}1)·({format_number(a1j)})·({format_number(sub_det)}) = {format_number(cofactor)}",
        extra={
            "index_col": j+1,
            "sign": sign,
            "a1j": {"as_float": float(a1j), "as_fraction": format_number(a1j)},
            "subdet": {"as_float": float(sub_det), "as_fraction": format_number(sub_det)},
            "cofactor": {"as_float": float(cofactor), "as_fraction": format_number(cofactor)}
        }
    )
    steps["text_steps"].append(f"C₁{j+1} = ({sign_str}1)·{format_number(a1j)}·{format_number(sub_det)}")




# For determinants
def _matrix_pretty_lines(A: Matrix) -> List[str]:
    """Devuelve la matriz como líneas de texto con números formateados (fracción/entero)."""
    return [
        "[ " + "  ".join(format_number(x) for x in row) + " ]"
        for row in A
    ]

def _matrix_block(title: str, A: Matrix) -> str:
    lines = _matrix_pretty_lines(A)
    return title + ":\n" + "\n".join("  " + ln for ln in lines)



