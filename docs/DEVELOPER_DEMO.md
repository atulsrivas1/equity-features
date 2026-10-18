# Developer demonstration: supplied inputs to a first report

This is a library demonstration using synthetic inputs. It is not a research
demonstration, trading strategy, production certification or human usability
study. Contracts/features are experimental0.0.4a4; the example consumer is0.4.0,
under Apache-2.0. See [quickstart](QUICKSTART.md),
[contributing](../CONTRIBUTING.md) and [start here](START_HERE.md).

## 1. Run the minimal delivered-wheel example

Use CPython3.12 x64 on Windows with Git and existing GitHub CLI read access to
Actions artifacts. Public repository visibility does not mean anonymous artifact
access. No paid market-data account is needed. Start with an absent destination:

```powershell
git clone https://github.com/atulsrivas1/equity-features.git eq134-wheel-demo
cd eq134-wheel-demo
git checkout 48d4689f10af8c07545e95bd4e70f240ca81d096
python tools/verify_quickstart.py
```

The unchanged accepted helper verifies exact retained artifacts, creates an
absent owned environment, installs three local wheels without an index or extra
dependencies and checks complete results, installed payloads and43 case objects.
It must show all four lines:

```text
Installed batch OHLC100/104/99/103; streamed prefix102/final parity; absent bars remain null.
Installed history100/110/121 gives h1=1/10,h2=21/100; missing history/instance stay explicit.
Installed external custom range/open=0.05; unchanged built-in range/close=5/103 verified.
Installed external BAR adapter passed public SDK conformance and custom5/100 binding.
```

The two bars have actual notional51200; close-weighted price102.6 is a different
quantity. Builtin range/close is5/103; the external range/open is5/100. Missing
bars/history remain explicit nulls with quality reasons. The stream's final
result matches batch without changing its earlier prefix. Full inputs,
configuration, results, quality and metadata are in the report; calculations
fetch no data or clock. Existing [formulas](features/SESSION_FORMULAS.md) and
the [quickstart explanation](QUICKSTART.md#understand-the-numbers-and-absence)
remain normative for this walkthrough.

The selected October Foundation run39089365385 contains Windows bundle12122147674
(expires2026-11-17T02:17:33Z) and Linux bundle12121724243
(expires2026-11-17T02:17:43Z). Exact sizes, digests, entries, wheel/RECORD/source maps
are in [accepted inputs](stories/EQ-132_INPUTS.json). This new demonstration is
Windows-only; existing accepted Windows/Linux qualification is separate. Missing,
expired or changed artifacts fail this pinned path. Do not substitute latest,
rebuild, switch index, overwrite or retry an unchanged failed directory.

## 2. See the source contributor path

Use a second absent checkout and environment. This installs full developer
tooling, including NumPy/PyArrow, separately from the minimal wheel environment:

```powershell
cd ..
git clone https://github.com/atulsrivas1/equity-features.git eq134-source-demo
cd eq134-source-demo
git checkout 84051d9c13f631de398c7f58985f6d07d8e0d255
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pip install --no-build-isolation -e packages/contracts -e packages/features -e examples/external_consumer
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe tools/verify_imports.py
```

Before either environment, verify the selected Python is CPython3.12 x64 with
the prerequisite command in [CONTRIBUTING](../CONTRIBUTING.md#source-contributor-setup).
The import smoke prints `Two package source imports, metadata, py.typed and inward dependency verified.`
It is a source check, not delivered-artifact qualification. Use explicit environment
Python paths, keep assertions enabled and preserve failures.

The [API navigation starter](https://github.com/atulsrivas1/equity-features/issues/432)
names four existing destinations and a preservation check. The maintainer demo
rehearses that exact command on a private modified copy; no public starter is
completed by the demonstration. [Other opportunities](../CONTRIBUTING.md#starter-opportunities)
remain unassigned future Backlog. Agree a task's readiness before implementation.
Follow the full contribution checks appropriate to a future patch; the narrow
demo does not repeat EQ133's649 tests or six reference verifiers.

## Evidence and limits

[EQ134 validation](stories/EQ-134_VALIDATION.json) records actual phase-specific command exits/log hashes/timings and separate review limits.

The actual author Windows demo at precode `bb6919f8ea2c79dee8b6533e74805fabaf19285d` passed all14 outer commands and the unchanged helper's14 nested steps/43 cases. Wheel runtime was CPython3.12.10/AMD64; its helper interval was 41.000seconds, with prerequisites/checkout and the separate contributor phase excluded. The full public validation retains every outer command's own duration; no combined novice timing is claimed. Separate local automated DATA review passed with no findings. This is not reviewer reinstallation or a new Linux demonstration. Existing
Python/Git/CLI/account setup is outside measured time. A maintainer observation
is not a novice five-minute, performance, uptake or response-time guarantee.
Cooperative subprocess timeouts do not prove physical process-tree containment.
Failed owned directories are retained; no recursive cleanup is claimed.

Research M2/M3/M5 and combined C1 remain open; the R13 diagnostic-only failed
study and witness deferral are unchanged. No market-data rights, profit, stable
API, production readiness or operational deployment follows from this demo.

## One participation request

Report one reproducible onboarding problem through the
[bug template](https://github.com/atulsrivas1/equity-features/issues/new?template=bug.md):
use synthetic inputs, exact versions and command, expected versus observed
behavior, and only sanitized nonsensitive output. Read the contribution/support
policy first. No invitations or external messages are sent by this document.
