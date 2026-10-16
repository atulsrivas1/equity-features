# EQ112 cross-venue mathematics and causal availability

Story214/E16#212/R12,5 provisional complexity points. This is a preparation packet while EQ111#213 remains active. Ready requires EQ111 accepted Done plus accepted EQ006/EQ033 and separate final public packet review. No contract/kernel implementation begins under this story. EQ113/114/115 retain their own readiness, implementation and actual delivery gates.

## Problem and selected bounded profile

Finite SessionSpec already handles supplied continuous partitions. New feed/product facts, two-leg normalization, causal matching and complete freeze/reopen quality need an explicit contract. Use caller-supplied finite IntervalSpec windows and AvailabilitySpec known_at mode. No rolling scheduler, calendar inference or new SessionSpec subtype. The initial research capability uses supplied positive last-trade prices, raw/default adjustment only, same currency, declared underlying/quantity units and known effective conversion. It supplies no economic-equivalence, authenticated-completeness, liquidity, profitability or provider-rights proof. Unsupported adjusted/midpoint/official-close/FX/duration-weighted/streaming modes fail explicitly.

The own optional package `equity-feature-continuous0.1.0a1` is proposed for EQ113/114 with stdlib plus unchanged `equity-feature-contracts0.0.4a4` only. Old contracts/features versions, ConfigSpec1,39registry IDs, FeatureResult/Arrow/state/worker/MCP/receipts stay unchanged. Do not coerce new results into old consumers. The new six namespaced IDs are opt-in only. No private feed, network, database/file input, wall clock, scheduling or publication occurs in calculations.

## Normative contract packet

Use EQ112_MATHEMATICS.md, EQ112_DECISIONS.md, EQ112_SCHEMAS.json and EQ112_FIXTURES.json. V3/original math/14oracles/46/48/77 drafts and all critiques remain superseded history, not current execution authority. Raw-only and the two empty-role fixes supersede conflicting V3/pre-role fixture text. JSON schema is structural documentation; it does not replace semantic typed admission or define error precedence by itself.

Planned typed API for EQ113: frozen `PriceObservation`, `Leg`, `FeedFact`, `ConversionFact`, `ContinuousConfig`, `ContinuousInput`, `Rational`, `RoleReadiness`, `MetricValue`, `DeviationWitness`, `ContinuousResult`; strict own config/input/result envelope codecs and SHA256 identities. Reuse exact existing nested contract types, detach bounded lists/tuples, reject subclasses/booleans/noncanonical fields and never run caller iterators/callbacks. Standard Python argument binding rejects unknown constructor keyword names; supplied value/codec/calculator admission uses the declared ContractError vocabulary. No pickle/arbitrary class import. Schema1 belongs to this new namespace, not the existing core schema.

EQ114 planned calls: `compute_basis(input)`, `compute_freeze(input)`, `compute_reopen(input)` return the own result type, with config.operation matching the call. `feature_ids()` exposes only the six immutable new names and cannot override the old registry. No state update/merge/checkpoint API. Serializers have strict duplicate/unknown-field/version/kind/trailing/number handling and enforce literal encoded limits; no filename/URL input parameter.

Formulas, units, ordering, first/last supplied-scope interpretation, original known-at, feed state, ratio effective time, operation-specific ages/mismatch, complete population/count weighting, exact reduced fractions/overflow stage, fixed quality roles/reasons, proof pointers and available_at are defined in the semantic/resolution documents. Every expected operation record includes complete config/legs/facts and result fields, with literal config/input/result canonical digests. The separate six rational boundaries and large exact comparison/subtraction control cover supported-stage limits; codec controls cover over-cap and noncanonical rational refusal. Digests are independently prepared with stdlib canonical JSON/SHA256, not production codecs.

## Acceptance and validation

- Freeze every original mathematical question with explicit reference choice, orientation, rational/zero/positive denominator rules, raw adjustment restriction, causal event/knowledge/effective times, count weighting, complete/incomplete/empty distinctions, exact arithmetic and limits. Retain unsupported modes without pretending coverage.
- Independently inspect all full literal inputs/results/proof pointers and canonical digests; verify hand-derived numeric rational values and fixed overflow stages. Resolve every concrete critique and preserve old failed preparations. Structural schema checks are data-tool checks, not implementation tests or runtime qualification.
- Publish the final source/docs packet before Ready and renew separate review at its actual public head. After Ready/In progress, reconcile public formula/API/type/examples compatibility decisions and freeze the original acceptance mapping. Actual candidate/default-branch CI, source publication and post-delivery verification precede Done. No installable code changes in EQ112; future installed distribution is EQ115.

The example documentation must include the120versus100 basis20/premium1/5,101 with2/3normalization versus67 producing1/3and1/201, freeze101/98/102 around100 giving max2/countmean5/3/stabletopK c2,c3, and pre-reopen120versus125 gap-5/ratio-1/25 with first known availability including all consumed certificates. An unavailable outcome must show the exact failed role/proof rather than a fabricated numeric value. Duration mean3/2 is a counterexample to the selected observation-count5/3, not a supported mode.

## Downstream delivery requirements

EQ113 must implement only the approved companion data/config/codecs, preserve the old independent config digest and finite sessions, and add strict positive/negative typing and round-trip/error/canonical fixtures. EQ114 must use these fixed literals for numerical admission/parity, stable tie/evidence/overflow and pure boundary audits; no expected numeric value may be computed by its own implementation. New public API docs/examples accompany each story.

EQ115 requires actual fresh clean Windows/Linux four-form light/combined wheel/selected-SDist installs, source/license/dependency/materialization/RECORD/origin maps, repeat archive parity, old-core numeric/config parity and current public provider ZIP every-member/size/hash/expiry auditing. Source tests, installed tests, native proofs and actual main qualification have distinct scopes. A new optional package needs its own concrete builder/workflow plan before code; no old artifact relabeling. R7 stays parked/automation paused, R13 unselected. No provider/private acquisition, hosting/account/spending/trading/registry action is authorized by this packet.

## Exact next step

Finish EQ111 final current CI, actual bothOS649-source-step logs, main delivery and two-criterion acceptance. Then freeze the final EQ112 packet filenames/maps/reviewer disposition and live dependencies, publish a linked draft, independently verify public sources, and move only EQ112 Backlog -> Ready -> In progress. Perform no EQ113 runtime implementation until EQ112 is accepted. Preserve unrelated primary bytes and14EQ108 mirrors throughout.
