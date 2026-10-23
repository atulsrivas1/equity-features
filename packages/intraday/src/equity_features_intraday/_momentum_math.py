"""EF2 momentum operands and R17 Decimal120 recurrences (ef2-conv1): MACD, DMI/ADX, stochastic, Williams %R.

Exact Fraction seeds, ordered recurrences in a fresh local Decimal context (the R17 policy), one guarded final
Float64 conversion with normalized exact zero. Callers have established the readiness of every operand slot.
"""
from __future__ import annotations

from dataclasses import dataclass
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


def _finite(value: Decimal) -> float:
    converted = float(value)
    if not isfinite(converted):
        fail("nonfinite momentum conversion", ErrorCode.OVERFLOW)
    return 0.0 if value == 0 else converted


# Additive internal operand families (immutable tuples over slots whose fields the caller proved ready).

def directional_moves(facts: tuple[SlotFacts, ...], first: int, last: int,
                      scale: int) -> tuple[tuple[Fraction, Fraction], ...]:
    """(+DM, -DM) for k = first+1..last: up = H[k]-H[k-1], dn = L[k-1]-L[k]; the strictly larger positive move wins."""
    divisor = 10**scale
    result: list[tuple[Fraction, Fraction]] = []
    for k in range(first+1, last+1):
        up = cast(int, facts[k].high) - cast(int, facts[k-1].high)
        dn = cast(int, facts[k-1].low) - cast(int, facts[k].low)
        result.append((Fraction(up if up > dn and up > 0 else 0, divisor),
                       Fraction(dn if dn > up and dn > 0 else 0, divisor)))
    return tuple(result)


def rolling_extrema_runs(facts: tuple[SlotFacts, ...], last: int, window: int, count: int,
                         scale: int) -> tuple[tuple[Fraction, Fraction, Fraction], ...]:
    """(HH, LL, C) for the `count` consecutive window ends last-count+1..last; the final element is the R17 extrema."""
    divisor = 10**scale
    result: list[tuple[Fraction, Fraction, Fraction]] = []
    for end in range(last-count+1, last+1):
        span = facts[end-window+1:end+1]
        result.append((Fraction(max(cast(int, f.high) for f in span), divisor),
                       Fraction(min(cast(int, f.low) for f in span), divisor),
                       Fraction(cast(int, facts[end].close), divisor)))
    return tuple(result)


# MACD

def _ema_chain(values: tuple[Fraction, ...], period: int) -> list[Decimal]:
    """E_p[k] for k = p-1..T-1; seed is the exact mean of the first p closes, alpha = 2/(p+1)."""
    if period == 1:
        return [decimal_fraction(value) for value in values]
    chain = [decimal_fraction(sum(values[:period], Fraction()) / period)]
    for value in values[period:]:
        chain.append((2*decimal_fraction(value) + (period-1)*chain[-1]) / (period+1))
    return chain


def macd_values(closes: tuple[Fraction, ...], fast: int, slow: int, signal: int,
                features: tuple[str, ...]) -> dict[str, float]:
    """Selected MACD outputs at the target of a fully ready epoch with at least the selected seeds."""
    if len(set(closes)) == 1:
        return {feature: 0.0 for feature in features}
    try:
        with localcontext(_policy()):
            fast_chain = _ema_chain(closes, fast)
            slow_chain = _ema_chain(closes, slow)
            lines = [f - s for f, s in zip(fast_chain[slow-fast:], slow_chain)]
            result: dict[str, float] = {}
            if "intraday.macd_line" in features:
                result["intraday.macd_line"] = _finite(lines[-1])
            if "intraday.macd_signal" in features or "intraday.macd_histogram" in features:
                if signal == 1:
                    smoothed = lines[-1]
                else:
                    smoothed = sum(lines[:signal], Decimal(0)) / signal
                    for line in lines[signal:]:
                        smoothed = (2*line + (signal-1)*smoothed) / (signal+1)
                if "intraday.macd_signal" in features:
                    result["intraday.macd_signal"] = _finite(smoothed)
                if "intraday.macd_histogram" in features:
                    result["intraday.macd_histogram"] = _finite(Decimal(0) if signal == 1 else lines[-1] - smoothed)
            return result
    except (DecimalException, OverflowError, ValueError):
        fail("momentum arithmetic outside declared numeric policy", ErrorCode.OVERFLOW)


# DMI and ADX

@dataclass(frozen=True)
class DmiResult:
    first_dx: int | None  # zero-based epoch index of the first defined DX at or after k = di_period
    dx_defined: bool  # DX defined at the target
    plus_di: float | None
    minus_di: float | None
    dx: float | None
    adx: float | None  # None until adx_period DX values exist from first_dx, or when the chain met an undefined DX


def dmi_values(trs: tuple[Fraction, ...], moves: tuple[tuple[Fraction, Fraction], ...],
               di: int, adx: int, want_adx: bool) -> DmiResult:
    """TR and DM for k = 1..T-1 (T-1 >= di).

    A smoothed value is zero exactly when its weighted inputs are all zero, decided on the exact inputs: every
    input since k = 1 for di >= 2 (all weights positive), the current input alone for di = 1 (weight of history 0).
    An ADX chain that consumes an undefined DX (possible only for di = 1) is itself undefined.
    """
    try:
        with localcontext(_policy()):
            smooth_tr = decimal_fraction(sum(trs[:di], Fraction()) / di)
            smooth_up = decimal_fraction(sum((m[0] for m in moves[:di]), Fraction()) / di)
            smooth_dn = decimal_fraction(sum((m[1] for m in moves[:di]), Fraction()) / di)
            tr_seen = any(x > 0 for x in trs[:di])
            dm_seen = any(m[0] > 0 or m[1] > 0 for m in moves[:di])
            first: int | None = None
            broken = False
            series: list[Decimal] = []
            plus_di: Decimal | None = None
            minus_di: Decimal | None = None
            dx: Decimal | None = None
            for k in range(di, len(trs)+1):
                if k > di:
                    tr_seen = tr_seen or trs[k-1] > 0
                    dm_seen = dm_seen or moves[k-1][0] > 0 or moves[k-1][1] > 0
                    smooth_tr = ((di-1)*smooth_tr + decimal_fraction(trs[k-1])) / di
                    smooth_up = ((di-1)*smooth_up + decimal_fraction(moves[k-1][0])) / di
                    smooth_dn = ((di-1)*smooth_dn + decimal_fraction(moves[k-1][1])) / di
                tr_positive = trs[k-1] > 0 if di == 1 else tr_seen
                dm_positive = (moves[k-1][0] > 0 or moves[k-1][1] > 0) if di == 1 else dm_seen
                last = k == len(trs)
                if last:
                    plus_di = 100*smooth_up/smooth_tr if tr_positive else None
                    minus_di = 100*smooth_dn/smooth_tr if tr_positive else None
                if tr_positive and dm_positive:
                    first = k if first is None else first
                    value = 100*abs(smooth_up-smooth_dn) / (smooth_up+smooth_dn)
                    series.append(value)
                    if last:
                        dx = value
                elif first is not None:
                    broken = True
            smoothed: Decimal | None = None
            if want_adx and not broken and first is not None and len(series) >= adx:
                smoothed = sum(series[:adx], Decimal(0)) / adx
                for value in series[adx:]:
                    smoothed = ((adx-1)*smoothed + value) / adx
            return DmiResult(first, dx is not None,
                             None if plus_di is None else _finite(plus_di),
                             None if minus_di is None else _finite(minus_di),
                             None if dx is None else _finite(dx),
                             None if smoothed is None else _finite(smoothed))
    except (DecimalException, OverflowError, ValueError):
        fail("momentum arithmetic outside declared numeric policy", ErrorCode.OVERFLOW)


# Stochastic oscillators and Williams %R

def _raw(run: tuple[Fraction, Fraction, Fraction]) -> Fraction | None:
    high, low, close = run
    return None if high == low else 100*(close-low)/(high-low)


def williams_value(run: tuple[Fraction, Fraction, Fraction]) -> float | None:
    """W = -100 (HH - C) / (HH - LL) for the last window end; None for a zero range."""
    high, low, close = run
    if high == low:
        return None
    try:
        with localcontext(_policy()):
            return _finite(decimal_fraction(-100*(high-close)/(high-low)))
    except (DecimalException, OverflowError, ValueError):
        fail("momentum arithmetic outside declared numeric policy", ErrorCode.OVERFLOW)


def stochastic_values(runs: tuple[tuple[Fraction, Fraction, Fraction], ...], slowing: int,
                      d_period: int | None) -> float | None:
    """%K (d_period None; runs holds the last k_slowing window ends) or %D (runs holds k_slowing+d_period-1 ends).

    A smoothed value that consumes any undefined raw value is undefined (None).
    """
    raws = [_raw(run) for run in runs]
    if any(raw is None for raw in raws):
        return None
    try:
        with localcontext(_policy()):
            values = [decimal_fraction(cast(Fraction, raw)) for raw in raws]
            slowed = [sum(values[i:i+slowing], Decimal(0)) / slowing
                      for i in range(len(values)-slowing+1)]
            if d_period is None:
                return _finite(slowed[-1])
            return _finite(sum(slowed[-d_period:], Decimal(0)) / d_period)
    except (DecimalException, OverflowError, ValueError):
        fail("momentum arithmetic outside declared numeric policy", ErrorCode.OVERFLOW)
