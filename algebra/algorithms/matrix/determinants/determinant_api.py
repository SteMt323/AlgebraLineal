from __future__ import annotations
from typing import Any, Dict, List, Optional

from .crammer import (
    determinant_sarrus,
    determinant_cofactors,
    determinant_cramer,
    validate_determinant_properties,
)
from algebra.algorithms.utils import format_number, matrix_as_fraction


def determinant_api(*, A: List[List[float]], method: str = "cofactors", options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    opt = options or {}
    method = (method or "cofactors").lower()
    if A is None:
        raise ValueError("Se requiere la matriz A.")

    if method == "sarrus":
        det, steps = determinant_sarrus(A)
    elif method == "cofactors":
        det, steps = determinant_cofactors(A)
    elif method == "cramer":
        det, steps = determinant_cramer(A)
    else:
        raise ValueError(f"Método desconocido: {method}")

    props = validate_determinant_properties(A, det)

    return {
        "input": {"method": method, "A": A, "A_pretty": matrix_as_fraction(A)},
        "steps": steps,   # <-- YA ES {"frame":{"states":[...]}, "text_steps":[...]}
        "result": {"determinant": det, "determinant_pretty": format_number(det)},
        "properties": props,
    }
