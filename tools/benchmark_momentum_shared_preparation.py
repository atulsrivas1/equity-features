"""Momentum with and without a shared preparation (Story 2B); internal, synthetic, pre-release; indicative, uncontrolled.

Times compute_momentum for its three sub-families on seeded synthetic 390-slot sessions, once with each call admitting
the batches itself and once with one shared prepare_intraday product, and checks the canonical results hash equal.
The other families are timed unshared only and their shared cost is PROJECTED as (unshared - admit) because they do
not yet accept a preparation. Work-note numbers only; no release claim.
"""
from __future__ import annotations

import hashlib
import json
import random
import statistics
import sys
import time
from fractions import Fraction

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, Coverage, DataKind, InputScope,
    IntervalCoverage, PriceUnit, SessionSpec, SourceBinding,
)
from equity_features_intraday import (
    IntradayContext, IntradayRun, build_channels_config, build_intraday_config, build_momentum_config,
    build_money_flow_config, build_path_efficiency_config, build_realized_variance_config, compute_channels,
    compute_momentum, compute_money_flow, compute_path_efficiency, compute_realized_variance,
    decode_momentum_config, prepare_intraday,
)
from equity_features_intraday._admission import admit
from equity_features_intraday._momentum_registry import MOMENTUM_FAMILY_FEATURES

SLOTS = 390
SEEDS = 12
REPEATS = 7


def session(seed: int):
    rnd = random.Random(seed)
    n = SLOTS
    context = IntradayContext(f"SYN{seed:03}", "synthetic-calendar", "ten-ns-grid", "revision1",
                              (SessionSpec("synthetic", "S", 0, n*10, "UTC"),), (IntradayRun("S", 0, 10, n),),
                              0, n-1, "reset")
    price, closes = 1000000, []
    for _ in range(n):
        price += rnd.randint(-40, 40)
        closes.append(price)
    nulls = {rnd.randrange(n) for _ in range(3)} if seed % 3 == 0 else set()
    gap = False
    cols = [Column("instrument_id", (context.instrument_id,)*n), Column("session_id", ("S",)*n),
            Column("start_ns", tuple(i*10 for i in range(n))), Column("end_ns", tuple((i+1)*10 for i in range(n))),
            Column("known_at_ns", tuple((i+1)*10 for i in range(n))),
            Column("close", tuple(None if i in nulls else c for i, c in enumerate(closes))),
            Column("high", tuple(None if i in nulls else c+rnd.randint(1, 9) for i, c in enumerate(closes))),
            Column("low", tuple(None if i in nulls else c-rnd.randint(1, 9) for i, c in enumerate(closes))),
            Column("volume", tuple(0 if i in nulls else rnd.randint(1, 1000) for i in range(n)))]
    batch = CanonicalBatch(DataKind.BAR, tuple(cols), BatchMetadata(
        "synthetic", SourceBinding("synthetic", f"snap{seed}", "map1", f"input{seed}"),
        Coverage(n, n-gap, not gap), PriceUnit(4, "USD"), scope=InputScope(0, n*10, "synthetic-v1"),
        interval_coverage=tuple(IntervalCoverage(f"slot:{i}", i*10, (i+1)*10,
                                                 Coverage(1, 0 if gap and i == 100 else 1, not (gap and i == 100)))
                                for i in range(n))))
    return (batch,), context


def configs(context):
    a, j, u = AvailabilitySpec(SLOTS*10, SLOTS*10, SLOTS*10), AdjustmentSpec(), PriceUnit(4, "USD")
    kw = dict(availability=a, adjustment=j, price_unit=u)
    mom = [build_momentum_config(context, family="macd", fast_period=12, slow_period=26, signal_period=9,
                                 evidence_limit=16, **kw),
           build_momentum_config(context, family="dmi", di_period=14, adx_period=14, evidence_limit=16, **kw),
           build_momentum_config(context, family="stochastic", k_period=14, k_slowing=3, d_period=3,
                                 evidence_limit=16, **kw)]
    other = {
        "flow": (compute_money_flow, build_money_flow_config(context, policy_version="ef2-mf1", cmf_period=20,
                                                             evidence_limit=16, **kw), ("intraday.obv", "intraday.cmf")),
        "channels": (compute_channels, build_channels_config(context, producer="donchian", period=20,
                                                             evidence_limit=16, **kw), None),
        "rv": (compute_realized_variance, build_realized_variance_config(
            context, policy_version="ef3-rv1", sampling="every_governed_slot", annualization_factor=None,
            evidence_limit=16, **kw), ("intraday.realized_variance",)),
        "path": (compute_path_efficiency, build_path_efficiency_config(
            context, policy_version="ef4-path1", window=20, epoch_profile="session_reset", evidence_limit=16, **kw),
            ("path.efficiency_ratio", "path.net_displacement")),
    }
    prep = build_intraday_config(context, period=20, band_k=Fraction(2), evidence_limit=16, **kw)
    return mom, other, prep


def feats(config, context):
    return tuple(sorted(MOMENTUM_FAMILY_FEATURES[decode_momentum_config(context, config).family]))


def canon(result) -> str:
    return hashlib.sha256(repr(result).encode()).hexdigest()


def timed(fn):
    samples = []
    for _ in range(REPEATS):
        t = time.perf_counter()
        fn()
        samples.append(time.perf_counter()-t)
    return statistics.median(samples)


def main() -> None:
    inputs = []
    for seed in range(SEEDS):
        batches, context = session(seed)
        mom, other, pconf = configs(context)
        inputs.append((batches, context, [(c, feats(c, context)) for c in mom], other, pconf))
    same = 0
    for batches, context, mom, _, pconf in inputs:
        prep = prepare_intraday(batches, context, pconf, requirements=("simple_returns",))
        for cfg, f in mom:
            assert canon(compute_momentum(batches, context, cfg, features=f)) == canon(
                compute_momentum(batches, context, cfg, features=f, preparation=prep)), (context.instrument_id, f)
            same += 1
    preps = [prepare_intraday(b, c, p, requirements=("simple_returns",)) for b, c, _, _, p in inputs]

    def run_plain():
        for batches, context, mom, _, _ in inputs:
            for cfg, f in mom:
                compute_momentum(batches, context, cfg, features=f)

    def run_shared():
        for batches, context, mom, _, pconf in inputs:
            prep = prepare_intraday(batches, context, pconf, requirements=("simple_returns",))
            for cfg, f in mom:
                compute_momentum(batches, context, cfg, features=f, preparation=prep)

    def run_shared_excl_prep():
        for (batches, context, mom, _, _), prep in zip(inputs, preps):
            for cfg, f in mom:
                compute_momentum(batches, context, cfg, features=f, preparation=prep)

    def run_admit():
        for batches, context, mom, _, _ in inputs:
            admit(batches, context, mom[0][0])

    def run_prep():
        for batches, context, _, _, p in inputs:
            prepare_intraday(batches, context, p, requirements=("simple_returns",))

    def run_other():
        for batches, context, _, other, _ in inputs:
            for fn, cfg, fs in other.values():
                fn(batches, context, cfg, **({} if fs is None else {"features": fs}))

    run_plain(); run_shared(); run_other()  # warm up
    t_plain, t_shared = timed(run_plain), timed(run_shared)
    t_excl, t_admit, t_prep, t_other = timed(run_shared_excl_prep), timed(run_admit), timed(run_prep), timed(run_other)
    n = SEEDS
    six_plain = t_plain+t_other
    six_shared = t_prep+t_excl+(t_other-4*t_admit)
    out = {
        "status": "internal, synthetic, pre-release; indicative, uncontrolled, work notes only",
        "sessions": n, "slots": SLOTS, "repeats": REPEATS, "python": sys.version.split()[0],
        "hash_equal_cases": same,
        "ms_per_session": {"momentum_unshared_3_calls": 1000*t_plain/n, "momentum_shared_incl_prepare": 1000*t_shared/n,
                           "momentum_shared_excl_prepare": 1000*t_excl/n, "admit_only": 1000*t_admit/n,
                           "prepare_intraday": 1000*t_prep/n, "other_four_families_unshared": 1000*t_other/n},
        "momentum_gain_incl_prepare": t_plain/t_shared,
        "momentum_gain_excl_prepare": t_plain/t_excl,
        "six_family_gain_projected": six_plain/six_shared,
        "six_family_projection_note": "other four families' shared cost projected as unshared minus admit; not measured",
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
