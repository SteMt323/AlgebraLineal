from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple

from algebra.algorithms.matrix.matrix_operations import (
    add_matrices, sub_matrices, scalar_mult, transpose, matmul,
    sum_many, sub_many, matmul_chain, inverse)

from ..utils import matrix_as_fraction, format_number

Number = float
Matrix = List[List[Number]]


def matrix_ops_api(*, operation: str, A: Optional[Matrix] = None, B: Optional[Matrix] = None,
                   matrices: Optional[List[Matrix]] = None, scalar: Optional[Number] = None,
                   options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    opt = options or {}

    try:
        if operation == 'add':
            C, steps = add_matrices(A, B)
            return {
                'input': {'operation': operation, 'A': A, 'B': B},
                'steps': steps.split('\n') if isinstance(steps, str) else steps,
                'result': {'matrix': C, 'matrix_pretty': matrix_as_fraction(C)}
            }

        if operation == 'sub':
            C, steps = sub_matrices(A, B)
            return {
                'input': {'operation': operation, 'A': A, 'B': B},
                'steps': steps.split('\n') if isinstance(steps, str) else steps,
                'result': {'matrix': C, 'matrix_pretty': matrix_as_fraction(C)}
            }

        if operation == 'scalar':
            C, steps = scalar_mult(scalar, A)
            return {
                'input': {'operation': operation, 'A': A, 'scalar': scalar},
                'steps': steps.split('\n') if isinstance(steps, str) else steps,
                'result': {'matrix': C, 'matrix_pretty': matrix_as_fraction(C)}
            }

        if operation == 'transpose':
            T, steps = transpose(A)
            return {
                'input': {'operation': operation, 'A': A},
                'steps': steps.split('\n') if isinstance(steps, str) else steps,
                'result': {'matrix': T, 'matrix_pretty': matrix_as_fraction(T)}
            }

        if operation == 'matmul':
            C, steps = matmul(A, B)
            return {
                'input': {'operation': operation, 'A': A, 'B': B},
                'steps': steps.split('\n') if isinstance(steps, str) else steps,
                'result': {'matrix': C, 'matrix_pretty': matrix_as_fraction(C)}
            }

        if operation == 'sum_many':
            C, steps = sum_many(matrices)
            return {
                'input': {'operation': operation, 'matrices': matrices},
                'steps': steps.split('\n') if isinstance(steps, str) else steps,
                'result': {'matrix': C, 'matrix_pretty': matrix_as_fraction(C)}
            }

        if operation == 'sub_many':
            C, steps = sub_many(matrices[0], matrices[1:])
            return {
                'input': {'operation': operation, 'matrices': matrices},
                'steps': steps.split('\n') if isinstance(steps, str) else steps,
                'result': {'matrix': C, 'matrix_pretty': matrix_as_fraction(C)}
            }

        if operation == 'matmul_chain':
            C, steps = matmul_chain(matrices)
            return {
                'input': {'operation': operation, 'matrices': matrices},
                'steps': steps.split('\n') if isinstance(steps, str) else steps,
                'result': {'matrix': C, 'matrix_pretty': matrix_as_fraction(C)}
            }

        if operation == 'inverse':
            frame = {}
            Ainv, steps = inverse(A, frame=frame)
            return {
                'input': {'operation': operation, 'A': A},
                'steps': {
                    'frame': frame,
                    'text_steps': steps.split('\n') if isinstance(steps, str) else steps
                },
                'result': {'matrix': Ainv, 'matrix_pretty': matrix_as_fraction(Ainv)}
            }

        raise ValueError('Operación inválida')
    except Exception as e:
        # Uniform error shape similar to other APIs
        return {'error': {'code': 'MATRIX_OP_ERROR', 'message': str(e)}}
