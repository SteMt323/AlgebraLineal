from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from sympy import Expr, Symbol, lambdify, latex as sympy_latex


@dataclass
class SecantIterationRow:
    iteration: int
    x_prev: float
    x_curr: float
    x_next: float
    f_prev: float
    f_curr: float
    f_next: float
    Ea: float          # error aproximado absoluto
    Ea_lt_tol: bool    # Ea < tolerancia


def secant_method(
    expr: Expr,
    x_symbol: Symbol,
    x0: float,
    x1: float,
    tol: float,
    max_iter: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Método de la secante para encontrar raíces de f(x) = 0.

    Devuelve un diccionario con las secciones:
    - iterations_estimate
    - table
    - details
    - conclusion
    """
    if max_iter is None:
        max_iter = 50

    f = lambdify(x_symbol, expr, "math")

    iteration_rows: List[SecantIterationRow] = []
    iterations_detail: List[Dict[str, Any]] = []

    x_prev = float(x0)
    x_curr = float(x1)

    f_prev = float(f(x_prev))
    f_curr = float(f(x_curr))

    # Comprobación inicial de pendiente secante
    den0 = f_curr - f_prev
    if den0 == 0:
        raise ZeroDivisionError(
            "La pendiente secante inicial es cero: f(x1) - f(x0) = 0. "
            "No se puede aplicar el método de la secante con estos valores iniciales."
        )

    Ea: float = 0.0

    for k in range(1, max_iter + 1):
        den = f_curr - f_prev
        if den == 0:
            raise ZeroDivisionError(
                f"En la iteración {k} se obtuvo f(x_k) - f(x_(k-1)) = 0, "
                "lo que produce división entre cero en la fórmula de la secante."
            )

        # Fórmula de la secante:
        # x_next = x_curr - f(x_curr)*(x_curr - x_prev)/(f(x_curr) - f(x_prev))
        x_next = x_curr - f_curr * (x_curr - x_prev) / den
        f_next = float(f(x_next))

        if k == 1:
            Ea = 0.0
            Ea_lt_tol = False
        else:
            Ea = abs(x_next - x_curr)
            Ea_lt_tol = Ea < tol

        # Guardar fila tabla
        iteration_rows.append(
            SecantIterationRow(
                iteration=k,
                x_prev=x_prev,
                x_curr=x_curr,
                x_next=x_next,
                f_prev=f_prev,
                f_curr=f_curr,
                f_next=f_next,
                Ea=Ea,
                Ea_lt_tol=Ea_lt_tol,
            )
        )

        # Detalle LaTeX
        detail_lines = _build_iteration_latex_lines(
            k,
            expr,
            x_prev,
            x_curr,
            x_next,
            f_prev,
            f_curr,
            f_next,
            Ea,
            is_first=(k == 1),
            tol=tol,
        )
        iterations_detail.append(
            {
                "iteration": k,
                "lines": detail_lines,
            }
        )

        # Criterio de paro: Ea < tol a partir de la segunda iteración
        if k > 1 and Ea_lt_tol:
            break

        # Preparar siguiente iteración
        x_prev, x_curr = x_curr, x_next
        f_prev, f_curr = f_curr, f_next

    if not iteration_rows:
        raise RuntimeError("El método de la secante no produjo ninguna iteración.")

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
            "formula_secant": (
                r"x_{k+1} = x_k - f(x_k)\,\dfrac{x_k - x_{k-1}}{f(x_k) - f(x_{k-1})}"
            ),
            "formula_error_general": r"E_a = |x_{k+1} - x_k|",
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
            "x_prev": row.x_prev,
            "x_curr": row.x_curr,
            "x_next": row.x_next,
            "f_prev": row.f_prev,
            "f_curr": row.f_curr,
            "f_next": row.f_next,
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
            rf"\text{{El método de la secante converge en }} {total_iters} "
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
    x_prev: float,
    x_curr: float,
    x_next: float,
    f_prev: float,
    f_curr: float,
    f_next: float,
    Ea: float,
    is_first: bool,
    tol: float,
) -> List[str]:
    """
    Construye la lista de líneas LaTeX explicando la iteración k.
    """
    f_latex = sympy_latex(expr)
    lines: List[str] = []

    # Título
    lines.append(rf"\textbf{{Iteración {k}:}}")

    # x_{k-1}, x_k
    idx_prev = k - 1
    idx_curr = k

    if k == 1:
        # para la primera iteración usamos x_0 y x_1 explícitamente
        lines.append(rf"x_0 = {x_prev:.6f},\quad x_1 = {x_curr:.6f}")
    else:
        lines.append(
            rf"x_{{{idx_prev}}} = {x_prev:.6f},\quad x_{{{idx_curr}}} = {x_curr:.6f}"
        )

    # f(x_{k-1}), f(x_k)
    lines.append(
        rf"f(x_{{{idx_prev}}}) = f({x_prev:.6f}) = "
        rf"{f_latex}\big|_{{x={x_prev:.6f}}} = {f_prev:+.6f}"
    )
    lines.append(
        rf"f(x_{{{idx_curr}}}) = f({x_curr:.6f}) = "
        rf"{f_latex}\big|_{{x={x_curr:.6f}}} = {f_curr:+.6f}"
    )

    # Fórmula de la secante
    idx_next = k + 1
    lines.append(
        rf"x_{{{idx_next}}} = x_{{{idx_curr}}} - "
        rf"f(x_{{{idx_curr}}})\frac{{x_{{{idx_curr}}} - x_{{{idx_prev}}}}}"
        rf"{{f(x_{{{idx_curr}}}) - f(x_{{{idx_prev}}})}}"
    )
    lines.append(
        rf"x_{{{idx_next}}} = {x_curr:.6f} - "
        rf"{f_curr:+.6f}\frac{{{x_curr:.6f} - {x_prev:.6f}}}"
        rf"{{{f_curr:+.6f} - {f_prev:+.6f}}} = {x_next:.6f}"
    )

    # f(x_{k+1})
    lines.append(
        rf"f(x_{{{idx_next}}}) = f({x_next:.6f}) = "
        rf"{f_latex}\big|_{{x={x_next:.6f}}} = {f_next:+.6f}"
    )

    # Error aproximado
    if is_first:
        lines.append(r"E_a = |x_2 - x_1| = 0")
    else:
        lines.append(
            rf"E_a = |x_{{{idx_next}}} - x_{{{idx_curr}}}|"
            rf" = |{x_next:.6f} - {x_curr:.6f}| = {Ea:.6f}"
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
