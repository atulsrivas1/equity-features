"""Selected price-band cells from exact moments and unrounded radius witnesses."""
from decimal import (
    Context, Decimal, DecimalException, localcontext, ROUND_HALF_EVEN,
    InvalidOperation, DivisionByZero, Overflow, Underflow, Subnormal, Clamped, FloatOperation,
)
from fractions import Fraction
from math import isfinite

from equity_feature_contracts import ErrorCode
from ._context import fail
from ._indicators import decimal_fraction


BAND_FEATURES = frozenset(f"intraday.band_{name}" for name in
                          ("middle", "upper", "lower", "width_ratio", "position"))


def finite(value: Decimal) -> float:
    converted = float(value)
    if not isfinite(converted):
        fail("nonfinite band conversion", ErrorCode.OVERFLOW)
    return 0.0 if value == 0 else converted


def band_values(values: tuple[Fraction, ...], multiplier: Fraction,
                features: tuple[str, ...]) -> dict[str, float | None]:
    """Caller has established a complete selected rolling-moment operand."""
    mean, variance, residual = values
    if mean <= 0 or variance < 0:
        fail("invalid admitted band moments", ErrorCode.OVERFLOW)
    if not features or any(feature not in BAND_FEATURES for feature in features):
        fail("unknown internal selected band")
    context = Context(prec=120, rounding=ROUND_HALF_EVEN, Emin=-999999, Emax=999999,
                      capitals=1, clamp=0, traps=[InvalidOperation, DivisionByZero, Overflow,
                      Underflow, Subnormal, Clamped, FloatOperation])
    context.clear_flags()
    result: dict[str, float | None] = {}
    try:
        with localcontext(context):
            center = decimal_fraction(mean)
            if variance == 0:
                for feature in features:
                    result[feature] = (None if feature == "intraday.band_position" else
                                       0.0 if feature == "intraday.band_width_ratio" else finite(center))
                return result
            if "intraday.band_middle" in features:
                result["intraday.band_middle"] = finite(center)
            if len(features) == 1 and features[0] == "intraday.band_middle":
                return result
            radius_squared = multiplier * multiplier * variance
            radius = decimal_fraction(radius_squared).sqrt()
            if radius <= 0:
                fail("nonpositive band radius", ErrorCode.OVERFLOW)
            if "intraday.band_upper" in features:
                result["intraday.band_upper"] = finite(center + radius)
            if "intraday.band_lower" in features:
                numerator = mean * mean - radius_squared
                result["intraday.band_lower"] = (0.0 if numerator == 0 else
                    finite(decimal_fraction(numerator) / (center + radius)))
            if "intraday.band_width_ratio" in features:
                result["intraday.band_width_ratio"] = finite(2 * radius / center)
            if "intraday.band_position" in features:
                if residual < 0:
                    numerator = radius_squared - residual * residual
                    position = (Decimal(0) if numerator == 0 else
                        decimal_fraction(numerator) /
                        (2 * radius * (radius - decimal_fraction(residual))))
                else:
                    position = Decimal(1) / 2 + decimal_fraction(residual) / (2 * radius)
                result["intraday.band_position"] = finite(position)
        return result
    except (DecimalException, OverflowError, ValueError):
        fail("band arithmetic outside declared numeric policy", ErrorCode.OVERFLOW)
