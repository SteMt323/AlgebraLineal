from decimal import Decimal, getcontext, ROUND_DOWN, ROUND_HALF_UP
from typing import Dict, Any, List, Tuple

getcontext().prec = 28  # Set default precision

def _quantize_decimal(d: Decimal, exp_str: str) -> Decimal:
    """Quantize a Decimal to a given exponent string with specified rounding."""
    return d.quantize(Decimal(exp_str))

def trunc_to_decimal(d: Decimal, decimals: int = 2) -> Decimal:
    """Truncate a Decimal to a specified number of decimal places."""
    exp = '1' + ('o' * decimals)
    q = Decimal('1').scaleb(-decimals)
    return d.quantize(q, rounding=ROUND_DOWN)

def round_to_decimal(d: Decimal, decimals: int = 2) -> Decimal:
    q = Decimal('1').scaleb(-decimals)
    return d.quantize(q, rounding=ROUND_HALF_UP)

def _pretty (d: Decimal, decimals: int =  2) -> str:
    fmt = f"{{:,.{decimals}f}}"
    return fmt.format(d)

def accumulate_error_iterations(
    *,
    initial_amount: Decimal,
    iterations: int,
    mode: str = "trunc",
    rate: Decimal = Decimal("0.0625"),
    interest_display_decimals: int = 4,
    approx_decimals: int = 2
) -> Dict[str, Any]:
    if iterations <= 0:
        raise ValueError("Iteraciones deben ser mayores a cero.")
    if mode not in ("trunc", "round"):
        raise ValueError("El modo debe ser truc o round")
    
    rows: List[Dict[str, Any]] = []
    prev = initial_amount
    error_accum = Decimal('0')
    for i in range(1, iterations + 1):
        interest_real = prev * rate

        if mode == "trunc":
            interest_approx = trunc_to_decimal(interest_real, approx_decimals)
            op_text = f"truncar a {approx_decimals} decimales"
        else:
            interest_approx = round_to_decimal(interest_real, approx_decimals)
            op_text = f"redondear a {approx_decimals} decimales"

        amount_real = prev + interest_real
        amount_approx = prev + interest_approx
        diff = amount_real - amount_approx
        error_accum += diff

        row = {
            "iteration": i,

            # montos (numéricos Decimal)
            "prev_amount": prev,
            "interest_real": interest_real,
            "interest_approx": interest_approx,
            "amount_real": amount_real,
            "amount_approx": amount_approx,
            "difference": diff,
            "error_accum": error_accum,

            # pretty strings (listas para UI)
            "prev_amount_pretty": _pretty(prev, approx_decimals),
            "interest_real_pretty": _pretty(_quantize_decimal(interest_real, "1E-{0}".format(interest_display_decimals)), interest_display_decimals),
            "interest_approx_pretty": _pretty(interest_approx, approx_decimals),
            "amount_real_pretty": _pretty(_quantize_decimal(amount_real, "1E-{0}".format(interest_display_decimals)), interest_display_decimals),
            "amount_approx_pretty": _pretty(amount_approx, approx_decimals),
            "difference_pretty": _pretty(diff, approx_decimals),
            "error_accum_pretty": _pretty(error_accum, approx_decimals),

            # meta info
            "approx_mode": mode,
            "approx_operation_text": op_text
        }
        rows.append(row)
        prev = amount_approx


    summary = {
        "iterations": iterations,
        "initial_amout_pretty": _pretty(initial_amount, approx_decimals),
        "final_error_accum_pretty": _pretty(error_accum, approx_decimals),
        "rate": rate,
        "mode": mode
    }

    return {"rows": rows, "summary": summary}