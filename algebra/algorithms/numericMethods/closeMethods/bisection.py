from __future__ import annotations
import math
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from sympy import lambdify, latex as sympy_latex, Expr, Symbol


@dataclass
class BisectionIterationRow:
    iteration: int
    xl: float
    xu: float
    xr: float
    ea: float           # error relativo porcentual
    yl: float
    yu: float
    yr: float
    interval_length: float


def bisection_method(
    expr: Expr,
    x_symbol: Symbol,
    xi: float,
    xu: float,
    tol: float,
    max_iter: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Implementación del método de la bisección.

    Devuelve un diccionario con cuatro secciones:
    - iterations_estimate: cálculo aproximado de número de iteraciones necesarias
    - table: datos numéricos por iteración (para tabla)
    - details: pasos detallados en LaTeX por iteración
    - conclusion: interpretación final del resultado
    """
    # ---------- Preparar función numérica ----------
    f = lambdify(x_symbol, expr, "math")

    # ---------- 1) Estimación de número de iteraciones ----------
    interval_length0 = xu - xi
    # Evitar log de número no positivo
    if interval_length0 <= 0 or tol <= 0:
        # Esto debería estar validado en el serializer, pero por seguridad:
        raise ValueError("Intervalo o tolerancia inválidos para bisección.")

    n_est = math.log2(interval_length0 / tol)
    n_min = max(1, math.ceil(n_est))

    if max_iter is None:
        max_iter = n_min

    iteration_rows: List[BisectionIterationRow] = []
    iterations_detail: List[Dict[str, Any]] = []

    xr_prev: Optional[float] = None
    a = xi
    b = xu
    xr: Optional[float] = None

    for k in range(1, max_iter + 1):
        xl = a
        xu_current = b
        xr = 0.5 * (xl + xu_current)

        yl = float(f(xl))
        yu = float(f(xu_current))
        yr = float(f(xr))

        if xr_prev is None:
            ea = 0.0
        else:
            # error relativo porcentual
            ea = abs((xr - xr_prev) / xr) * 100.0 if xr != 0 else 0.0

        interval_length = xu_current - xl

        # ---------- fila de la tabla ----------
        iteration_rows.append(
            BisectionIterationRow(
                iteration=k,
                xl=xl,
                xu=xu_current,
                xr=xr,
                ea=ea,
                yl=yl,
                yu=yu,
                yr=yr,
                interval_length=interval_length,
            )
        )

        # ---------- detalle LaTeX por iteración ----------
        detail_lines = _build_iteration_latex_lines(
            k,
            expr,
            xl,
            xu_current,
            xr,
            yl,
            yu,
            yr,
            ea,
            is_first=(xr_prev is None),
        )
        iterations_detail.append(
            {
                "iteration": k,
                "lines": detail_lines,
            }
        )

        # Criterio de paro por longitud del intervalo
        if interval_length < tol:
            break

        # Actualizar intervalo según el cambio de signo
        if yl * yr < 0:
            # raíz en [xl, xr]
            b = xr
        else:
            # raíz en [xr, xu]
            a = xr

        xr_prev = xr

    # Si por alguna razón no hubo iteraciones
    if xr is None:
        raise RuntimeError("El método de bisección no produjo ninguna iteración.")

    root = xr
    total_iters = len(iteration_rows)

    # ---------- 1ª parte: iteraciones necesarias ----------
    iters_section = {
        "latex": {
            "formula_general": r"n \ge \log_{2}\!\left(\frac{b-a}{E}\right)",
            "formula_substitution": (
                rf"n \ge \log_2\left(\frac{{{interval_length0:.4f}}}{{{tol:.4g}}}\right)"
            ),
            "formula_numeric": rf"n \ge {n_est:.4f}",
            "n_min": n_min,
        },
        "numeric": {
            "interval_length": interval_length0,
            "tolerance": tol,
            "estimate": n_est,
            "n_min": n_min,
        },
    }

    # ---------- 2ª parte: tabla de iteraciones ----------
    table_section = [
        {
            "iteration": row.iteration,
            "xl": row.xl,
            "xu": row.xu,
            "xr": row.xr,
            "Ea": row.ea,
            "yl": row.yl,
            "yu": row.yu,
            "yr": row.yr,
            "interval_length": row.interval_length,
        }
        for row in iteration_rows
    ]

    # ---------- 3ª parte: detalles de cada iteración ----------
    details_section = iterations_detail

    # ---------- 4ª parte: interpretación final ----------
    conclusion_section = {
        "latex": (
            rf"\text{{El método de bisección converge en }} {total_iters} "
            rf"\text{{ iteraciones. La raíz aproximada es }} "
            rf"x_r = {root:.6f}."
        ),
        "root": root,
        "iterations": total_iters,
        "stopping_criterion": "longitud_intervalo < tolerancia",
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
    xl: float,
    xu: float,
    xr: float,
    yl: float,
    yu: float,
    yr: float,
    ea: float,
    is_first: bool,
) -> List[str]:
    """
    Construye una lista de líneas LaTeX que explican la iteración k.

    Cada string de la lista está pensado para ser renderizado individualmente
    en el frontend con KaTeX/MathJax (por ejemplo, un <BlockMath /> por línea).
    """
    f_latex = sympy_latex(expr)
    lines: List[str] = []

    # OJO: llaves de LaTeX → {{ }} en f-strings
    lines.append(rf"\textbf{{Iteración {k}:}}")

    # Intervalo actual
    lines.append(rf"x_l = {xl:.4f},\quad x_u = {xu:.4f}")

    # Cálculo de xr
    lines.append(
        rf"x_r = \frac{{x_l + x_u}}{{2}} \Rightarrow x_r = "
        rf"\frac{{{xl:.4f} + {xu:.4f}}}{{2}} = {xr:.4f}"
    )

    # Error relativo
    if is_first:
        lines.append(r"E_a = 0.0000")
    else:
        lines.append(
            r"E_a = \left|\frac{x_r^{(k)} - x_r^{(k-1)}}{x_r^{(k)}}\right|\cdot 100"
            rf" = {ea:.4f}\%"
        )

    # Evaluaciones de f(x)
    lines.append(
        rf"v_l = f(x_l) = f({xl:.4f}) = {f_latex}\big|_{{x={xl:.4f}}} = {yl:+.6f}"
    )
    lines.append(
        rf"v_u = f(x_u) = f({xu:.4f}) = {f_latex}\big|_{{x={xu:.4f}}} = {yu:+.6f}"
    )
    lines.append(
        rf"v_r = f(x_r) = f({xr:.4f}) = {f_latex}\big|_{{x={xr:.4f}}} = {yr:+.6f}"
    )

    # Decisión del nuevo intervalo
    if yl * yr < 0:
        lines.append(
            rf"f(x_l) f(x_r) = ({yl:+.4f})({yr:+.4f}) < 0 "
            r"\Rightarrow \text{la raíz está entre }[x_l, x_r]."
        )
        lines.append(
            rf"\text{{Nuevo intervalo: }}[x_l, x_u] \leftarrow [{xl:.4f}, {xr:.4f}]"
        )
    else:
        lines.append(
            rf"f(x_l) f(x_r) = ({yl:+.4f})({yr:+.4f}) > 0 "
            r"\Rightarrow \text{la raíz está entre }[x_r, x_u]."
        )
        lines.append(
            rf"\text{{Nuevo intervalo: }}[x_l, x_u] \leftarrow [{xr:.4f}, {xu:.4f}]"
        )

    return lines
