# EQ137 pre-code contract: immutable intraday preparation

Story [#471](https://github.com/atulsrivas1/equity-features/issues/471), parent [E25](https://github.com/atulsrivas1/equity-features/issues/465), R17 milestone21. This is a concrete proposal for exact review before Ready and implementation. No preparation package, installed artifact, numerical producer or measured performance result exists yet.

## Accepted mathematical input and remaining gates

Use the original EQ136 [mathematics](https://github.com/atulsrivas1/equity-features/blob/8044f2a0f59d29b85981aaa446777ac2f92fc29b/docs/features/INTRADAY_FOUNDATIONS.md), [API/transport/quality](https://github.com/atulsrivas1/equity-features/blob/8044f2a0f59d29b85981aaa446777ac2f92fc29b/docs/api/INTRADAY.md), original fixtures and frozen benchmark/adoption plan on actual published main8044f2a0f59d29b85981aaa446777ac2f92fc29b. Separate source review passed71 assertions and79 fresh methods;80 independent mathematical cases remain source-bound. Candidate70 checks passed; independent actual-main readback matched all1,232 Git leaves/all21 changed public files. This frozen mathematical-contract component is explicitly accepted as an input to this story, not production qualification.

EQ136 actual-main run39227653910 and final Done acceptance remain separate open gates. Check for known relevant failures before Ready, and rework dependent work if a later failure invalidates these inputs. A separate assessment of actual requirements/inputs supports component admission without inventing a literal upstream Done-label barrier (receipt SHA2569c8c6348af33ff9409121a66735fa44c0ce63fe1180481ae4383bc50362a6be1). This packet still requires its own published exact review, assignment and Ready admission. One active implementation story; earlier specification delivery is not a competing kernel implementation.

## Scope, package and public capability

Deliver `packages/intraday`, distribution `equity-features-intraday==0.1.0a1`, module `equity_features_intraday`, exact dependency `equity-feature-contracts==0.0.4a4`, Python3.12. Implement the accepted context/run/config codec, source admission, own descriptive discovery and compatible immutable preparation factory. Existing core39-ID registry, runtime packages, exact downstream pins and daily mathematics remain unchanged.

The eight selected output IDs are described truthfully with batch capability false until EQ138/EQ139 implements them. Invoking an unimplemented selected output returns typed UNSUPPORTED_CAPABILITY, not a placeholder numerical result. Preparation is supported independently of those output kernels. Public update/restore/merge remain unsupported; there is no persistent/live service, new executor, acquisition, credential access or output publication in calculations. EQ140 owns the actual installed worker binding.

## Producer, inspection and ownership

Implement accepted signatures `IntradayRun`, `IntradayContext`, `build_intraday_config` and `prepare_intraday(batches, context, config, *, requirements)`. Preparation is a concrete opaque immutable factory product, with no public constructor, restore, merge or wire codec. Explicitly reject accidental pickle/process transfer; workers later reconstruct from canonical task inputs and call the factory inside their installed trusted operation. This is ordinary trusted in-process ownership, not authentication against arbitrary Python code.

Readonly inspection exposes context_digest, config_digest, normalized requirements, ordered actual input_bindings and original immutable batches. Private storage owns immutable slot records with global indices, actual session/bounds, row/input identity, values, field presence, coverage and knowledge classification. Own collection copies detach caller-owned mutable containers. Retain CanonicalBatch objects; compatible reuse requires the same original objects in the same order and exact context/config/version identity. New equal-metadata batches are not proof of equal payload. No global lookup/cache or metadata rewriting.

Closed families and complete-family views are:

| Requirement | Exact arithmetic and membership | Inspection units |
| --- | --- | --- |
| anchored_closes | ordered closes anchor..target | currency/share |
| true_ranges | ordered TR anchor+1..target, using H/L and previous closes; single-anchor warm-up tracks its close only | currency/share |
| price_moments | last N epoch closes, exact mean/population variance/centered target residual | currency/share, squared currency/share, currency/share respectively |
| high_extrema | target-including maximum of H over last N epoch slots | currency/share |
| low_extrema | target-including minimum of L over last N epoch slots | currency/share |
| simple_returns | latest one-slot C[target]/C[target-1]-1, explicit predecessor | dimensionless fraction |

Canonical prices are integer coefficients at declared scale. Inspection uses exact Fractions divided by10**scale for prices and by10**(2*scale) for variance. Never scale a dimensionless ratio or infer annualization. Private centered coefficients may remain exact integers. Each family view includes its dependency slot indices, exact complete values or None, status, expected/observed counts, ordered reasons, units and bounded evidence provenance. Nonready arithmetic is not exposed as a complete result. Expected counts refer to logical dependency slots, not tuple-value length. Partial per-slot facts may remain private.

Build only requested families. Missing unrelated H/L must not block closes/moments; malformed supplied canonical payload remains a call-level error. Missing required family on a supplied preparation is UNSUPPORTED_CAPABILITY, without silent global recomputation. None remains absent delivery and cannot be replaced by a prepared object; empty delivery remains observed empty. Preserve the published status/reason precedence, including close-only single-anchor ATR warm-up and absent-delivery reason suppression.

## Stable preparation mathematics and tests

For an admitted full moment window choose exact integer origin O. Retain N, sum(d), sum(d*d), d=C-O. Mean is O+sum(d)/N, population variance is `(N*sum(d*d)-sum(d)**2)/N**2`, and residual is C[target]-mean before rounding. Use Python integers/Fractions with explicit bounded operands: at N<=4,096/int64 coefficients, centered sums are below2**75, squared sums below2**138 and the variance numerator below2**150 in magnitude. Do not wrap fixed-width sums, convert large prices to Float64 before centering or clamp material negative variance. Typed arithmetic failure is distinct from unavailable source data.

Use original exact direct-window/pairwise-difference/Decimal references independent of the producer. Test first eligibility/seeds, N/min/max bounds, large offsets/tiny variation, old-window cancellation/eviction, gaps, flat/empty data, close-only fields, ATR's target-close independence, reset/carry overnight boundaries, revisions/action compatibility, UTC int64 arithmetic, cutoff equality and unknown/future knowledge. Snapshot eviction tests compare successive independently supplied windows; no public incremental state is implied. Corrections rebuild from explicit revised inputs.

Exercise actual producer admission and closed codec validation: duplicate/unknown/noncanonical JSON keys, booleans in integer fields, control/oversize labels, mismatched context/config/source/unit/action, unexpected/duplicate/overlapping slots and coverage contradictions, chunk limits and same-session distinct targets. Include copied-same-label/different-object reuse rejection, changed revision/config rejection, missing-family rejection, immutable alias ownership, unsupported state and serialization. Conditional EQ136 readiness JSON supplies expected cases; it does not substitute for executing these producer tests.

Compare independently prepared families against shared preparation using full projection P(preparation,family): context/config identities, ordered actual input bindings and the entire family view (exact values/units/dependencies/status/counts/reasons/evidence). Only outer requested-family lists/private storage shape are excluded. Numerical and quality identities cannot be projected away to manufacture parity.

## Purity and CI integration

The shared `tools/check_boundary.py` currently rejects unknown package directories before later steps. Admit only this reviewed intraday package and integrate its own strict AST/import/call/exact-dependency policy into the shared checker. Preserve fail-closed unknown-package behavior and all existing negative controls. New intraday controls include forbidden I/O/clock/credential/worker imports, file/JSON stream operations and executable aliases; document that static checks are not a Python sandbox. The shared check must work before intraday is installed, through source inspection rather than importing it.

Retain existing root jobs, source routing, original foundation operations and immutable historical workflow hashes. Append one exact reviewed block after the original foundation artifact upload in `packages.yml`, on its existing Windows/Linux matrix:

```yaml
      - name: Install intraday preparation package
        run: python -m pip install --no-deps --no-build-isolation -e packages/intraday
      - run: python -m pip check
      - run: python -B tools/check_intraday_boundary.py
      - run: python -B -m mypy --strict packages/intraday/src
      - run: python -I -B -m unittest discover -s tests/intraday
      - run: python -B tools/build_intraday.py
      - name: Retain verified experimental intraday artifacts
        uses: actions/upload-artifact@v4
        with:
          name: intraday-${{ github.sha }}-${{ matrix.os }}-attempt-${{ github.run_attempt }}
          path: dist/intraday/
          retention-days: 30
          if-no-files-found: error
```

Normalize only that exact literal block for the existing immutable historical comparison; require single presence and negative controls rejecting altered/missing/duplicate blocks or other unapproved operation changes. Do not replace old hashes or strip an arbitrary suffix. Intraday edits do not require a new root-family/routing schema. If actual qualification contradicts this design, record rework before altering it.

## Exact artifacts and installed qualification

All new outputs/repeat builds/install receipts live under `dist/intraday/` and owned isolated temporary roots. Do not put new archives in root dist: the foundation builder asserts exactly six root archives. Preserve the original foundation upload before creating the new output directory; upload intraday separately. Test first and repeated build invocations and output ownership. Do not recursively clean a shared output root.

Build source-pinned exact contracts0.0.4a4, features0.0.4a4 and intraday0.1.0a1 archives inside the isolated output tree. Verify repeat payloads, raw archive namespace/member types and RECORD before materialization, selected-SDist rebuild parity and exact Git source mappings. Four fresh installed forms: light wheel/SDist (contracts+intraday) and combined wheel/SDist (adds existing features). Install pinned third-party toolchain first, then selected local project archives without index fallback; run pip check, installed origin/file/metadata/RECORD inspection, isolated tests/examples and strict positive/exact-negative typing. Do not add source directories to PYTHONPATH for installed evidence. Preserve accepted core behavior with before/after probes in combined forms.

The existing channel is successful-main GitHub Actions source/artifacts, with actual hashes/access/expiry recorded; no stable registry, tag, GitHub release or service publication is inferred. Windows/Linux source/installed/archive evidence and actual main readback remain mandatory. No package implementation or installed result is claimed by this plan.

## Performance, documentation and accepted end state

Use EQ136's frozen small/large/skewed/long-history synthetic workloads, noise/adoption rule, seven post-warm-up samples and bounded memory/core-second criteria before timings. Compare separate preparation against shared compatible preparation with identical admitted facts/configuration and full P parity. Include validation, ownership/copy and inspection cost; retain failures and slower fallback. Record runtime/hardware/affinity/capacity at measurement, not an invented deadline or speed rank. Worker and complete source-to-sink baselines remain EQ140/EQ141; R18 owns wider scheduler/resource optimization.

The same story updates package README, API/examples/discovery, unit/precision/ownership decisions, build/delivery/version documentation and evidence-linked issue/PR/handoff. Accepted end state requires independently reviewed actual producer code, independent numerical and admission tests, measured preparation reuse/resource evidence, exact both-platform installed artifacts, current CI, publication/readback and lifecycle. Only implemented preparation is delivered in this story; EMA/RSI/ATR and band kernels remain separate. Start Ready -> In progress only after this exact public packet and actual dependency/input assessment pass. R18 remains after verified R17 completion.
