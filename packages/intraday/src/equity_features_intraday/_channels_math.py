"""EF2 channel operands and R17 Decimal120 recurrences (ef2-v1): Ichimoku, Keltner, Donchian, pivots, percentile, squeeze.

Exact Fraction/integer arithmetic wherever the contract is rational (one correctly rounded float64 conversion), the R17
Decimal120 recurrences (fresh local context, R17 traps) for the unrounded EMA/ATR chains and the single irrational
square root, and a guarded final conversion with normalized exact zero. Callers have established the readiness of every
operand slot.
"""
from __future__ import annotations

from decimal import (
    Context, Decimal, DecimalException, localcontext, ROUND_HALF_EVEN,
    InvalidOperation, DivisionByZero, Overflow, Underflow, Subnormal, Clamped, FloatOperation,
)
from fractions import Fraction
from math import isfinite
from typing import cast

from equity_feature_contracts import ErrorCode
from ._admission import SlotFacts
from ._context import fail
from ._indicators import decimal_fraction


def _policy() -> Context:
    context = Context(prec=120, rounding=ROUND_HALF_EVEN, Emin=-999999, Emax=999999,
                      capitals=1, clamp=0, traps=[InvalidOperation, DivisionByZero, Overflow,
                      Underflow, Subnormal, Clamped, FloatOperation])
    context.clear_flags()
    return context


def exact_float(value: Fraction) -> float:
    """One correctly rounded (round-half-even) float64 conversion of an exact rational; exact zero is +0.0."""
    converted = float(value)
    if not isfinite(converted):
        fail("nonfinite channel conversion", ErrorCode.OVERFLOW)
    return 0.0 if value == 0 else converted


def decimal_float(value: Decimal) -> float:
    converted = float(value)
    if not isfinite(converted):
        fail("nonfinite channel conversion", ErrorCode.OVERFLOW)
    return 0.0 if value == 0 else converted


# Additive internal operand families (window ends at earlier slots; R17 operands end at the target only).

def rolling_high_at(facts: tuple[SlotFacts, ...], end: int, period: int) -> int:
    """HH in integer coefficients over the `period` governed bars ending at `end`, current bar included."""
    return max(cast(int, f.high) for f in facts[end-period+1:end+1])


def rolling_low_at(facts: tuple[SlotFacts, ...], end: int, period: int) -> int:
    """LL in integer coefficients over the `period` governed bars ending at `end`, current bar included."""
    return min(cast(int, f.low) for f in facts[end-period+1:end+1])


def rolling_extrema_at(facts: tuple[SlotFacts, ...], end: int, period: int) -> tuple[int, int]:
    """(HH, LL) over the `period` bars ending at `end`; the independent sides are read separately by Donchian."""
    return rolling_high_at(facts, end, period), rolling_low_at(facts, end, period)


def midpoint(extrema: tuple[int, int], scale: int) -> Fraction:
    return Fraction(extrema[0] + extrema[1], 2 * 10**scale)


def rolling_moments_at(facts: tuple[SlotFacts, ...], end: int, period: int, scale: int) -> tuple[Fraction, Fraction]:
    """(mean, population variance) of the `period` closes ending at `end`, exactly as the R17 price_moments."""
    window = facts[end-period+1:end+1]
    total = sum(cast(int, f.close) for f in window)
    squares = sum(cast(int, f.close)**2 for f in window)
    numerator = period*squares - total**2
    if total <= 0 or numerator < 0:
        fail("moment arithmetic invariant violated", ErrorCode.OVERFLOW)
    divisor = 10**scale
    return Fraction(total, period*divisor), Fraction(numerator, period**2*divisor**2)


def width_keys(facts: tuple[SlotFacts, ...], first: int, last: int, period: int) -> list[tuple[int, int]]:
    """Exact squared band-width keys (N*sum(c^2) - sum(c)^2, sum(c)^2) for the windows ending first..last.

    w2 = 4 k^2 V / mu^2 = 4 k^2 (N S2 - S1^2) / S1^2, so with one shared k the key orders windows exactly and is
    free of the price scale. Prefix sums keep the whole population linear.
    """
    base = first - period + 1
    closes = [cast(int, facts[i].close) for i in range(base, last+1)]
    prefix = [0]
    squares = [0]
    for value in closes:
        prefix.append(prefix[-1] + value)
        squares.append(squares[-1] + value*value)
    keys: list[tuple[int, int]] = []
    for end in range(first, last+1):
        hi, lo = end - base + 1, end - base + 1 - period
        total, sq = prefix[hi] - prefix[lo], squares[hi] - squares[lo]
        if total <= 0 or period*sq - total*total < 0:
            fail("moment arithmetic invariant violated", ErrorCode.OVERFLOW)
        keys.append((period*sq - total*total, total*total))
    return keys


def percentile_rank(population: list[tuple[int, int]], target: tuple[int, int]) -> Fraction:
    """(2 Lt + Et) / (2 c) by exact integer cross-multiplication; the target is excluded from the population."""
    less = equal = 0
    for numerator, denominator in population:
        left, right = numerator * target[1], target[0] * denominator
        if left < right:
            less += 1
        elif left == right:
            equal += 1
    return Fraction(2*less + equal, 2*len(population))


def pivot_levels(high: int, low: int, close: int, scale: int) -> dict[str, Fraction]:
    """Classic floor-trader pivots from the exact prior-session extremes and last close, unclamped."""
    divisor = 10**scale
    point = Fraction(high + low + close, 3*divisor)
    spread = Fraction(high - low, divisor)
    return {"point": point, "resistance_1": 2*point - Fraction(low, divisor),
            "support_1": 2*point - Fraction(high, divisor),
            "resistance_2": point + spread, "support_2": point - spread}


# R17 EMA/ATR recurrences returning the unrounded Decimal120 value (callers hold the local policy context).

def _ema(values: tuple[Fraction, ...], period: int) -> Decimal:
    result = decimal_fraction(sum(values[:period], Fraction()) / period)
    for value in values[period:]:
        result = (2*decimal_fraction(value) + (period-1)*result)/(period+1)
    return result


def _atr(values: tuple[Fraction, ...], period: int) -> Decimal:
    result = decimal_fraction(sum(values[:period], Fraction()) / period)
    for value in values[period:]:
        result = ((period-1)*result + decimal_fraction(value))/period
    return result


def _keltner_core(closes: tuple[Fraction, ...], true_ranges: tuple[Fraction, ...], ema_period: int,
                  atr_period: int, multiplier: Fraction) -> tuple[Decimal, Decimal]:
    centre = _ema(closes, ema_period)
    half_width = _atr(true_ranges, atr_period) * multiplier.numerator / multiplier.denominator
    return centre, half_width


def keltner_values(closes: tuple[Fraction, ...], true_ranges: tuple[Fraction, ...], ema_period: int,
                   atr_period: int, multiplier: Fraction, features: tuple[str, ...]) -> dict[str, float]:
    """Selected Keltner cells keyed by short name (middle, upper, lower, width_ratio) from the unrounded chains."""
    try:
        with localcontext(_policy()):
            centre, half = _keltner_core(closes, true_ranges, ema_period, atr_period, multiplier)
            cells = {"middle": lambda: centre, "upper": lambda: centre + half,
                     "lower": lambda: centre - half, "width_ratio": lambda: 2*half/centre}
            return {name: decimal_float(cells[name]()) for name in features}
    except (DecimalException, OverflowError, ValueError):
        fail("channel arithmetic outside declared numeric policy", ErrorCode.OVERFLOW)


def squeeze_values(closes: tuple[Fraction, ...], true_ranges: tuple[Fraction, ...], ema_period: int,
                   atr_period: int, multiplier: Fraction, mean: Fraction, variance: Fraction, band_k: Fraction,
                   features: tuple[str, ...]) -> dict[str, float | bool]:
    """Signed gaps and the inclusive inside relation (short names lower_gap, upper_gap, inside).

    The relation is decided by exact algebra on the Decimal120 operands: with x = E + mATR - mu and
    y = mu - E + mATR, upper_gap >= 0 iff x >= 0 and x^2 >= k^2 V, and likewise for y; equal is inside.
    """
    try:
        with localcontext(_policy()):
            centre, half = _keltner_core(closes, true_ranges, ema_period, atr_period, multiplier)
            middle = decimal_fraction(mean)
            radius_squared = decimal_fraction(band_k * band_k * variance)
            radius = radius_squared.sqrt()
            result: dict[str, float | bool] = {}
            if "lower_gap" in features:
                result["lower_gap"] = decimal_float((middle - radius) - (centre - half))
            if "upper_gap" in features:
                result["upper_gap"] = decimal_float((centre + half) - (middle + radius))
            if "inside" in features:
                above, below = centre + half - middle, middle - centre + half
                result["inside"] = (above >= 0 and above*above >= radius_squared
                                    and below >= 0 and below*below >= radius_squared)
            return result
    except (DecimalException, OverflowError, ValueError):
        fail("channel arithmetic outside declared numeric policy", ErrorCode.OVERFLOW)
