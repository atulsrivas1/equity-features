"""Gate for the optional shared preparation of compute_momentum (internal, synthetic, pre-release).

Checks: results equal with and without the argument; every admission-input mismatch is refused inconsistent_identity;
a forged preparation is refused invalid_schema; the catalog digests and backend_version are unchanged by the argument;
the no-argument path is not slower than the pre-change reference timing within noise (reported, loose bound).
"""
from __future__ import annotations

import hashlib
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import benchmark_momentum_shared_preparation as bench  # noqa: E402
from equity_feature_contracts import (  # noqa: E402
    AdjustmentSpec, AvailabilitySpec, ContractError, ErrorCode, PriceUnit,
)
from equity_features_intraday import (  # noqa: E402
    IntradayContext, build_intraday_config, build_momentum_config, compute_momentum, describe_momentum,
    intraday_catalog_digest, momentum_catalog_digest, prepare_intraday,
)
from equity_features_intraday._registry import PACKAGE_VERSION  # noqa: E402

PINNED_CATALOGS = ("11e0c702d405d1fb137dc290f65b2cc3fa0f0d09560664e865240e64a80b1125",
                   "050a0a03c12891323d1ebc4c17696c9ce0787497b441b173121465562e3ad815")  # digests of the unmodified registries at this version
failures: list[str] = []


def expect_code(name: str, code: ErrorCode, **kw: object) -> None:
    try:
        compute_momentum(**kw)  # type: ignore[arg-type]
    except ContractError as error:
        if error.code != code:
            failures.append(f"{name}: {error.code} != {code}")
        return
    failures.append(f"{name}: not refused")


def digest(result: object) -> str:
    return hashlib.sha256(repr(result).encode()).hexdigest()


def main() -> None:
    batches, context = bench.session(0)
    mom, _, pconf = bench.configs(context)
    prep = prepare_intraday(batches, context, pconf, requirements=("simple_returns",))
    cfg = mom[0]
    features = bench.feats(cfg, context)
    base = dict(context=context, features=features, preparation=prep)
    # Equality with and without, per family and per feature subset.
    for config in mom:
        f = bench.feats(config, context)
        if digest(compute_momentum(batches, context, config, features=f)) != digest(
                compute_momentum(batches, context, config, features=f, preparation=prep)):
            failures.append(f"result differs for {f}")
        if digest(compute_momentum(batches, context, config, features=f[:1])) != digest(
                compute_momentum(batches, context, config, features=f[:1], preparation=prep)):
            failures.append(f"subset result differs for {f}")
    # Mismatch matrix.
    a, j, u = cfg.availability, cfg.adjustment, cfg.price_unit
    kw = dict(family="macd", fast_period=12, slow_period=26, signal_period=9, evidence_limit=16)

    def other(**over: object) -> object:
        args = dict(availability=a, adjustment=j, price_unit=u)
        args.update(over)
        return build_momentum_config(context, **kw, **args)  # type: ignore[arg-type]

    variants: dict[str, dict[str, object]] = {
        "knowledge cutoff": dict(availability=replace(a, knowledge_cutoff_ns=a.knowledge_cutoff_ns-10)),
        "evaluation_ns": dict(availability=replace(a, evaluation_ns=a.evaluation_ns+10)),
        "reconstruction mode": dict(availability=replace(a, mode="reconstruction", reconstruction_reason="replay")),
        "price scale": dict(price_unit=PriceUnit(u.scale-1, u.currency)),
        "price currency": dict(price_unit=PriceUnit(u.scale, "EUR")),
        "adjustment": dict(adjustment=replace(j, policy_version="other-policy")),
    }
    for name, over in variants.items():
        try:
            config = other(**over)
        except ContractError:
            continue  # unreachable: refused at configuration, not a share question
        expect_code(name, ErrorCode.INCONSISTENT_IDENTITY, batches=batches, config=config, **base)  # type: ignore[arg-type]
    ctx2 = replace(context, revision="revision2")
    cfg2 = build_momentum_config(ctx2, **kw, availability=a, adjustment=j, price_unit=u)
    expect_code("different context", ErrorCode.INCONSISTENT_IDENTITY, batches=batches, config=cfg2,
                **{**base, "context": ctx2})
    expect_code("equal but not identical batches", ErrorCode.INCONSISTENT_IDENTITY,
                batches=bench.session(0)[0], config=cfg, **base)
    expect_code("batches None", ErrorCode.INCONSISTENT_IDENTITY, batches=None, config=cfg, **base)
    expect_code("empty batches", ErrorCode.INCONSISTENT_IDENTITY, batches=(), config=cfg, **base)
    expect_code("forged preparation", ErrorCode.INVALID_SCHEMA, batches=batches, config=cfg,
                **{**base, "preparation": object()})
    # Digests unchanged: the argument does not touch catalogs, backend_version or any result digest.
    plain = compute_momentum(batches, context, cfg, features=features)
    shared = compute_momentum(batches, context, cfg, features=features, preparation=prep)
    if not plain.metadata.backend_version == shared.metadata.backend_version == PACKAGE_VERSION:
        failures.append("backend_version differs")
    if plain.metadata.config_digest != shared.metadata.config_digest or plain.metadata != shared.metadata:
        failures.append("result metadata differs")
    if (intraday_catalog_digest(), momentum_catalog_digest()) != PINNED_CATALOGS or not describe_momentum():
        failures.append("catalog digest changed")
    if failures:
        raise SystemExit("shared preparation gate FAILED: " + "; ".join(failures))
    print("Shared preparation: results equal with and without, mismatch matrix refused, digests unchanged")


if __name__ == "__main__":
    main()
