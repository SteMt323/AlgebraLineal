import math 
from dataclasses import dataclass

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

def bisection_method(expr, x_symbol, xi, xu, tol, max_iter=None):
    from sympy import lambdify, latex

    f = lambdify(x_symbol, expr, "math")

    # ---------- 1) Cálculo aproximado de número de iteraciones ----------
    interval_length0 = xu - xi
    n_est = math.log2(interval_length0 / tol)
    n_min = math.ceil(n_est)

    if max_iter is None:
        max_iter = n_min

    iteration_rows = []
    iterations_detail = []

    xr_prev = None
    a = xi
    b = xu

    for k in range(1, max_iter + 1):
        xl = a
        xu = b
        xr = 0.5 * (xl + xu)

        yl = float(f(xl))
        yu = float(f(xu))
        yr = float(f(xr))

        if xr_prev is None:
            ea = 0.0
        else:
            ea = abs((xr - xr_prev) / xr) * 100.0

        interval_length = xu - xl

        # ---------- fila de la tabla ----------
        iteration_rows.append(
            BisectionIterationRow(
                iteration=k,
                xl=xl, xu=xu, xr=xr,
                ea=ea,
                yl=yl, yu=yu, yr=yr,
                interval_length=interval_length,
            )
        )

        # ---------- detalle en LaTeX de esta iteración ----------
        detail_latex = _build_iteration_latex(
            k, expr, xl, xu, xr, yl, yu, yr, ea, xr_prev is None
        )
        iterations_detail.append(detail_latex)

        # criterio de paro por longitud del intervalo
        if interval_length < tol:
            break

        # test de cambio de signo para actualizar [a,b]
        if yl * yr < 0:
            # raíz en [xl, xr]
            b = xr
        else:
            # raíz en [xr, xu]
            a = xr

        xr_prev = xr

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
    # iterations_detail ya viene como lista de strings LaTeX
    details_section = iterations_detail

    # ---------- 4ª parte: interpretación final ----------
    conclusion_section = {
        "latex": (
            rf"\text{{El método converge en }} {total_iters} "
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


def _build_iteration_latex(k, expr, xl, xu, xr, yl, yu, yr, ea, is_first):
    """Construye el bloque de texto LaTeX para una iteración."""
    from sympy import latex as sympy_latex

    f_latex = sympy_latex(expr)
    lines = []

    # OJO: llaves de LaTeX → {{ }}
    lines.append(rf"\textbf{{Iteración {k}:}}")
    lines.append(rf"x_l = {xl:.4f},\quad x_u = {xu:.4f}")
    lines.append(
        rf"x_r = \frac{{x_l + x_u}}{{2}} \Rightarrow "
        rf"x_r = \frac{{{xl:.4f} + {xu:.4f}}}{{2}} = {xr:.4f}"
    )

    if is_first:
        lines.append(r"E_a = 0.0000")
    else:
        lines.append(
            r"E_a = \left|\frac{x_r^{(k)} - x_r^{(k-1)}}{x_r^{(k)}}\right|\cdot 100"
            rf" = {ea:.4f}\%"
        )

    lines.append(
        rf"v_l = f(x_l) = f({xl:.4f}) = {f_latex}\big|_{{x={xl:.4f}}} = {yl:+.6f}"
    )
    lines.append(
        rf"v_u = f(x_u) = f({xu:.4f}) = {f_latex}\big|_{{x={xu:.4f}}} = {yu:+.6f}"
    )
    lines.append(
        rf"v_r = f(x_r) = f({xr:.4f}) = {f_latex}\big|_{{x={xr:.4f}}} = {yr:+.6f}"
    )

    if yl * yr < 0:
        lines.append(
            rf"f(x_l) f(x_r) = ({yl:+.4f})({yr:+.4f}) < 0 "
            r"\Rightarrow \text{{la raíz está entre }}[x_l, x_r]."
        )
        lines.append(
            rf"\text{{Nuevo intervalo: }}[x_l, x_u] \leftarrow [{xl:.4f}, {xr:.4f}]"
        )
    else:
        lines.append(
            rf"f(x_l) f(x_r) = ({yl:+.4f})({yr:+.4f}) > 0 "
            r"\Rightarrow \text{{la raíz está entre }}[x_r, x_u]."
        )
        lines.append(
            rf"\text{{Nuevo intervalo: }}[x_l, x_u] \leftarrow [{xr:.4f}, {xu:.4f}]"
        )

    # Un bloque tipo "Iteración k: ..." que luego renderizas con KaTeX
    return r"\\[4pt]".join(lines)
