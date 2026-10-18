# Contributing to Equity Features

Start with a numbered issue and agree its scope before implementation. Use supplied synthetic or explicitly licensed inputs. Calculations remain source-independent: fetching, credentials, files/databases, scheduling and publication belong in their owning adapters/workers, not calculation packages. Define formulas, units, timing, initialization, coverage and edge cases before numerical code; use independent expected fixtures. Performance changes require measurements and result parity.

## Choose the right path

- Want to use the library? Follow the [minimal delivered-wheel quickstart](docs/QUICKSTART.md), then the existing example catalog. Its isolated three-wheel environment is different from contributor setup.
- Want to change code? Link a scoped issue, inspect the relevant normative contract and tests, then propose a small patch with independent expectations.
- Want to help without code? Take a scoped documentation/navigation task, report a reproducible synthetic defect, or review a proposed contract. Record what you actually checked.
- Optional I/O, workers and research retain their own implementation owners. Account/profile administration belongs with the setup owner. A link does not transfer research/data rights or ownership.

## Source contributor setup

Use a fresh checkout and an absent .venv directory. Prerequisites are Git, CPython3.12 x64 and network access to the pinned public development requirements. Confirm Python version/implementation/architecture before creating the environment. These instructions install the full development toolset, including optional NumPy/PyArrow tooling; those are not new core runtime dependencies or the minimal end-user path. No paid market-data credential is needed.

For a new public source checkout:

```text
git clone https://github.com/atulsrivas1/equity-features.git
cd equity-features
python -c "import platform,struct,sys; assert platform.system() in ('Windows','Linux') and sys.implementation.name=='cpython' and sys.version_info[:2]==(3,12) and struct.calcsize('P')==8 and platform.machine().lower() in ('amd64','x86_64'); print(platform.system(),platform.machine(),sys.version.split()[0])"
```

That prerequisite check reads the selected interpreter; it does not provision Python or establish delivered-package qualification.

From the repository root on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pip install --no-build-isolation -e packages/contracts -e packages/features -e examples/external_consumer
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe tools/verify_imports.py
```

On Linux:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pip install --no-build-isolation -e packages/contracts -e packages/features -e examples/external_consumer
.venv/bin/python -m pip check
.venv/bin/python tools/verify_imports.py
```

The selected `python` must already be CPython3.12 x64 with venv support; environment provisioning is not performed by these instructions. Install the two local core distributions together so pip does not substitute an unrelated unpublished internal distribution. Use the environment's explicit Python for every subsequent command; do not rely on shell activation. Keep assertions enabled. Stop on an existing environment or failed command and inspect the failure rather than deleting unrelated work or retrying unchanged commands automatically. Editable source checks do not qualify a delivered artifact.

## Match checks to the work

Run all existing independent reference verifiers and import smoke before a PR. Session, quote, history, context, timing and diagnostic verifier scripts are stdlib equation/reference checks; they are not the production calculation implementation or a general prose/link validator. Documentation-only work also needs explicit source/anchor preservation and manual destination checks for changed links. The current Documentation workflow verifies UTF8/planning/reference constraints but does not validate every Markdown link.

For the six independent design/reference checks, run each command with the explicit environment interpreter. Windows PowerShell commands are below; on Linux replace `.\.venv\Scripts\python.exe` with `.venv/bin/python`.

```powershell
.\.venv\Scripts\python.exe tools/verify_session_examples.py
.\.venv\Scripts\python.exe tools/verify_quote_examples.py
.\.venv\Scripts\python.exe tools/verify_history_examples.py
.\.venv\Scripts\python.exe tools/verify_context_examples.py
.\.venv\Scripts\python.exe tools/verify_timing_examples.py
.\.venv\Scripts\python.exe tools/verify_diagnostic_examples.py
```

For core Python changes, follow the current Foundation workflow: unit discovery at tests/unit, check_boundary.py, strict mypy over contracts/features/typed callers, and relevant synthetic examples. Use the explicit .venv Python on your OS. Keep numerical fixtures independent of the implementation. Optional packages have their own workflow/check topology; discuss scope with their owner instead of adding them to core.

The corresponding core source checks are:

```powershell
.\.venv\Scripts\python.exe tools/verify_compatibility.py
.\.venv\Scripts\python.exe -m unittest discover -s tests/unit
.\.venv\Scripts\python.exe tools/check_boundary.py
.\.venv\Scripts\python.exe -m mypy --strict packages/contracts/src packages/features/src examples/in_memory_adapter.py examples/external_consumer/src examples/typed_caller.py
```

Maintainers must still verify exact current CI and applicable fresh installed wheel/sdist/absence/RECORD/source/current-artifact and default-branch evidence. A green source test, successful editable import or merged PR alone is not release acceptance. Existing build/delivery documentation identifies those gates; do not relabel a local check as their completion.

## Review, support and response target

Keep PRs small and linked to numbered issues. Describe the concrete behavior, mathematical/API impact or explicit no-impact decision, actual validation/failures and limitations. Update relevant API/examples/decisions/changelog/knowledge/handoff and issue evidence in the same story. See the [review policy](docs/CODE_REVIEW.md) and [delivery gates](docs/PUBLIC_DEVELOPMENT.md). Follow the exact Backlog → Ready → In progress → Code review → Test → Ready to release → Released → Done lifecycle. A completed separate permitted final-head review and findings disposition are required; self-review, a review request or CI alone is insufficient.

Use the public bug/proposal templates for nonsensitive supplied-data reports. Include exact versions/channel, expected versus observed behavior and a minimal synthetic reproduction. Keep credentials, private data and unsupported rights out of issues/logs. For security reports, follow [SECURITY.md](SECURITY.md): use private vulnerability reporting when enabled, otherwise request a private channel without disclosing sensitive details publicly. This guide does not assert that private reporting is enabled.

Maintainers aim to triage contributions during the existing weekly active-work review, capacity permitting. This is a best-effort target, not a guaranteed acknowledgement, review/merge deadline or measured response statistic. No automatic reminder or invitation is created. Library, I/O, workers, research and setup/account requests retain the routing above.

## Rights and actual contributor credit

Contributions are licensed under Apache-2.0. By submitting a contribution, confirm that you have the right to contribute it under that license. Keep all supplied examples synthetic or explicitly licensed; public code licensing does not grant market-data rights.

External contributors keep their actual identity and provenance; do not impersonate the owner. Propose scoped changes through issues/patches or a linked PR. Maintainer integration follows the existing owner author/local-committer and no-Coauthors policy. Preserve actual contribution and review provenance in the issue/PR record; use acknowledgments with consent, not invented credit or claims of human review. Changing the integration identity policy requires its own explicit decision.

## Starter opportunities

- [Add navigation to the current public API sections](https://github.com/atulsrivas1/equity-features/issues/432)
- [Walk through the continuous-quote example intervals](https://github.com/atulsrivas1/equity-features/issues/433)
- [Clarify current reading context for result contracts](https://github.com/atulsrivas1/equity-features/issues/434)

These are unassigned future Backlog opportunities outside selected R14 milestone16. Agree readiness and scope with the maintainer before implementation. The issue bodies name files, acceptance, prerequisites and runnable checks. Creating them does not implement their proposed changes or establish contributor uptake.
