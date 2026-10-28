# EF release acceptance checklist

Single pass/fail list for accepting an EF release (EF1 to EF4 and later). A release is accepted only when every item is PASS with evidence linked; any FAIL or "not run" blocks acceptance. "Delivered" is not "accepted" (see STATUS.md). Mark each item with date, commit SHAs of core, io and workers, and the evidence path. Commands run from the core repo root unless an item names another repo (for example `tools/ef1_results_demo.py` is in `..\equity-feature-workers` and `tools/check_extraction.py` is in `..\equity-feature-io`); sibling repos are `..\equity-feature-io` and `..\equity-feature-workers`.

Record: release ____ core SHA ____ io SHA ____ workers SHA ____ date ____ tester ____

## 1. Build
- [ ] 1.1 All three trees clean and at the recorded SHAs (`git status`, `git log -1`).
- [ ] 1.2 Fresh venv per CONTRIBUTING; `pip check` clean.
- [ ] 1.3 All 8 packages build as wheel and sdist; versions bumped from the previous release (the bump is owed for EF2 to EF4); `docs/RELEASE_INTEGRITY.md` repeat-build equality recorded.
- [ ] 1.4 `tools/check_boundary.py` exits 0 (baseline 2026-10-27: fails on `import base64` in `ef1/_reference_close.py` and `_venue_status.py`; fix branch `fix/boundary-base64` unpushed).
- [ ] 1.5 `mypy --strict` result recorded; if not clean, each remaining error is owner-waived in DECISIONS.md (baseline: 55 errors in 10 files).

## Pre-merge command (per PR, no CI)
Run `python tools/pre_merge_check.py` from the core root in the pinned venv (CONTRIBUTING.md: requirements-dev.txt plus editable core packages). It runs check_boundary, check_equity_delivery_replan and every `tools/verify_*.py` including `verify_ef4_fixtures`, prints PASS/FAIL/SKIP and exits non-zero on any FAIL. Three checks need installed wheels, io wheels or jsonschema and run with `--installed`; `verify_quickstart` skips if its ignored scratch folder `work/eq132-quickstart-Windows` exists. The script prints, but does not run, the manual commands: io `check_extraction.py` and `mypy --strict packages/duckdb/src`, and the four workers EF4 `--refusals` drivers (baselines tape 73/75, quote_vwap 80/80, path_efficiency 39/39, projections 114/114). Record the output in the PR. There is no CI workflow in this repo. Past EF4 PR verdicts: `docs/qa/EF4_PR_REVIEWER_VERDICTS.md`.

## 2. Verify scripts (installed wheels, not editable)
- [ ] 2.1 PASS: verify_imports, verify_compatibility, verify_session_examples, verify_quote_examples, verify_history_examples, verify_context_examples, verify_timing_examples, verify_diagnostic_examples, verify_registry, verify_release_policy, verify_quickstart.
- [ ] 2.2 PASS from installed wheels: verify_public_typing (rejects editable installs), verify_supplied_worker_examples (needs io wheels), verify_remote_transport (needs `jsonschema`; add to the dev requirements or waive).
- [ ] 2.3 Output ownership manifest `docs/plans/equity-output-ownership.json` checked against every new header (EF3: 2 entries without header, 36 headers without entry; EF4: not checked).

## 3. Unit suites
- [ ] 3.1 Core: `python -m unittest discover tests/unit` zero failures (baseline 1075 run, 1 FAIL: stale count in `test_purity_audit`; fix branch `fix/purity-audit-count`).
- [ ] 3.2 io: 48 of 48 (`unittest discover -s tests`).
- [ ] 3.3 workers: all pass in an installed (non-PYTHONPATH) environment; the 3 subprocess failures at baseline must pass with installed wheels, not be waived as environmental.
- [ ] 3.4 Every EF2/EF3/EF4 family has at least one unit test file, or an owner decision that waives unit tests for it with the reason recorded (today none exists; see EDGE_CASE_MATRIX.md). Because the standing policy is no new automated tests, this item needs an owner ruling or waiver before it can PASS.
- [ ] 3.5 Count of U rows in `EDGE_CASE_MATRIX.md` is zero, or each U row has an owner-signed waiver.

## 4. Demo census
- [ ] 4.1 `tools/ef1_results_demo.py` with default sibling paths: all cases pass (EF2 304/304 baseline; EF3 346/346; EF4 297/297).
- [ ] 4.2 `tools/check_extraction.py --core-root <core>` exits 0 (census: every contract fixture and refusal recipe has a demo).
- [ ] 4.3 Refusal census: matched count equals recipe count, or each deviation is a ruled, documented one (EF4: 306 of 308; RF18, RF35 ruled E6).
- [ ] 4.4 Refusal recipes with no worker path are listed and checked at library (EF4: RF41, 42, 43, 54, 55, 60, 65, 66, 69).
- [ ] 4.5 Generator fixtures and random-fixture claims (EF4 G01 to G03; 1000 seeded per I1/I2) re-run by the tester, not author-reported.
- [ ] 4.6 Browser walkthrough: all runs, 0 failed, display defects listed and closed.

## 5. Hand recompute (independent)
- [ ] 5.1 Tester recomputes a sample by hand or by an independent script outside the repo code: at least 10 percent of result fixtures per contract, stratified (one per output family, one near-tolerance, one exact-zero, one refusal).
- [ ] 5.2 Recompute includes at least one case each for: split/action basis, zero volume, empty window, single bar, equal timestamp, early close.
- [ ] 5.3 Any mismatch is a defect filed before acceptance; negative control (deliberately broken kernel) shown to fail the script.

## 6. Determinism across 4 install forms
- [ ] 6.1 Wheels only, sdists only, wheel-core plus sdist-others, sdist-core plus wheel-others: fresh venv each, `pip check` clean.
- [ ] 6.2 Same demo set in each; canonical `content_sha256` identical across all four for every result case.
- [ ] 6.3 Run twice per form; the two runs identical (determinism, not only parity).
- [ ] 6.4 Installed run is standalone: no reads from the source tree (known EF1 to EF4 limit: oracle JSON and a contract file are read from source) or the exceptions are listed.

## 7. Linux qualification
- [ ] 7.1 WSL Ubuntu (or CI Linux) has python3-venv and pip (owner action outstanding).
- [ ] 7.2 Steps 1 to 6 re-run on Linux; `content_sha256` equal to the Windows values for every case (bit equality; any tolerance fallback needs an owner ruling, see parity policy in EDGE_CASE_MATRIX.md).
- [ ] 7.3 Line-ending rule (`.gitattributes`) decided and fixtures hash identically under both endings.

## 8. Real-source parity
- [ ] 8.1 Real-source demo for the release's families (EF1 done for one symbol and day; EF2 to EF4 not done): real data labelled real, synthetic parts labelled synthetic.
- [ ] 8.2 Result equals an independent exact query on the same source rows; source file unchanged.
- [ ] 8.3 Coverage includes the awkward real rows (sub-second timestamps, a third of rows were refused for second precision in EF1), halts and early close days if the source has them.
- [ ] 8.4 No market data committed to any repo.

## 9. Rights
- [ ] 9.1 Dataset rights confirmed in writing by the owner for every dataset used in 8.
- [ ] 9.2 Fixtures are synthetic or explicitly licensed; no proprietary formulas, code or thresholds copied; private audit closure material not copied (opaque ids only).
- [ ] 9.3 Licence files and dependency inventory (`docs/DEPENDENCY_INVENTORY.json`) current for the new packages.

## 10. Process and docs
- [ ] 10.1 Every PR in the release has a recorded independent review (verdict artifact, not only a session note) and merged state read from GitHub.
- [ ] 10.2 Owner has reviewed the shared amendment rulings (EF3 R1 to R9; EF4 E1 to E9) and coordinator decisions in DECISIONS.md.
- [ ] 10.3 Known-limit list in the delivery evidence doc is current; each limit is fixed, waived or scheduled with an issue.
- [ ] 10.4 STATUS.md, HANDOFF.md, CHANGELOG updated; retrospective written; token ledger updated.
- [ ] 10.5 Acceptance stories closed with child evidence audited (EF4: EQ-158, 159, 160, 161, 162, 172, 163; EF3: EQ-153 to 157, 241; EF2: EQ-152).

## 11. Owner demo and sign-off
- [ ] 11.1 Owner shown the browser demo from a fresh start (stop stale servers first, for example 127.0.0.1:18400).
- [ ] 11.2 Owner states acceptance in chat, per release; recorded in DECISIONS.md.
- [ ] 11.3 Publication/version tag only after 11.2; no merge or publish is done by the tester.

Result: ACCEPT only if every box is checked. Otherwise list blockers: ____________________
