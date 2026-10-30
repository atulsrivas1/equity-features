Source: work/po-rulings-contract-catalogue-2026-10-29.md (Product Owner ruling record, 2026-10-29). Copy made 2026-10-30 as a verbatim copy; internal, synthetic, pre-release.

# PO rulings: contract catalogue (2026-10-29)

Scope: internal, synthetic, pre-release. Input: architect-contract-home-2026-10-29.md (sections 0-9). Owner delegated the decision to the Architect; hard requirement: contracts easy for clients to consume.

## 1. Recommendation: APPROVED with modifications

Approved: core stays the authority (frozen bytes and paths untouched). A generated catalogue lives in io, ships inside `equity-feature-io-contracts` as module `equity_feature_io_contracts.catalogue` with data under `catalogue/`, and is mirrored as `docs/contracts/catalogue/` in io. Docs and package are the same bytes, gated equal by a drift gate. Options A, B, E rejected; D allowed only as the EF6+ authoring path.

Modifications:
- M1. Packaging is in the first release, not optional (S6 is core scope). There is no docs-only interim release of the catalogue.
- M2. The "same bytes" gate is a hard requirement: docs copy equals package data, and both equal a regeneration from core. Both checks run in one gate command.
- M3. Every page and every JSON carries: contract_version, status (frozen/proposed), source core path, core commit, sha256 of LF bytes, and the line "Authority: core frozen contract; on conflict core wins and the gate fails."
- M4. "Unparsed" top-level keys are listed, never silently dropped. A non-empty unparsed list for a frozen family fails review unless the PO has accepted it in writing.
- M5. EF1 is in scope (confirmation (c) of the Architect: yes), but EF1 may ship in a later catalogue release than EF3/4/5 if S2 slips; the catalogue version records which families are present. EF1 must not delay EF6.
- M6. The core advisory hook (script by path, skipped when io checkout is absent) is accepted. No core dependency change.
- M7. No hand-edited generated files (header "GENERATED, do not edit"; gate enforces).

## 2. The three confirmations

1. Core is authority on conflict: CONFIRMED. The gate fails; the catalogue is never patched to match behaviour.
2. io-contracts prerelease version bump (minor) acceptable: CONFIRMED. Internal, pre-release, so no compatibility promise is broken. Must pass `verify_versions.py`; changelog entry required listing producers touched.
3. `check_input` / `check_output` structural only: CONFIRMED. They never compute, never replace library refusals, cite the catalogue rule that failed, and the library stays authority. Any semantic/numeric check is out of scope and needs a new PO ruling.

## 3. Story order, priority, parallelism

Priority relative to EF6: EF6 contract freeze and EF6 stories are NOT blocked and keep priority. Catalogue work runs as a parallel lane; it never gates an EF6 PR. EF6 follows architect section 7 (authoring discipline: pure key names, two mandatory md sections). EF6 catalogue pages are generated in the EF6 freeze PR only if S1+S3 have merged by then; otherwise in the first catalogue PR after.

Order (client-first):
1. S1 extractor + schema + EF3/EF4/EF5 (io)
2. S3 drift gate (io, then workers, then core advisory hook)
3. S6 packaged `catalogue` module + index.json + lookups, minor bump (io-contracts)
4. S8 `check_input` / `check_output` (io-contracts)
5. S2 EF2 + EF1 families (io)
6. S4 link layer (io docs, workers docs)
7. S5 header cross-check test + IO_V1 one-line cross-reference (confirm zero golden/hash churn first)
8. S7 core pointer README note (core, markdown only)

Note: S6 and S8 move ahead of S2 because they deliver client value on already-extracted families; S2 only widens coverage.

Parallelism (no two writers on the same files):
- S1, S3 (io part), S6, S8, S2, S5 all touch io catalogue/tools/io-contracts files: SERIAL on the io writer. Exception: S2 may run in parallel with S6/S8 only if S2 writes solely new per-family map files and generated EF1/EF2 output, and S6/S8 do not touch the extractor core; coordinator must check file lists before allowing it. Default is serial.
- S3 workers part and core advisory hook (separate repos) may run in parallel with io stories once the io gate script is merged.
- S4 (workers docs, io docs/api) may run in parallel with S6/S8 provided io docs/api is touched by S4 only and the catalogue directory by the other.
- S7 (core markdown) is independent; may run any time after S1 is merged.
- EF6 worktrees (ef6-0, ef6-io, ef6-workers) are separate lanes; catalogue stories must not edit files EF6 PRs touch (EF6 docs, `_ef6*` modules). S5's IO_V1 edit is the only shared-risk file; schedule it when no EF6 PR touches IO_V1.
- Each story: fresh independent reviewer per PR per the working agreement.

## 4. Acceptance criteria: client ease

A. Find in minutes. Using only the installed `equity-feature-io-contracts` wheel or the io repo, a new client locates any feature's input and output contract in under 5 minutes by (i) `INDEX.md`, (ii) `catalogue.producers()`, or (iii) `catalogue.by_feature_id(feature_id)` from a result column. Verified by a cold-read test: a reviewer who did not write it finds three named producers (one per family EF3/4/5) using the INDEX only, timed.
B. Predictable paths. `catalogue/index.json`, `catalogue/<producer_id>/input.{json,md}`, `output.{json,md}`, `catalogue/INDEX.md`. Paths guessable from producer_id.
C. Read in minutes. `input.md` states, in fixed order: roles/slots and nullability; batch kind and required columns; reference fact kinds and schemas; config parameters, defaults and who supplies them; coverage/adjustment/scale/known_at rules; input-stage refusal codes; link to the adapter API page. `output.md` states: feature ids with dtype, unit, grain, order; quality vocabulary and readiness; evidence bounds; reasons reached; headers as `FeatureHeader` values. Each page fits one screen of headings; no page requires opening the core JSON.
D. Validate in minutes. `check_input` and `check_output` run on a small example in the docs with copy-paste code, return a result citing the failed catalogue rule, and need no core or workers import. A client can validate a sample input and a sample output in under 10 minutes following the quickstart in `CATALOGUE.md`.
E. Input contract states what an adapter must supply (shape, kinds, columns, nullability, config), never which provider supplies it. Zero provider names in catalogue pages, JSON, quickstart, or error messages; a test greps for this.
F. Machine and human equivalence: JSON and md are generated from the same data; gate verifies.
G. Versioning visible: `catalogue.version()` returns catalogue version plus per-producer contract_version; changelog lists producers touched per release.
H. No semantics invented: every field traces to a core key; unparsed list present and empty (or PO-accepted) for shipped families.
I. Zero change to frozen bytes; `check_boundary.py`, `check_extraction.py`, evolution file unaffected (verified, each story states the result).
J. Dependency direction: the module imports only io-contracts types and packaged data; no import of core or workers.
K. Adding EF6 costs one extraction map and no new client code.

## 5. Wording constraints (all catalogue artefacts, docs, changelog, PR text)

- State plainly: internal, synthetic, pre-release. No production, customer, or commercial-readiness claims; no stability promise beyond the version rules above.
- No provider names or provider concerns anywhere. Input contract describes what an adapter supplies; outputs describe what a consumer receives.
- Use "contract", "producer", "feature id", "adapter" consistently; use plain words, no marketing language.
- Generated files carry the GENERATED header and the authority line (M3).
- Do not describe check_input/check_output as validating correctness of values; call them structural checks.

## 6. Implications for the coordinator

- Assign EQ numbers; record these rulings in HANDOFF.md.
- Bump of io-contracts is minor, prerelease, announced in S6 PR.
- Report back only if: unparsed keys appear in a frozen family, S5 shows golden/hash churn, or an EF6 PR collides on a file. Otherwise decide routinely.
