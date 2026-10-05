# EQ-021 — sampled quote metrics plan

Prepared before code, issue25/epic20/R1; confirm8points. Pull only after EQ020
verified Done. One active story; preserve EQ095/PR120. Author self-review plus CI.

## Mathematics and interface

`compute_quotes(batch: CanonicalBatch | None, config: ConfigSpec, *, entity:
EntityKey) -> FeatureResult` implements sampled_spread and state_counts only.
Parameters eligibility_policy and observation_limit (exact integer0..10000).
No quantiles/variance: frozen QUOTE_FORMULAS explicitly excludes them, despite
provisional handoff wording. Preserve original equation, no new feature meaning.
Normalized quote schema contains no eligibility column; every caller-admitted
row is an observation, and caller owns exclusion/withdrawal/delta normalization.

Require source/session/unit/basis/target InputScope/coverage and C/K/E compatibility,
exact unique total input order. Sampling must be trade_snapshot or continuous;
identity remains explicit and both are event-weighted populations, never pooled
or described as duration-complete. Qc means are update weighted.

Classify null/nonpositive sides invalid, positive b<a normal, equal locked,
b>a crossed. Sizes optional and ignored. Counts total=normal+locked+crossed+invalid,
valid=normal+locked, exact checked int64. Valid spread=(a-b)/10^scale; bps=
20000*(a-b)/(a+b), exact wide integer differences/half-sum before float conversion.
Mean spread uses checked decimal128 coefficient sum/valid/scale. Bps reduction
uses compensated float64 sum of individually exact Fraction-converted bps,
never ratio of mean spread/midpoint. rtol/atol1e-12; counts exact.

Typed QuoteStateCounts exposes classification counts/derived valid/total. Typed
SampledSpread carries two valid-only means, sampling identity, total/valid and
owned bounded optional QuoteObservation diagnostics. Retain first min(limit,n)
ordered original event states, signed crossed diagnostics, invalid null diagnostics;
record truncation explicitly. Limit0 retains none. Root source metadata binds rows;
matching bounded EvidenceRows tie optional original observations to source/event.
Arrow typed structs/list and UTCns; no JSON cell or new scalar feature IDs.

Complete empty/allinvalid/allcrossed counts available; no valid spread gives
sampled means null/not_applicable independently, retaining typed bounded diagnostics.
FeatureResult gains a narrowly validated structured NOT_APPLICABLE exception for
SampledSpread with valid=0 and null means; incomplete/missing remain null cells. Missing source/absent side fields
(nonempty population) ->missing_input; incomplete/unknown knowledge nulls affected
publications. Explicit null side is counted invalid, not missing-input enrichment.
No unbounded observations or stream capability: summary state is fixed counts,
exact spread total and compensated bps pair, diagnostics bounded by configuration.
Batch canonical admission still costs proportional to input. Future update mode
will support limit0 or prove bounded diagnostics independently.

## Independent verification and delivery

Golden bid100/102/105/null ask102/102/104/102: total4,normal1,locked1,crossed1,
invalid1,valid2; mean spread1 and bps10000/101. Test scale/wide half-sums,
mean-of-bps differing from ratio-of-means, locked/crossed/nonpositive/null/optional
sizes, equal-time order/duplicates, boundaries, sampling labels, empty/missing,
coverage/K/reconstruction and metadata. Optional limit/truncation/provenance,
immutable ownership/Arrow and retained scaling tested. Version0.0.2a4 both
packages;22 implemented batch IDs. Update exact discovery example count22.
API/examples/contracts/registry/changelog/README/continuity and EQ020 receipt;
full local/head/main gates and actual OS bundles/four fresh installs before Done.
