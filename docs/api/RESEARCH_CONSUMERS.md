# Pure research consumer API definition

[EQ089#101](https://github.com/atulsrivas1/equity-features/issues/101) fixes this contract before implementation. Types and functions below are specified targets, not importable modules or qualified distributions yet. See [complete normative schemas/math/encoding/errors](../research/STRATEGY_LABEL_CONTRACTS.md) and [independent71requirements](../stories/EQ-089_FIXTURES.json).

| Distribution target | Public entry point | Inputs and output |
| --- | --- | --- |
| equity-feature-strategies0.1.0a1 | scan(StrategyRequest) -> StrategyResult | Entity, FeatureRequirement, Predicate, Ranking, StrategyConfig; supplied core FeatureResult, exact known_at availability, declared universe; complete rows/ranking/top-k/coverage/provenance |
| equity-feature-labels0.1.0a1 | evaluate_label(LabelRequest) -> LabelResult | Entity, BasisWitness, LabelOrigin, PriceObservation, LabelConfig; supplied immutable original signal and future price/basis facts; pending/incomplete/mature with causal numeric admission |

Each targets Python>=3.12,<3.13 and requires only equity-feature-contracts==0.0.4a4. Neither imports equity_features or the other research package. Core has no outward dependency. Both expose closed in-memory encode/digest helpers for their own supported records and immutable-code ValueError subclasses StrategyError/LabelError. Exact fields/version/error vocabulary/canonical tagged scalar domains and normalization are normative, no arbitrary decoder/import/file serializer.

Scanner requires exact FeatureRequirement expected_result_config_digest and expected_input_semantic_digest, closed five-feature schema/algorithm/dtype/unit, one namespace/session and identical availability. Callers project unsupported producer columns outside this package. All required predicate/rank cells are assessed; unavailable dominates false. Preserve exact int64 comparisons, numeric-direction sort with ascending Entity ties, unique ordinal ranks and top_k0. Complete rows and exact eligible/expected coverage distinguish partial and empty0/0.

Label uses checked elapsed int64 horizon/exact endpoints and supplied raw/split basis. Original signal anchor/availability/digests never change when future label path/basis revises. Nonmature outputs have null value/label_known_at; mature price-return uses quotient then subtract1 with explicit numeric guards. No total return/dividend/interpolation/calendar discovery. Consumer joins require mature status, endpoint<=join C and label_known_at<=join K under causal C/K/E and explicit matching origin/revision selection.

No fetching, files/DB/network, wall clock, credentials, job scheduling, publication, orders or portfolio management. Supplied basis/origin identities are trusted facts, not authentication/economic validation. EQ090/EQ091 implement meaningful independent fixtures and pure boundaries; EQ092 qualifies actual optional wheels/sdists and synthetic actual-producer/backtest/causality examples. Until those gates, existing installation/core API remains unchanged.
