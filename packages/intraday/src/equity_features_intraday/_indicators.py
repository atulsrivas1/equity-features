"""Ordered snapshot recurrences; exact seeds and an explicit local precision policy."""
from decimal import (
    Context, Decimal, DecimalException, localcontext, ROUND_HALF_EVEN,
    InvalidOperation, DivisionByZero, Overflow, Underflow, Subnormal, Clamped, FloatOperation,
)
from fractions import Fraction
from math import isfinite

from equity_feature_contracts import ErrorCode
from ._context import fail


def decimal_fraction(value: Fraction) -> Decimal:
    return Decimal(value.numerator) / Decimal(value.denominator)


def indicator(feature: str, values: tuple[Fraction, ...], period: int) -> float:
    """Caller has established the selected operand's readiness and seed length."""
    context = Context(prec=120, rounding=ROUND_HALF_EVEN, Emin=-999999, Emax=999999,
                      capitals=1, clamp=0, traps=[InvalidOperation, DivisionByZero, Overflow,
                      Underflow, Subnormal, Clamped, FloatOperation])
    context.clear_flags()
    try:
        with localcontext(context):
            if feature == "intraday.rsi":
                changes = tuple(b-a for a, b in zip(values, values[1:]))
                gains = tuple(max(change, Fraction()) for change in changes)
                losses = tuple(max(-change, Fraction()) for change in changes)
                gain = decimal_fraction(sum(gains[:period], Fraction()) / period)
                loss = decimal_fraction(sum(losses[:period], Fraction()) / period)
                for up, down in zip(gains[period:], losses[period:]):
                    gain = ((period-1)*gain + decimal_fraction(up)) / period
                    loss = ((period-1)*loss + decimal_fraction(down)) / period
                result = Decimal(50) if gain == loss == 0 else 100*gain/(gain+loss)
            else:
                result = decimal_fraction(sum(values[:period], Fraction()) / period)
                for value in values[period:]:
                    current = decimal_fraction(value)
                    result = ((2*current + (period-1)*result)/(period+1)
                              if feature == "intraday.ema" else
                              ((period-1)*result + current)/period)
            converted = float(result)
            if not isfinite(converted):
                fail("nonfinite indicator conversion", ErrorCode.OVERFLOW)
            return 0.0 if result == 0 else converted
    except (DecimalException, OverflowError, ValueError):
        fail("indicator arithmetic outside declared numeric policy", ErrorCode.OVERFLOW)
