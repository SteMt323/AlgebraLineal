from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple

from algebra.Constants.properties import DETERMINANT_PROPERTIES

from algebra.algorithms.utils import (
    isclose, format_number, matrix_as_fraction, shape, normalize_neg_zero, clone_with, TOL
)

Number = float
Matrix = List[List[Number]]



def _check_square(A: Matrix) -> None:
    m, n = shape(A)
    if m != n:
        raise ValueError("La matriz debe ser cuadrada para calcular el determinante.")


def determinant_sarrus(A: Matrix) -> Tuple[float, List[str]]:
    """Calcula determinante usando la regla de Sarrus (solo 3x3).

    Returns: (determinant, steps)
    """
    _check_square(A)
    n = shape(A)[0]
    if n != 3:
        raise ValueError("La Regla de Sarrus solo aplica para matrices 3x3.")

    steps: List[str] = []
    a11, a12, a13 = A[0]
    a21, a22, a23 = A[1]
    a31, a32, a33 = A[2]

    # diagonales positivas
    d1_pos = a11 * a22 * a33
    d2_pos = a12 * a23 * a31
    d3_pos = a13 * a21 * a32
    positive = d1_pos + d2_pos + d3_pos
    steps.append(f"Diagonales principales: {format_number(d1_pos)}, {format_number(d2_pos)}, {format_number(d3_pos)} (suma = {format_number(positive)})")

    # diagonales negativas
    d1_neg = a13 * a22 * a31
    d2_neg = a11 * a23 * a32
    d3_neg = a12 * a21 * a33
    negative = d1_neg + d2_neg + d3_neg
    steps.append(f"Diagonales secundarias: {format_number(d1_neg)}, {format_number(d2_neg)}, {format_number(d3_neg)} (suma = {format_number(negative)})")

    det = positive - negative
    steps.append(f"Determinante (Sarrus) = {format_number(positive)} - {format_number(negative)} = {format_number(det)}")
    return det, steps


def determinant_cofactors(A: Matrix) -> Tuple[float, List[str]]:
    """Calcula determinante por expansión por cofactores (recursivo).

    Returns: (determinant, steps_summary)
    """
    _check_square(A)
    n = shape(A)[0]

    steps: List[str] = []

    def _det_cof(M: Matrix) -> float:
        size = shape(M)[0]
        if size == 1:
            return M[0][0]
        if size == 2:
            return M[0][0] * M[1][1] - M[0][1] * M[1][0]
        total = 0.0
        for j in range(size):
            # build submatrix excluding row 0 and column j
            sub = [[M[i][k] for k in range(size) if k != j] for i in range(1, size)]
            sub_det = _det_cof(sub)
            cofactor = ((-1) ** j) * M[0][j] * sub_det
            steps.append(f"Cofactor for element (0,{j}) = ({format_number(M[0][j])}) * det(sub) = {format_number(cofactor)}")
            total += cofactor
        return total

    det = _det_cof(A)
    steps.insert(0, f"Expansión por cofactores sobre la primera fila (tamaño {n}x{n})")
    steps.append(f"Determinante (cofactores) = {format_number(det)}")
    return det, steps


def determinant_cramer(A: Matrix) -> Tuple[float, List[str]]:
    """Compatibilidad con la interfaz 'cramer' — aquí usamos expansión por cofactores.

    Returns same as cofactors for determinant calculation.
    """
    # In CramerMethod.py the 'cramer' option delegates to the generic determinant
    return determinant_cofactors(A)


def validate_determinant_properties(A: Matrix, det: float) -> Dict[str, Any]:
    """Valida algunas propiedades comunes relacionadas con determinantes y devuelve
    un resumen con resultados booleanos y evidencias.
    """
    props: Dict[str, Any] = {}
    m, n = shape(A)

    # 1) Si una fila o columna es cero => det == 0
    zero_row = any(all(isclose(x, 0.0, TOL) for x in row) for row in A)
    zero_col = any(all(isclose(A[i][j], 0.0, TOL) for i in range(m)) for j in range(n))
    props['zero_row_or_col'] = {
        'applies': zero_row or zero_col,
        'message': DETERMINANT_PROPERTIES.get(1),
        'evidence': {
            'zero_row': zero_row,
            'zero_col': zero_col
        }
    }

    # 2) Dos filas o columnas iguales => det == 0
    equal_rows = False
    for i in range(m):
        for j in range(i+1, m):
            if all(isclose(A[i][k], A[j][k], TOL) for k in range(n)):
                equal_rows = True
    equal_cols = False
    for i in range(n):
        for j in range(i+1, n):
            if all(isclose(A[k][i], A[k][j], TOL) for k in range(m)):
                equal_cols = True
    props['equal_rows_or_cols'] = {
        'applies': equal_rows or equal_cols,
        'message': DETERMINANT_PROPERTIES.get(2),
        'evidence': {'equal_rows': equal_rows, 'equal_cols': equal_cols}
    }

    # 3) Intercambio de filas multiplica por -1: we can demonstrate by swapping two rows and comparing
    swapped_demo = None
    if m > 1:
        Mswap = clone_with(A)
        Mswap[0], Mswap[1] = Mswap[1], Mswap[0]
        try:
            det_swap, _ = determinant_cofactors(Mswap)
            swapped_demo = isclose(det_swap, -det, TOL)
        except Exception:
            swapped_demo = False
    props['swap_rows_sign'] = {
        'applies': swapped_demo,
        'message': DETERMINANT_PROPERTIES.get(3),
        'evidence': {'det_original': format_number(det), 'det_after_swap': format_number(det * -1) if det is not None else None}
    }

    # 4) Si una columna es múltiplo escalar de otra -> det == 0
    scalar_mult_col = False
    if n > 1:
        for i in range(n):
            for j in range(i+1, n):
                # find scalar k such that column_j = k * column_i
                k = None
                ok = True
                for r in range(m):
                    a = A[r][i]
                    b = A[r][j]
                    if isclose(a, 0.0, TOL):
                        if not isclose(b, 0.0, TOL):
                            ok = False
                            break
                        else:
                            continue
                    ratio = b / a
                    if k is None:
                        k = ratio
                    elif not isclose(k, ratio, TOL):
                        ok = False
                        break
                if ok and k is not None:
                    scalar_mult_col = True
    props['scalar_multiple_column'] = {
        'applies': scalar_mult_col,
        'message': DETERMINANT_PROPERTIES.get(4),
        'evidence': {'found': scalar_mult_col}
    }

    # add a quick consistency check: if any of the above implies det == 0 but computed det not ~0, mark inconsistent
    inferred_zero = props['zero_row_or_col']['applies'] or props['equal_rows_or_cols']['applies'] or props['scalar_multiple_column']['applies']
    props['consistency'] = {
        'inferred_zero': inferred_zero,
        'det_is_zero': isclose(det, 0.0, TOL),
        'consistent': (not inferred_zero) or isclose(det, 0.0, TOL)
    }

    return props

__all__ = ['determinant_sarrus', 'determinant_cofactors', 'determinant_cramer', 'validate_determinant_properties']