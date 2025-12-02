# algebra/algorithms/newton_raphson.py

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from sympy import Expr, Symbol, lambdify, diff, latex as sympy_latex


@dataclass
class NewtonIterationRow:
    iteration: int
    xk: float
    fxk: float
    fprimexk: float
    x_next: float
    Ea: float          # error aproximado absoluto
    Ea_lt_tol: bool    # Ea < tolerancia


def newton_raphson_method(
    expr: Expr,
    x_symbol: Symbol,
    x0: float,
    tol: float,
    max_iter: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Método de Newton–Raphson para encontrar raíces de f(x) = 0.

    Estructura de salida:
    - iterations_estimate: info sobre la fórmula de Newton y el error
    - table: filas numéricas por iteración
    - details: explicación LaTeX de cada iteración
    - conclusion: interpretación final
    """

    if max_iter is None:
        max_iter = 50

    # Derivada simbólica
    fprime_expr = diff(expr, x_symbol)
    if fprime_expr == 0:
        raise ValueError(
            "La derivada simbólica de la función es cero. "
            "Newton–Raphson no es aplicable a una función constante."
        )

    # Funciones numéricas
    f = lambdify(x_symbol, expr, "math")
    fprime = lambdify(x_symbol, fprime_expr, "math")

    iteration_rows: List[NewtonIterationRow] = []
    iterations_detail: List[Dict[str, Any]] = []

    xk = float(x0)
    x_prev: Optional[float] = None
    Ea: float = 0.0

    for k in range(1, max_iter + 1):
        fxk = float(f(xk))
        fpxk = float(fprime(xk))

        if fpxk == 0:
            raise ZeroDivisionError(
                f"En la iteración {k} se obtuvo f'(x_k) = 0, "
                "lo que produce una división entre cero en la fórmula de Newton–Raphson."
            )

        x_next = xk - fxk / fpxk

        if x_prev is None:
            Ea = 0.0
            Ea_lt_tol = False
        else:
            Ea = abs(x_next - xk)
            Ea_lt_tol = Ea < tol

        # Guardar fila de tabla
        iteration_rows.append(
            NewtonIterationRow(
                iteration=k,
                xk=xk,
                fxk=fxk,
                fprimexk=fpxk,
                x_next=x_next,
                Ea=Ea,
                Ea_lt_tol=Ea_lt_tol,
            )
        )

        # Guardar detalle LaTeX
        detail_lines = _build_iteration_latex_lines(
            k,
            expr,
            fprime_expr,
            xk,
            fxk,
            fpxk,
            x_next,
            Ea,
            is_first=(x_prev is None),
            tol=tol,
        )
        iterations_detail.append(
            {
                "iteration": k,
                "lines": detail_lines,
            }
        )

        if Ea_lt_tol and x_prev is not None:
            # criterio de paro: error aproximado absoluto menor a la tolerancia
            break

        x_prev = xk
        xk = x_next

    # Si por alguna razón no hubo iteraciones
    if not iteration_rows:
        raise RuntimeError("El método de Newton–Raphson no produjo ninguna iteración.")

    last_row = iteration_rows[-1]
    root = last_row.x_next
    total_iters = len(iteration_rows)
    last_error = last_row.Ea

    # ---------- 1ª parte: iterations_estimate ----------
    if total_iters > 1:
        xk_last = iteration_rows[-1].x_next
        xk_prev = iteration_rows[-2].x_next
        formula_error_sub = (
            rf"E_a = \left|{xk_last:.6f} - {xk_prev:.6f}\right| = {last_error:.6f}"
        )
    else:
        formula_error_sub = r"E_a = 0"

    iters_section = {
        "latex": {
            "formula_newton": (
                r"x_{k+1} = x_k - \frac{f(x_k)}{f'(x_k)}"
            ),
            "formula_error_general": (
                r"E_a = |x_k - x_{k-1}|"
            ),
            "formula_error_substitution": formula_error_sub,
            "formula_error_numeric": rf"E_a \approx {last_error:.6f}",
            "iterations": total_iters,
        },
        "numeric": {
            "tolerance": tol,
            "last_error": last_error,
            "iterations": total_iters,
        },
    }

    # ---------- 2ª parte: tabla ----------
    table_section = [
        {
            "iteration": row.iteration,
            "xk": row.xk,
            "fxk": row.fxk,
            "fprimexk": row.fprimexk,
            "x_next": row.x_next,
            "Ea": row.Ea,
            "Ea_lt_E": row.Ea_lt_tol,
        }
        for row in iteration_rows
    ]

    # ---------- 3ª parte: detalles ----------
    details_section = iterations_detail

    # ---------- 4ª parte: conclusión ----------
    conclusion_section = {
        "latex": (
            rf"\text{{El método de Newton-Raphson converge en }} {total_iters} "
            rf"\text{{ iteraciones. La raíz aproximada es }} "
            rf"x \approx {root:.6f}."
        ),
        "root": root,
        "iterations": total_iters,
        "stopping_criterion": "E_a < tolerancia (error aproximado absoluto)",
    }

    return {
        "iterations_estimate": iters_section,
        "table": table_section,
        "details": details_section,
        "conclusion": conclusion_section,
    }


def _build_iteration_latex_lines(
    k: int,
    expr: Expr,
    fprime_expr: Expr,
    xk: float,
    fxk: float,
    fpxk: float,
    x_next: float,
    Ea: float,
    is_first: bool,
    tol: float,
) -> List[str]:
    """
    Construye la lista de líneas LaTeX explicando la iteración k.
    """
    f_latex = sympy_latex(expr)
    fprime_latex = sympy_latex(fprime_expr)

    lines: List[str] = []

    lines.append(rf"\textbf{{Iteración {k}:}}")

    # Valor actual x_k
    lines.append(rf"x_{{{k-1}}} = {xk:.6f}" if k > 1 else rf"x_0 = {xk:.6f}")

    # f(x_k)
    lines.append(
        rf"f(x_{{{k-1 if k>1 else 0}}}) = f({xk:.6f}) = "
        rf"{f_latex}\big|_{{x={xk:.6f}}} = {fxk:+.6f}"
    )

    # f'(x_k)
    lines.append(
        rf"f'(x_{{{k-1 if k>1 else 0}}}) = f'({xk:.6f}) = "
        rf"{fprime_latex}\big|_{{x={xk:.6f}}} = {fpxk:+.6f}"
    )

    # Fórmula de Newton
    if k == 1:
        idx = 1
        prev_idx = 0
    else:
        idx = k
        prev_idx = k - 1

    lines.append(
        rf"x_{{{idx}}} = x_{{{prev_idx}}} - "
        rf"\frac{{f(x_{{{prev_idx}}})}}{{f'(x_{{{prev_idx}}})}}"
        rf" = {xk:.6f} - \frac{{{fxk:+.6f}}}{{{fpxk:+.6f}}}"
        rf" = {x_next:.6f}"
    )

    # Error aproximado
    if is_first:
        lines.append(r"E_a = |x_1 - x_0| = 0")
    else:
        lines.append(
            rf"E_a = |x_{{{idx}}} - x_{{{prev_idx}}}|"
            rf" = |{x_next:.6f} - {xk:.6f}| = {Ea:.6f}"
        )
        if Ea < tol:
            lines.append(
                rf"E_a = {Ea:.6f} < E = {tol:.6f}"
                r" \Rightarrow \text{se cumple el criterio de paro.}"
            )
        else:
            lines.append(
                rf"E_a = {Ea:.6f} > E = {tol:.6f}"
                r" \Rightarrow \text{se requiere otra iteración.}"
            )

    return lines
