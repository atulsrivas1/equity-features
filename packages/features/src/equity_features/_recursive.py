"""Bounded scalar recurrences after caller-history admission; no public state API."""
from fractions import Fraction
import math
from typing import cast
from equity_feature_contracts import checked_decimal128, checked_int64


def rsi(closes: list[int], period: int) -> float:
    gains = checked_decimal128(sum(max(b-a, 0) for a, b in zip(closes[:period], closes[1:period+1])))
    losses = checked_decimal128(sum(max(a-b, 0) for a, b in zip(closes[:period], closes[1:period+1])))
    total = checked_decimal128(gains+losses)
    proportion = float(Fraction(gains, total)) if total else 0.5
    mantissa, exponent = math.frexp(float(Fraction(total, period)))
    decay = (period-1)/period
    for index in range(period+1, len(closes)):
        delta = closes[index]-closes[index-1]
        if delta == 0:
            if mantissa:
                mantissa, shift = math.frexp(mantissa*decay)
                exponent = checked_int64(exponent+shift)
            continue
        new_mantissa, new_exponent = math.frexp(abs(delta)/period)
        if not mantissa:
            mantissa, exponent = new_mantissa, new_exponent
            proportion = float(delta > 0)
            continue
        old_mantissa, shift = math.frexp(mantissa*decay)
        old_exponent = checked_int64(exponent+shift)
        common = max(old_exponent, new_exponent)
        old_difference = old_exponent-common
        new_difference = new_exponent-common
        old_weight = math.ldexp(old_mantissa, old_difference) if old_difference >= -1074 else 0.0
        new_weight = math.ldexp(new_mantissa, new_difference) if new_difference >= -1074 else 0.0
        combined = old_weight+new_weight
        proportion = (old_weight*proportion+new_weight*float(delta > 0))/combined
        mantissa, shift = math.frexp(combined)
        exponent = checked_int64(common+shift)
    return 100.0*proportion


def atr(rows: list[tuple[int | None, int | None, int | None]], period: int, scale: int) -> float:
    ranges = [max(cast(int, high)-cast(int, low), abs(cast(int, high)-cast(int, previous[0])),
                  abs(cast(int, low)-cast(int, previous[0])))
              for previous, (_, high, low) in zip(rows, rows[1:])]
    average = float(Fraction(checked_decimal128(sum(ranges[:period])), period*scale))
    for true_range in ranges[period:]:
        average = ((period-1)/period)*average+(true_range/scale)/period
    return average
