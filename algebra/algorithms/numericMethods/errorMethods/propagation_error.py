from __future__ import annotations 
from typing import Any, Dict

from decimal import Decimal, getcontext, ROUND_HALF_UP
from math import pi 
from sympy import Symbol, lambdify
from sympy.parsing.latex import parse_latex
from sympy import latex as sympy_latex
import numpy

getcontext().prec = 28
x_sym = Symbol('x')

def _to_decimal(v: float, decimals: int = 6) -> str:
    q = Decimal(1).scaleb(-decimals)
    d = Decimal(v).quantize(q, rounding=ROUND_HALF_UP)
    fmt = f"{{:.{decimals}f}}"
    return fmt.format(d)

def propagation_error_api(*, function_latex: str, x0: float, delta_x: float, angle_mode: str = "rad", decimals: int = 4,) -> Dict[str, Any]:
    # Parsear f(x) desde la entrada latex
    expr= parse_latex(function_latex)
    d_expr = expr.diff(x_sym)

    f_num = lambdify(x_sym, expr, "numpy")
    df_num = lambdify(x_sym, d_expr, "numpy")

    x0_val = float(x0)
    dx_val = float(delta_x)

    if angle_mode == "deg":
        x0_val = x0_val * pi / 100.0
        dx_val = dx_val * pi / 100.0
    else:
        x0_eval = x0_val
        dx_eval = dx_val

    f_x0 = float(f_num(x0_eval))
    f_x0_dx = float(f_num(x0_eval + dx_eval))
    df_x0 = float(df_num(x0_eval))

    dy_aprox = df_x0 * dx_eval
    dy_real = f_x0_dx - f_x0
    error_abs = abs(dy_real - dy_aprox)

    # Representaciones en LaTeX
    f_tex = function_latex                
    df_tex = sympy_latex(d_expr)               

    x0_str = _to_decimal(x0_val, decimals)
    dx_str = _to_decimal(dx_val, decimals)
    df_x0_str = _to_decimal(df_x0, decimals)
    f_x0_str = _to_decimal(f_x0, decimals)
    f_x0dx_str = _to_decimal(f_x0_dx, decimals)
    dy_aprox_str = _to_decimal(dy_aprox, decimals)
    dy_real_str = _to_decimal(dy_real, decimals)
    err_str = _to_decimal(error_abs, decimals)

    if angle_mode == "deg":
        x_label = f"{x0_str}^\\circ"
        x_plus_dx_label = f"({x0_str} + {dx_str})^\\circ"
    else:
        x_label = x0_str
        x_plus_dx_label = f"{x0_str} + {dx_str}"

    return {
        "input": {
            "function_latex": f_tex,
            "x0": x0_str,
            "delta_x": dx_str,
            "angle_mode": angle_mode,
        },
        "steps": {
            "derivative": {
                "operation": {
                    "expression": r"f'(x) = \frac{d}{dx} f(x)"
                },
                "formula": {
                    "function": f"f(x) = {f_tex}",
                    "derivative": f"f'(x) = {df_tex}",
                    "evaluation": f"f'({x_label}) \\approx {df_x0_str}",
                },
                "result": df_x0_str,
            },
            "approx_delta_y": {
                "operation": {
                    "expression": r"\Delta y_{\text{aprox}} \approx f'(x_0)\,\Delta x"
                },
                "formula": {
                    "expression": (
                        r"\Delta y_{\text{aprox}} \approx "
                        f"{df_x0_str} \cdot {dx_str}"
                    )
                },
                "result": dy_aprox_str,
            },
            "exact_delta_y": {
                "operation": {
                    "expression": r"\Delta y_{\text{real}} = f(x_0 + \Delta x) - f(x_0)"
                },
                "formula": {
                    "expression": (
                        r"\Delta y_{\text{real}} = "
                        f"f({x_plus_dx_label}) - f({x_label}) "
                        f"= {f_x0dx_str} - {f_x0_str}"
                    )
                },
                "result": dy_real_str,
            },
            "absolute_error": {
                "operation": {
                    "expression": r"e_a = |\Delta y_{\text{real}} - \Delta y_{\text{aprox}}|"
                },
                "formula": {
                    "numerator": (
                        f"|{dy_real_str} - {dy_aprox_str}|"
                    )
                },
                "result": err_str,
            },
        },
        "result": {
            "delta_y_approx": dy_aprox_str,
            "delta_y_real": dy_real_str,
            "absolute_error": err_str,
        },
    }