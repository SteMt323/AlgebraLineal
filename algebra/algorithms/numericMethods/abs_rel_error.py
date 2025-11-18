# algebra/algorithms/abs_rel_error.py
from decimal import Decimal, getcontext, ROUND_HALF_UP
from typing import Dict, Any, Optional

getcontext().prec = 28

def _fmt(d: Decimal, decimals: int) -> str:
    """Formato fijo con separador de miles opcional. Devuelve string."""
    fmt = f"{{:,.{decimals}f}}"
    return fmt.format(d)

def compute_abs_rel_error(
    *,
    true_value: Decimal,
    approx_value: Decimal,
    decimals_display: int = 6
) -> Dict[str, Any]:
    m: Decimal = true_value
    m_tilde: Decimal = approx_value
    # Error absoluto
    ea: Decimal = m - m_tilde

    # Preparar absolute_error según estructura solicitada
    absolute_error = {
        "operation": {
            "numerator": "m - m~"
        },
        "formula": {
            "numerator": f"{_fmt(m, decimals_display)} - {_fmt(m_tilde, decimals_display)}"
        },
        "result": _fmt(ea, decimals_display)
    }
    if m == Decimal("0"):
        relative_error = {
            "operation": {
                "numerator": "m - m~",
                "denominator": "m"
            },
            "formula": {
                "numerator": f"{_fmt(m, decimals_display)} - {_fmt(m_tilde, decimals_display)}",
                "denominator": _fmt(m, decimals_display)
            },
            "result": None,
            "note": "Undefined: true value m == 0 (division by zero)"
        }
    else:
        er: Decimal = (ea / m).quantize(Decimal(1).scaleb(-decimals_display), rounding=ROUND_HALF_UP)
        relative_error = {
            "operation": {
                "numerator": "m - m~",
                "denominator": "m"
            },
            "formula": {
                "numerator": f"{_fmt(m, decimals_display)} - {_fmt(m_tilde, decimals_display)}",
                "denominator": _fmt(m, decimals_display)
            },
            "result": _fmt(er, decimals_display)
        }

    out = {
        "input": {
            "true_value_pretty": _fmt(m, decimals_display),
            "approx_value_pretty": _fmt(m_tilde, decimals_display)
        },
        "absolute_error": absolute_error,
        "relative_error": relative_error
    }
    return out
