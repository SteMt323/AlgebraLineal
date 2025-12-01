from __future__ import annotations
import math
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from sympy import (
    lambdify, 
    latex as sympy_latex, 
    Expr, 
    Symbol,
    )

@dataclass
class FalsePositionIterationRow:
    iteration: int
    xl: float
    xu: float
    xr: float
    ea: float
    yl: float
    yu: float
    yr: float
    ea_lt_tol: bool

def false_position_method(
    expr: Expr,
    x_symbol: Symbol,
    xi: float,
    xu: float,
    tol: float,
    max_iter: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Implementación del método de la falsa posición (regula falsi).

    Devuelve un diccionario con cuatro secciones:
    - iterations_estimate: análisis del error relativo porcentual (Ea)
    - table: datos numéricos por iteración (para tabla)
    - details: pasos detallados en LaTeX por iteración
    - conclusion: interpretación final del resultado
    """
    f = lambdify(x_symbol, expr, "math")

    if max_iter is None:
        max_iter = 100  # límite de seguridad

    iteration_rows: List[FalsePositionIterationRow] = []
    iterations_detail: List[Dict[str, Any]] = []

    xl = xi
    xu_current = xu
    xr_prev: Optional[float] = None
    xr: Optional[float] = None

    for k in range(1, max_iter + 1):
        # Valores de la función en los extremos
        yl = float(f(xl))
        yu = float(f(xu_current))

        # Fórmula de falsa posición:
        # xr = xu - f(xu)*(xl - xu)/(f(xl) - f(xu))
        denominator = (yl - yu)
        if denominator == 0:
            raise ZeroDivisionError(
                "Durante el método de falsa posición se obtuvo f(x_l) = f(x_u), "
                "lo que produce una división entre cero en la fórmula de x_r."
            )

        xr = xu_current - yu * (xl - xu_current) / denominator
        yr = float(f(xr))

        # Error relativo porcentual
        if xr_prev is None:
            ea = 0.0
        else:
            ea = abs((xr - xr_prev) / xr) * 100.0 if xr != 0 else 0.0

        ea_lt_tol = ea < tol if xr_prev is not None else False

        # Guardar fila de tabla
        iteration_rows.append(
            FalsePositionIterationRow(
                iteration=k,
                xl=xl,
                xu=xu_current,
                xr=xr,
                ea=ea,
                yl=yl,
                yu=yu,
                yr=yr,
                ea_lt_tol=ea_lt_tol,
            )
        )

        # Guardar detalle LaTeX por iteración
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

        # Criterio de paro principal: Ea < tolerancia (a partir de la 2ª iteración)
        if xr_prev is not None and ea_lt_tol:
            break

        # Actualizar intervalo según el signo
        # a) si f(xl) f(xr) < 0 → la raíz está en [xl, xr] → xu = xr
        # b) si f(xl) f(xr) > 0 → la raíz está en [xr, xu] → xl = xr
        prod = yl * yr
        if prod < 0:
            xu_current = xr
        elif prod > 0:
            xl = xr
        else:
            # f(xr) = 0 (raízn exacta)
            xr_prev = xr
            break

        xr_prev = xr

    if xr is None:
        raise RuntimeError("El método de falsa posición no produjo ninguna iteración.")

    root = xr
    total_iters = len(iteration_rows)
    last_ea = iteration_rows[-1].ea

    # ---------- 1 parte: "iterations_estimate" = análisis del error ----------
    # Aquí no hay fórmula de n, así que devolvemos la fórmula general de Ea
    # y la evaluación numérica de la última iteración.
    iters_section = {
        "latex": {
            "formula_general": (
                r"E_a = \left|\frac{x_r^{(k)} - x_r^{(k-1)}}{x_r^{(k)}}\right|\cdot 100"
            ),
            "formula_substitution": (
                rf"E_a = \left|\frac{{x_r^{{({total_iters})}} - "
                rf"x_r^{{({total_iters-1})}}}}{{x_r^{{({total_iters})}}}}\right|\cdot 100"
                if total_iters > 1
                else r"E_a = 0"
            ),
            "formula_numeric": rf"E_a \approx {last_ea:.4f}\%",
            # Por compatibilidad con el front: usamos n_min como número real de iteraciones
            "n_min": total_iters,
        },
        "numeric": {
            "tolerance": tol,
            "last_error": last_ea,
            "iterations": total_iters,
        },
    }

    # ---------- 2 parte: tabla ----------
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
            "Ea_lt_E": row.ea_lt_tol,
        }
        for row in iteration_rows
    ]

    # ---------- 3 parte: detalles ----------
    details_section = iterations_detail

    # ---------- 4 parte: conclusión ----------
    conclusion_section = {
        "latex": (
            rf"\text{{El método de falsa posición converge en }} {total_iters} "
            rf"\text{{ iteraciones. La raíz aproximada es }} "
            rf"x_r = {root:.6f}."
        ),
        "root": root,
        "iterations": total_iters,
        "stopping_criterion": "E_a < tolerancia (error relativo porcentual)",
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
    Construye la lista de líneas LaTeX que explican la iteración k
    """
    f_latex = sympy_latex(expr)
    lines: List[str] = []

    # Título de la iteración
    lines.append(rf"\textbf{{Iteración {k}:}}")

    # Intervalo
    lines.append(rf"x_l = x_i = {xl:.4f}\quad x_u = {xu:.4f}")

    # Fórmula de falsa posición
    # x_r = x_u - f(x_u)(x_l - x_u)/(f(x_l) - f(x_u))
    lines.append(
        r"x_r = x_u - f(x_u)\frac{x_l - x_u}{f(x_l) - f(x_u)}"
        rf" \Rightarrow x_r = {xu:.4f} - {yu:+.6f}"
        rf"\frac{{{xl:.4f} - {xu:.4f}}}{{{yl:+.6f} - {yu:+.6f}}}"
        rf" = {xr:.4f}"
    )

    # Error relativo Ea
    if is_first:
        lines.append(r"E_a = 0.0000")
    else:
        lines.append(
            r"E_a = \left|\frac{x_r^{(k)} - x_r^{(k-1)}}{x_r^{(k)}}\right|\cdot 100"
            rf" = {ea:.4f}\%"
        )

    # Evaluaciones de la función
    lines.append(
        rf"v_l = f(x_l) = f({xl:.4f}) = {f_latex}\big|_{{x={xl:.4f}}} = {yl:+.6f}"
    )
    lines.append(
        rf"v_u = f(x_u) = f({xu:.4f}) = {f_latex}\big|_{{x={xu:.4f}}} = {yu:+.6f}"
    )
    lines.append(
        rf"v_r = f(x_r) = f({xr:.4f}) = {f_latex}\big|_{{x={xr:.4f}}} = {yr:+.6f}"
    )

    # Decisión de subintervalo
    prod = yl * yr
    if prod < 0:
        lines.append(
            rf"f(x_l) f(x_r) = ({yl:+.4f})({yr:+.4f}) < 0 "
            r"\Rightarrow \text{la raíz está en el subintervalo inferior }[x_l, x_r]."
        )
        lines.append(
            rf"\text{{Nuevo intervalo: }}[x_l, x_u] \leftarrow [{xl:.4f}, {xr:.4f}]"
        )
    elif prod > 0:
        lines.append(
            rf"f(x_l) f(x_r) = ({yl:+.4f})({yr:+.4f}) > 0 "
            r"\Rightarrow \text{la raíz está en el subintervalo superior }[x_r, x_u]."
        )
        lines.append(
            rf"\text{{Nuevo intervalo: }}[x_l, x_u] \leftarrow [{xr:.4f}, {xu:.4f}]"
        )
    else:
        lines.append(
            r"f(x_l) f(x_r) = 0 \Rightarrow \text{se encontró la raíz exactamente en }x_r."
        )

    return lines