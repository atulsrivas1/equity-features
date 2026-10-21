# EF1 supplied anchor API — EQ167 source-authoring slice

Experimental feature package0.0.4a5, canonical contracts0.0.4a4. This change is source-authored and unexecuted while the EQ142 qualification resource window is reserved. No numerical, installable-artifact, worker/sink, review or release acceptance is claimed. [Frozen EF1 contract](../ef1/CONTRACT.json) and [mathematics](../features/EF1_ANCHORS.md) govern the selected slice.

Explicitly import from `equity_features.ef1`:

```python
build_ef1_config(selection, *, session, window, availability, price_unit, adjustment)
decode_ef1_context(config)
ef1_definitions(config)
compute_ef1(batches, config, *, entity)
```

The first builder argument is the complete mathematical context dictionary with exactly version, producer, calendar and selection. Anchor producer requires version `ef1-context1`, producer `anchor`, calendar null, selection exactly mode/definition. Mode is `trades` or `bars_actual_notional`. Definition has exactly anchor_id/reset_id/start_ns/selection_policy_id/revision; no acquired known-at or market values. All strings have explicit safety/size bounds. Context encodes canonical ASCII JSON (sorted keys, no whitespace, finite exact integer values), at most4096bytes/codepoints and depth8. Decoder rejects duplicate/unknown fields and noncanonical strings, and returns a detached recursively immutable mapping.

Real regular SessionSpec remains unchanged. Window must be `WindowSpec(1,target,(target,),"completed_eod")`; ConfigSpec identity is `ef1.anchor`, algorithm `v1`, schema1, with exactly one ef1_context_json Parameter. C/K/E are actual AvailabilitySpec values; start<C strictly. Builder and callback revalidate, so bypassing discovery cannot bypass admission. Unsupported EF1 producers return `unsupported_capability`; no partial placeholder result advertises them implemented.

`batches` is a concrete tuple/list of **present actual CanonicalBatch objects**, at most2, in nonmissing-role order. Primary kind is TRADE or BAR according to mode; second kind is REFERENCE for anchor_provenance. Either role may be missing: `(proof,)`, `(market,)` and `()` preserve absence without a fake source. Wrong/reordered/duplicate roles, duplicate input_id and lazy iterables fail. A covered empty primary is a real zero-row canonical batch with positive-duration scope and complete0/0coverage.

Market namespace/entity, price unit, adjustment, declared order and reject-duplicate policy must match. Actual scope is exactly[start,C), with explicit eligibility identity and auction construction matching SessionSpec. Trade order and bar coherence use public canonical validation. Ordinary trades atC or outside the anchor scope fail; the existing explicit regular-close auction exception requires exact matching construction. No sort/dedup/proration occurs. Canonical input metadata retains the original source identity; the numerical package reads no external resources.

Actual proof is REFERENCE: exactly one row, kind `ef1.anchor.provenance`, text `supplied_anchor`, reference_id `a1:` plus lowercase SHA256 of canonical ASCII **definition** only, effective_start equal anchor start, original known-at and end null or>C. Source snapshot equals requested revision and mapping_version is `ef1-reference-map1`. Namespace/entity match target; price/factor payload columns are forbidden. Missing/empty/incomplete, late/unknown or expired proof leaves affected outputs unavailable; wrong hash/revision/shape raises typed error. The hash binds the supplied declaration; it authenticates neither source truth nor a historical anchor-selection algorithm.

`ef1_definitions` returns a frozen tuple of own `EF1Definition` records, not a default-registry extension. Records expose feature_id, algorithm/schema versions, dtype, unit, outputs, requirements, formula and batch-only capabilities. The canonical FeatureDefinition validator deliberately only admits its accepted built-ins with executable flags, so EF1 does not bypass or widen it. Exact sorted complete outputs:

| ID | Type | Unit / representation |
| --- | --- | --- |
| session.anchor.notional | decimal128 | Currency coefficient at bound PriceUnit.scale |
| session.anchor.volume | int64 | Integer shares |
| session.anchor.vwap | float64 | Full currency/share, one final conversion |

One call returns one complete canonical FeatureResult: all3values and quality rows, original complete present input bindings, unchanged availability/config digest, backend python-exact and feature backend version0.0.4a5. Scalar evidence is empty/evidence_limit0; full supplied input content remains the canonical task's responsibility. Quality expected/observed counts use original primary market row population; the independent proof gates readiness without fabricating market observations. No result concatenation or worker metadata rewrite is permitted. Different anchors/configurations need separate work/publication identities.

Missing actual bar notional affects notional/VWAP, preserving independently ready volume. Complete positive-duration empty population gives totals0 and null VWAP/not_applicable/zero_denominator; missing primary is missing_input. Coverage, known-at and missing-field reasons remain distinct. Unknown/future source knowledge is retained rather than adapter-filtered or overwritten. Corrections require a new immutable source/request identity and full replay; no update/restore/merge is supported.

Positive-volume bars with supplied actual_notional require it to be strictly positive even when optional OHLC columns are absent. Zero or negative supplied notional is malformed input, not an available zero/negative VWAP. Positive actual-notional/volume operands may calculate without OHLC; absent/null notional remains unavailable while volume stays independently ready. The zero-volume zero/absent rule is unchanged. Independent review finding LIB01 identified the missing guard; its source correction and additional fixtures are authored but unexecuted pending the reserved resource window and reviewer recheck.

The default core39registry and R17 APIs are unchanged. Feature-package version bump changes backend metadata of old kernels that already report the feature version; olda4 complete result bytes are not promised identical. Accepted worker a4dependency/backend guards need a separately reviewed EF1 companion admission. No canonical distribution/schema/codec change is made. The remaining8EF1producers and full EQ164 inventory audit remain outstanding.

Current source/install/build gates now distinguish exact features0.0.4a5 from contracts0.0.4a4 instead of requiring equal package versions. Current build family maps and the standalone consumer's feature dependency use that exact pair; canonical dependencies staya4. No historical qualification receipt, measured baseline or source-pinned quickstart artifact was rewritten. Installed typing authoring adds a public EF1 positive caller and3independent rejected EF1 calls alongside the existing legacy cases. These checks and21anchor test methods are authored, **not executed**. Provenance/conformance/R10 companion worker source/dependency pins require the coordinator's reviewed worker15 migration before their new-bundle qualification can pass; changing a package map alone does not establish compatibility.

LIB02 source review identified an additional current-bundle gate: explanationsa1 refused the genuine a5 backend metadata on unchanged legacy results. The explanationsa2 companion candidate now admits exactly python-exact a4/a5 in both matching guards, preserving actual result/receipt identity and the existing built-in-ID lookup. It adds no EF1 explanation producer or numerical semantics. Its3current artifact maps targeta2; R9 inherits that common map. No package declares a runtime dependency on explanations, so no downstream dependency pin was widened. The old a1 receipts/oracles stay unchanged. Paired hand-authored a4/a5 and unknowna6 refusal controls are authored, unexecuted, and await renewed independent review.
