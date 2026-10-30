# Release 0 Architect rulings

Internal, synthetic, pre-release. Architect, 2026-10-30. Answers the five Architect requests listed under "Rulings needed from the Architect" in `docs/planning/RELEASE-MAP.md` (sections 1-5), plus the three earlier questions (section 6). Where a section says "Recommendation", the PO decides; the Architect rules only on technical state and design shape. Decided, pending owner review; the PO accepts or rejects and has final say on naming. Technical approach only; E9 and PO-1..PO-7 ratification stay with the owner. Basis: core main aa0b697; io 3c94be6 and workers 6c3123c read from `origin/main` (GitHub contents API). **[not verified]** marks what was not opened.

## 1. Catalogue stories S2-S8 (RL1-09)

Story definitions: `work/po-rulings-contract-catalogue-2026-10-29.md` (S1 extractor, S2 EF2+EF1, S3 drift gate, S4 link layer, S5 header cross-check, S6 packaged module with lookups, S7 core pointer, S8 `check_input`/`check_output`).

| Story | State on main | Evidence |
|---|---|---|
| S1 | merged | io #66; families EF3, EF4, EF5 (21 producers) in io `docs/contracts/catalogue/`; INDEX.md says "families present: EF3, EF4, EF5" |
| S3 (io part) | merged inside #66 | io `tools/check_contract_catalogue.py` (docs == package == regeneration), `tools/verify_contract_catalogue.py` |
| S3 (workers gate, core advisory hook) | not merged | no `catalogue` path in the workers main tree; no catalogue tool in core `tools/` |
| S6 part 1 (packaged data) | merged inside #66 | io `packages/io-contracts/.../catalogue/index.json` and `INDEX.md` |
| S6 part 2 (Python lookups), S8 | not merged | no `catalogue` or `check_input` symbol in io `packages/io-contracts/.../__init__.py`; #66 body lists both under "Not in S1" |
| S2, S4, S5, S7 | not merged | #66 body "Not in S1"; no EF1/EF2 producer directories; no workers or core change; open PRs in the three repos show none (io #15 #16, workers #42 #58 are older, unrelated) |

Recommendation: RL1-09 is S2, S3 remainder, S4, S5, S6 part 2, S7 and S8. Serial order on the io writer: S6 part 2, S8, S2, S4, S5; S3 workers gate and S7 are single-repo and run in parallel. DV1 catalogue pages (RL1-12) wait for the DV1 freeze text: the generator reads status only from a leading "Frozen as" / "Proposed freeze" (`work/architect-dv1-4-5-plan-2026-10-29.md`).

## 2. core_spread policy-label order (RL1-04)

Verified on main (`packages/features/src/equity_features/dv1/_core_spread.py` `_shape`, `build_core_spread_config`, and `_atr_simple_mean.py`, `_relative_log.py`, `_window_extreme.py`): every DV1 producer checks units, then cutoff, then policy label (INCOMPATIBLE_VERSION), then identity. core_spread differs only by running a parameter-shape check first (the policy value must be a string, else INVALID_CONFIG) and having no adjustment pair. The frozen contract wording (`DEFINITION_VARIANTS_CONTRACT_PROPOSAL.json` config_checks) says "unit and adjustment checks, cutoff, then the policy label, then identity" and omits the shape stage. Core #761 (not merged) rewrites the checks through shared `_config_check.py`; whether it keeps this order for core_spread is **[not verified]**.

| Option | Effect |
|---|---|
| A. Keep the order (shape, units, labels, cutoff, policy label, identity); amend contract wording to name a first "parameters" stage common to all producers | Docs only; no behaviour or fixture change |
| B. Move policy label before cutoff in all producers | Behaviour change in four producers, fixtures re-baselined |
| C. Make core_spread skip the shape stage | Behaviour change in one producer; breaks family symmetry |

Recommendation to the PO: A. It matches what is shipped, what `DV1_CORE_SPREAD_IMPLEMENTATION.md` states, and the "parameters first" stage order in the DV1 plan. Add one gate case per adjacent stage pair for core_spread, run in RL1-01's wording PR. PO rules (RL1-04).

## 3. Bars job-spec headers and the 39 cap (RL1-13, RL1-14)

13 headers (core `packages/contracts/src/equity_feature_contracts/_implemented.py` `BAR_IDS`): `session.bar.open`, `.high`, `.low`, `.close`, `.volume`, `.notional`, `.close_weighted_price`; `session.price.open_close_return`, `.range_fraction`, `.range_over_open`, `.close_location`, `.overnight_gap`, `.close_close_return`. The workers bump record (`docs/PRERELEASE_BUMP_DV1.md`) states a native `bars` job spec must list all 13; a 12-header spec is refused (INVALID_COMMAND). The thirteenth is `range_over_open`. Ruling: closed set, no subset; the list is `BAR_IDS`, and the workers builders and docs must read it from there (generated, not retyped).

Where "39" lives (all verified): (a) core `docs/api/REMOTE_ACCESS_POLICY.md` ("Instruments / sessions / features: 1 / 1 / 39 per job"); (b) workers `packages/service/src/equity_feature_service/jobs.py` lines 54 (`JobGrant`, `1 <= len(features) <= 39`) and 98 (`len(spec.features) > 39`), and `max_result_cells=3900` (39 x 100) at line 139; (c) workers `packages/service/.../schemas/remote-v1.1.schema.json` `maxItems: 39` (also v1 **[not checked]**). It is a per-job policy limit, not a count of built-ins. Only 24 built-ins are session batch ids (`SESSION_BATCH_IDS`), so a job cannot reach 39 today.

Recommendation to the PO: keep 39. Do not raise to 40 for the count. The cap is wire-schema text; changing it is a new schema version and a recorded policy revision (REMOTE_ACCESS_POLICY says wider limits need one). Decide the number once, with RL1-16, when ef5 and other families join the service. Recommend closing RL1-14 as "no change; documented" (PO decides).

## 4. Design approaches

### ef5 service/MCP exposure (RL1-16)

Facts: the service's job specs are session built-in specs (`SessionCommandSpec`, `JobGrant` features are `(str, str)` pairs, workers `jobs.py`); EF5 has a worker module (`equity_ef5.py`) but no service route (verified: workers `packages/service/src/equity_feature_service/jobs.py` imports only session command specs and the file list of `packages/service/src` has no ef5 module; the only `ef5` paths in workers main are `equity_ef5.py` and `tools/verify_ef5_worker.py`). Approach, primitives only:
1. Add a closed command table in the service keyed by producer id (`ef5.candle`, `ef5.structure`, `ef5.technical`), each naming the worker command, the input roles and the closed header set. Table is generated from the io catalogue index, so it cannot drift (needs S6 part 2).
2. Job specs list the whole closed header set per producer, as for bars. No subset, no defaults.
3. Admission reuses `JobGrant`; caps stay per job; `max_result_cells` is derived from the producer's header count, not from 39.
4. MCP adds nothing of its own: it wraps `client`, so exposure is a client method plus tool schema from the same table.
5. New wire fields mean a new remote schema version (v1.2); nothing in v1/v1.1 changes.
6. Refusals pass through the existing `contract_code` mapping. Remote cannot return types the client cannot decode: first confirm the notional-cell decode limit (`DECISIONS.md` row dated 2026-10-28, "Decided per PO (work/po-rulings-e1e2-followups-2026-10-28.md)", item (5)) is fixed or documented **[status not verified]**.
Owner-level only if it goes beyond primitives (named formations), per the EF5 stop-at-primitives reading.

### E9 unit-spelling migration (RL1-15)

Facts: the four aliases are still in code at main (`ef4/_rate_projection.py` lines 39-41: `trades_per_second`, `currency_per_second`, `fraction_per_second`; `ef4/_vwap.py` lines 43-44: `currency/share/second`); the DV1 a6 bump did not migrate them. The unit is inside `FeatureResult.metadata_json` and the evidence column content hash (`docs/ef4/EF4_LEDGER_APPLICATION.md`), so renaming changes identities. Approach:
1. One migration, one coordinated bump, in the DV1 order: core library META strings and a new contract version for the five affected headers (frozen files are never edited), then io (codec, catalogue regeneration, Parquet/DuckDB metadata), then workers goldens; re-pin PR per repo.
2. No dual reading: old bundles stay readable only through their recorded contract version. No alias translation layer, because translation would let two spellings hash differently under one id.
3. Gate first: a mapping table (alias to canonical, five ids) checked by a core tool; fixtures re-baselined by the independent expander, with before/after hash table as in the A5/A6 record.
4. Starts only after owner E9 ratification; the PO orders it last on the provisional reading (slash style).

## 5. Release id and EF label scheme (proposal; PO has final say)

Problem: `R<n>` is historical (`docs/releases/` holds R0-R18, R25 and R4_1; R19-R24 are absent, and those ids stay reserved, never reused); replan `EF1`-`EF8` has fixed goals in `docs/EQUITY_DELIVERY_REPLAN.md` (EF6 events/fundamentals, EF7 outcomes, EF8 policies); the parity reconciliation reused `EF6`..`EF14` for different stories (EF6 = DV1, EF12 = real-data enablement, EF14 = patterns).

Proposal:
1. `R<n>`: historical, closed, never reused.
2. `EF<n>`: only the replan's feature lines EF1-EF8 with the replan's meaning. No renumbering; EF5 stays delivered.
3. Named contract families keep their own id (`DV1`, later `DV2`...). DV1 is not "EF6". Recommend retiring the parity-doc label EF6=DV1 (PO decides; the label lives in the local `work/po-parity-reconciliation-2026-10-29.md`).
4. Parity stories EF9-EF14 from the reconciliation get the prefix `PX` (`PX-09`..`PX-14`, keeping their old number as the suffix) so none collides with a replan EF id; a one-table mapping lives in `docs/planning/`.
5. Release ids in the new loop: `RL-<nn>` zero padded (`RL-01`), directory `docs/releases/RL-01/`, story ids `RL-01-<nn>`. The hyphen and padding keep it visibly distinct from `R1`.
6. Cross-reference rule: a PR title or story names at most one of release id, family id.

## 6. Recommendations for the three earlier PO questions

Source: the Architect report on PR 765 (`docs/architecture/EXISTING-SYSTEM-AUDIT.md` rows for ADR-1/2/3/4 and the three PO rulings it asked for).

1. ADR-2 range pins: defer. Exact pins cost a known cascade handled by the DV1 discipline (SYSTEM-DESIGN section on pins). Revisit when a second consumer or a third repo bump per week makes the cascade the bottleneck. Fix the stale ADR-2 context now (docs only).
2. ADR-3 and ADR-4: ADR-3 (matrix) after the CV1 generator, because the coverage table already needs the same output-to-source fields; ADR-4 (entry points, io-sdk only, S/M) after RL1 and before any claim that third parties can add adapters.
3. Docs-only fixes to stale ADR-1/ADR-2 text and a COMPATIBILITY current-state table: yes, one docs PR, status stays "proposed".
