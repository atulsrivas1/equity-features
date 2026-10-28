# Equity Feature Strategies

Experimental0.1.0a1, Python3.12, requiring only equity-feature-contracts0.0.4a5.
Pure deterministic AND scanning, exact scalar ranking and top-k selection over supplied core FeatureResult values. Five supported features, explicit calculation/input-semantic identities, unavailable-first readiness and full-content provenance. No recomputation, fetching, files/DB/network, clock, scheduling, publication, orders or portfolio management. Future labels are rejected as signal features.

Use immutable Entity/FeatureRequirement/Predicate/Ranking/StrategyConfig/StrategyRequest values and scan(request). FeatureRequirement.dtype is the exact core ValueType enum; all identity/version/unit and expected calculation/input-semantic digest fields are explicit. Callers project supported columns outside the package. Missing inputs remain unavailable, int64 stays exact, ties use ascending Entity order, top_k0 is valid, and incomplete/empty universe coverage is explicit. encode/digest helpers accept a closed in-memory format, not arbitrary objects or an executable/file decoder.

[Normative contracts](https://github.com/atulsrivas1/equity-features/blob/main/docs/research/STRATEGY_LABEL_CONTRACTS.md) and [story102](https://github.com/atulsrivas1/equity-features/issues/102) define qualification and experimental artifact availability. Prepared source is not an installed release until that story's actual acceptance. No profitability, provider rights/authenticity or resource sandbox guarantee.
