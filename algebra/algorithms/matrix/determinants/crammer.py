from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple

from algebra.Constants.properties import DETERMINANT_PROPERTIES

from algebra.algorithms.utils import (
    isclose, format_number, shape, clone_with, TOL, 
    det_steps_init, log_det_init, log_sarrus_extended,
    log_sarrus_diag, log_det_result, log_cofactor_minor, log_subdet_2x2, 
    log_cofactor_value, DetSteps
)

Number = float
Matrix = List[List[Number]]



def _check_square(A: Matrix) -> None:
    m, n = shape(A)
    if m != n:
        raise ValueError("La matriz debe ser cuadrada para calcular el determinante.")


def determinant_sarrus(A: List[List[float]]) -> Tuple[float, DetSteps]:
    _check_square(A)
    m, n = shape(A)
    if n != 3:
        raise ValueError("La Regla de Sarrus solo aplica para matrices 3x3.")

    steps = det_steps_init()
    method_name = "Sarrus"
    log_det_init(steps, A, method_name)

    # Extender matriz
    extended = [row[:] + row[:2] for row in A]
    log_sarrus_extended(steps, extended)

    # Extraer entradas
    a11, a12, a13 = A[0]
    a21, a22, a23 = A[1]
    a31, a32, a33 = A[2]

    # Diagonales principales ↘
    triples_pos = [(a11, a22, a33), (a12, a23, a31), (a13, a21, a32)]
    d_pos_vals = [x*y*z for (x,y,z) in triples_pos]
    pos_sum = sum(d_pos_vals)
    log_sarrus_diag(steps, "principal", triples_pos, pos_sum)

    # Diagonales secundarias ↙
    triples_neg = [(a13, a22, a31), (a11, a23, a32), (a12, a21, a33)]
    d_neg_vals = [x*y*z for (x,y,z) in triples_neg]
    neg_sum = sum(d_neg_vals)
    log_sarrus_diag(steps, "secundaria", triples_neg, neg_sum)

    det = pos_sum - neg_sum
    log_det_result(steps, det, method_name, pos_sum, neg_sum)

    return det, steps



def determinant_cofactors(A: List[List[float]]) -> Tuple[float, DetSteps]:
    _check_square(A)
    n = shape(A)[0]
    steps = det_steps_init()
    method_name = "Cofactores"
    log_det_init(steps, A, method_name)

    # Recursivo (detallamos solo: nivel superior + 2×2)
    def _det_cof(M: List[List[float]], level: int) -> float:
        size = shape(M)[0]
        if size == 1:
            return M[0][0]
        if size == 2:
            a, b = M[0][0], M[0][1]
            c, d = M[1][0], M[1][1]
            det2 = a*d - b*c
            # Solo log si no estamos en la raíz (para no repetir demasiado):
            log_subdet_2x2(steps, M, det2)
            return det2
        # nivel > 2: sin logs internos (evitar explosión), solo cálculo
        total = 0.0
        for j in range(size):
            sub = [[M[i][k] for k in range(size) if k != j] for i in range(1, size)]
            sub_det = _det_cof(sub, level+1)
            total += ((-1)**j) * M[0][j] * sub_det
        return total

    total = 0.0
    # expandimos por primera fila con logs de menores y cofactores
    for j in range(n):
        a1j = A[0][j]
        sign = 1 if (j % 2 == 0) else -1
        M1j = [[A[i][k] for k in range(n) if k != j] for i in range(1, n)]

        log_cofactor_minor(steps, j, M1j)  # mostrar submatriz
        sub_det = _det_cof(M1j, level=1)
        cofactor = sign * a1j * sub_det
        total += cofactor
        log_cofactor_value(steps, j, sign, a1j, sub_det, cofactor)

    log_det_result(steps, total, method_name)
    return total, steps


def determinant_cramer(A: Matrix) -> Tuple[float, List[str]]:
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