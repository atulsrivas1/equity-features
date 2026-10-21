# EQ167 first anchor slice — independent source review

Reviewer: `/root/ef1_library_review`, fresh automated local reviewer, distinct from implementation author. October 20, 2026. This is a pre-PR dirty-source review, not human review, executable validation, exact-final-commit review or release acceptance.

Reviewed worktree: `[isolated core checkout]`; base HEAD `e3c5e55077dabcf64a3e11f1210ac6f3a923a2b3`.

## Disposition

**Changes required:** one P2 arithmetic admission defect. No tests, imports, builds, database access, data scans, benchmarks or GitHub mutations were executed. A final-head recheck and actual numerical/artifact/integration qualification remain mandatory.

## Finding LIB01 — P2: reject nonpositive actual notional independently of optional OHLC

Location: `packages/features/src/equity_features/ef1/_anchor.py:162–167` (also admission at line57).

Trigger: use bars_actual_notional, complete positive-duration scope, eligible matching anchor proof, a BAR row with positive volume3 and actual_notional=-1 (or0), and omit optional open/high/low/close columns. These are structurally admitted canonical columns. Existing `validate_batch(..., required_fields=())` checks actual-notional range only inside the branch where both low and high are supplied (`packages/contracts/src/equity_feature_contracts/validation.py:155–159`). Its optional-OHLC behavior consequently does not reject this row. The new accumulator adds the nonpositive amount without an independent guard, and checked_decimal128 permits signed/zero coefficients. This produces AVAILABLE negative/zero exact notional and negative/zero VWAP for positive shares, contradicting the positive traded-price arithmetic and compatible actual-notional requirement. This conclusion is from direct source tracing, not an executed reproduction.

Minimal correction: reject supplied actual_notional<=0 for every positive-volume BAR independently of optional OHLC presence; retain the existing absent/null notional unavailable behavior and zero-volume zero/absent rule. Use the established typed malformed-input error. Add independently authored controls for absent OHLC with negative/zero actual notional and positive volume, and a positive actual-notional/absent-OHLC control if that supported shape is intended. No canonical-contract package widening is necessary.

## Coverage and observations

Read all four new EF1 Python modules, complete new unit-test file, example, feature/API documents, package/version diffs, frozen contract ledger and admission records, and relevant existing CanonicalBatch/validation/config/result implementations. Read owner-supplied replacement AGENTS, primary coordinator agreement, public-development/handoff/project-knowledge/delivery/knowledge workflow documents. Current Project admission and owner sequencing records remain coordinator-owned; this reviewer performed no independent GitHub status refresh and makes no lifecycle claim.

The slice uses exact wide integer sums, Fraction division with one float conversion, strict anchor start<C, actual-notional BAR arithmetic instead of close*volume, original complete input metadata/config digest/C/K/E, explicit role order/identity checks and separate missing/covered-empty/zero behavior. Canonical default registry is unmodified. It supports anchor only and rejects other producers; it does not complete all EQ167/EF1 scope. Reconstruction intentionally invokes the existing AvailabilitySpec semantics; it retains original unknown/future source metadata and marks reconstruction mode rather than claiming causal known-at admission.

The authored tests contain hand-derived3300/3/11 arithmetic and actual-notional proxy counterexample, missing primary/proof, coverage, knowledge/bounds/auction/order/hash/version/identity and overflow cases. They were inspected but **not run**. No execution result is inferred from their presence.

The new code performs no external I/O, wall-clock lookup, credentials, scheduling or publication. Public source/docs/example inspected contain synthetic identities and original formulas; no local N: source paths, actual market rows or raw private chat were found in the changed public surfaces. This is source inspection, not a rights attestation for future source acquisition.

## Documentation and compatibility notes

The planned features0.0.4a5/contracts0.0.4a4 pair remains unqualified. Because old kernels derive backend_version from the package version, installed legacy-result metadata changes with the version bump; public API docs correctly disclose this and require worker companion exact-version admission and legacy numerical qualification. No a4 result-byte parity or artifact/platform compatibility claim follows from this review.

`docs/ef1/CONTRACT.json:3` still says proposed_not_frozen_not_executed and retains a remaining_freeze_blockers phrase while the new API links call it frozen. Preserve the exact reviewed numerical contract bytes until the coordinator chooses the minimal explicit status wrapper/erratum or reviewed update. Reconcile the publication wording before presenting final public contract state; this is a coordinator documentation note, separate from LIB01.

## Reviewed file identities (SHA256)

- `_anchor.py`: f6821377a8541cb1ae1db6157fd4de1a2656b88eebe9de86eeaf2e3598bc051c
- `_context.py`: eeb26c97c8daf39e599835846f25e05fff1d8ad1338c8ab1ba980c95e1b822ab
- `_definitions.py`: 37cdd50675604dec01093c2114c52cc5e82ea1f7e3c3bd73a9300fc2de076449
- EF1 `__init__.py`: ba5891ab03e7096f22d65feba6d9d1d4592f1b60fd18554345e02963d8b1f728
- `tests/unit/test_ef1_anchor.py`: 11ba99201fa0c9e0e70635247bdea1f11c0ed452810cfb3b6200ec09718136e8
- `examples/ef1_anchor.py`: e6840a436643ec0ccccd43abc2878af58ff4a99cc83548bee9ab67c1366c0d6a
- `docs/ef1/CONTRACT.json`: 02940da0c4663bbced050ac551e7fbafe2a1da1534e4c6fa5c87eaf90d420076

Source corrections require relevant renewed independent coverage. Fresh independent PR review/current CI, installed both-platform artifacts, three-layer numerical composition, separate output publication/readback, browser demo and full inventory release gate remain outstanding.

## Successor source recheck — October 20, 2026

LIB01 is **resolved by source inspection** at `_anchor.py:130–138`: each positive-volume BAR with supplied actual_notional<=0 now raises INVALID_SCHEMA independently of optional OHLC. New test `test_lib01_actual_notional_admission_is_independent_of_optional_ohlc` covers negative, zero, valid3300 and null notional with all OHLC columns absent, including independent volume readiness. No test execution occurred.

Reviewed the complete current tracked diff:25 modified files at this observation, plus original new anchor source/docs/test/example and new typing caller. Package maps, exact featuresa5/contractsa4 probes, external consumer metadata and installed public typing now distinguish the two versions without weakening exact admission. Reviewed new positive caller and three independently invalid EF1 call shapes in installed typing verifier. Existing frozen EQ142 source is untouched. Root-owned subsequent I/O/worker source-pin migration is not yet reviewed or accepted here.

### LIB02 — P2: current explanations combined qualification still rejects the a5 core it now builds

`tools/build_explanations.py:24` now selects features0.0.4a5. Its combined qualification executes `examples/evidence_explanation.py`, whose actual compute_trades result reports a5. Unchanged `packages/explanations/src/equity_feature_explanations/_explain.py:296` requires backend_version exactly0.0.4a4, so explain_result raises unsupported_version. The analogous receipt guard at183 also retains a4-only admission. The changed shared build table thus cannot qualify its selected current core in the existing supported synthetic composition. This is direct call-path source tracing; no execution is claimed.

Minimal correction: explicitly decide and implement the bounded legacy-producer a5 compatibility route for explanations, retaining supported a4 replay if required, plus corresponding independent version rejection and actual producer composition controls. Coordinate any package version/source-identity effects; do not blanket-admit arbitrary backend versions or EF1 IDs that explanations does not implement. Alternatively retain an explicitly separate historical a4 qualification route without claiming it qualifies the a5 package. The current changed builder and unchanged runtime gate are incompatible.

The initial possible quickstart compatibility concern was investigated and **not filed**: tools/verify_quickstart.py deliberately installs the fixed accepted_main artifacts in EQ-132_INPUTS.json, so its a4 probe belongs to historical finite artifact replay. It must not be blindly migrated to the dirty a5 candidate. Likewise historical receipt literals are not automatically defects; current-source compositions require actual call-path inspection.

Coordinator's explicit source-authoring freeze receipt binds the retained candidate ledger bytes and supplies its reviewed state. This resolves the practical status-wrapper ambiguity without silently editing the reviewed ledger; public API prose should make the wrapper authoritative.

Successor reviewed identities SHA256:

- `_anchor.py`: 8ad3f3fb1d0e46ccc7e807e57265a2686dd6923fd5566b12fe3c86c2795ec83e
- `tests/unit/test_ef1_anchor.py`: c53734e3e89258314a9e0b346f80354f9f6fe16ff93c1dc4132abec9a3f2096f
- `tools/verify_public_typing.py`: 4be8be6712ba90932aea462a53a93843b9083cad5f9d5bfd018c17a808e17922
- `examples/typing/ef1_anchor_positive.py`: a6f535c18b04d8a22a6b7aeac06f62d72124496a31ba10129f225716e85af08f

Verdict: anchor arithmetic correction accepted statically; **full-current-source approval remains pending LIB02 and root-owned explicit cross-repository compatibility/pin work**. No imports/tests/builds/benchmarks/DB or GitHub changes performed. Final committed-head independent review, executable numerical/artifact checks and release gates remain separate.

## LIB02 successor and bootstrap-source verdict — October 20, 2026

**LIB02 resolved by independent static review.** The explanation companion now declares0.1.0a2 and admits exactly the closed python-exact backend set {0.0.4a4,0.0.4a5} in both factory and direct-record validation. Original canonical0.0.4a4 records/formulas and closed built-in-ID lookup remain unchanged; no new EF1 explanation capability is implied. This is mathematically sound as a bounded metadata compatibility declaration because the changed core distribution retains existing legacy numerical implementation, while the feature package version intentionally changes its backend metadata. Independent hand-authored full legacy trade declarations cover both versions with equal values/quality, distinct actual result fingerprints and bound receipts; futurea6 refusal covers factory and direct construction. The existing actual optional producer test now preserves and asserts its real version. Actual execution is still required to establish passing compatibility.

Reviewed package metadata/README, both guard changes, entire new tests and example diff, and current build cohorts. The explanation/build pilot/evaluation maps select a2; R9 inherits the shared map. The actual example declares the installed producer version without rewriting its result. No additional blocking defect found in this corrected mathematical/explanation bootstrap subset.

**Approve coordinator's first bootstrap core source commit, limited to the reviewed feature/anchor, explanation companion, independent authored tests/examples, common version/build/typing probes and source-safe admission/API/math documentation.** This is source-authoring approval only. Exclude root-owned prospective provenance package/preflight/tests, provenance/conformance/R10 builder and workflow pin changes from that bootstrap commit. Placeholder strings are not approved for push. The coordinator must verify exact staged contents; no full-tree or unexecuted CI approval is granted.

Root-owned later provenance/pin changes require their own independent review at actual reviewed IO/worker source identities. Their necessity is acknowledged, not waived or retrospectively approved. Final exact committed bootstrap head must also receive renewed source identity coverage before it is presented as a reviewed final PR head. Runtime, numerical, installed both-platform artifacts, current-head CI and release gates remain outstanding.

Additional successor SHA256:

- explanations `_explain.py`: 7f0d3fdf0b0d4085f2be4deb00c015a655d28f4a699188341cf5f0f2ff110022
- explanations `pyproject.toml`: 2f1c865ec8729ee2e3f657435de9944d915f5b7f0ffaf5fd9bf92c8801025795
- `tests/explanations/test_explanations.py`: be280b37312a50b8b19ebe7d433be895d6374d7002c14b4109a665c37c28748f
- `examples/evidence_explanation.py`: 1009ed4ca18c93994f1af7a5f20fade30a5e54fff4549ec40e3899a2a5681e1f

No tests/imports/builds/benchmarks/data/DB/GitHub operations performed during any portion of this review. Only the local owned review report was written.
