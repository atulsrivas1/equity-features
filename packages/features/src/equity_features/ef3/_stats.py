"""Exact-rational sample statistics shared by the EF3 robust history and pace producers; pure, no I/O.

Every function takes exact integers or `Fraction` values and returns an exact `Fraction`; the only rounding
is the single final conversion in `to_float`. Conventions: median averages the two middle values for even n,
MAD is raw (scale constant 1) about the median, the quantile is Hyndman-Fan type 7 with an exact rational p,
the percentile rank is the mid-rank (L + E/2) / n.
"""
from __future__ import annotations

from fractions import Fraction
from math import floor

from equity_feature_contracts import ErrorCode
from ._common import fail


def median(values: list[Fraction]) -> Fraction:
    """Median of a nonempty sorted sample: the middle value, or the mean of the two middle values."""
    n = len(values)
    middle = n // 2
    return values[middle] if n % 2 else (values[middle - 1] + values[middle]) / 2


def mad(values: list[Fraction]) -> Fraction:
    """Raw median absolute deviation about the median of a nonempty sorted sample."""
    centre = median(values)
    return median(sorted(abs(value - centre) for value in values))


def quantile(values: list[Fraction], p: Fraction) -> Fraction:
    """Type 7 quantile of a nonempty sorted sample for an exact rational p in [0, 1]."""
    n = len(values)
    h = (n - 1) * p
    j = floor(h)
    if j + 1 >= n:
        return values[n - 1]
    return values[j] + (h - j) * (values[j + 1] - values[j])


def mid_rank(sample: list[Fraction], x: Fraction) -> Fraction:
    """Percentile rank (L + E/2) / n of x against the sample (ties count half)."""
    below = sum(1 for value in sample if value < x)
    equal = sum(1 for value in sample if value == x)
    return (Fraction(below) + Fraction(equal, 2)) / len(sample)


def to_float(value: Fraction) -> float:
    """One correctly rounded binary64 of an exact rational; exact zero is the positive zero."""
    try:
        return float(value)
    except OverflowError:
        fail(ErrorCode.OVERFLOW, "statistic outside binary64")
