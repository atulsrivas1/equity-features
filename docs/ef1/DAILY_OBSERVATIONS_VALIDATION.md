# Daily observation library author checks

October 21, 2026. Base commit
`877f8aea0489da4e3d41e7f04bf551a2e8e4a470`, branch
`codex/ef1-daily-libraries`, uncommitted source for coordinator review.
This is local author evidence, not independent review or release acceptance.
Environment: Windows 11 build 26300, AMD64, CPython 3.12.10. Source imports
resolved to this owned checkout's contracts/features packages. No shared
environment installation was performed.

The command records below use `$python` for the actual coordinator-provided
CPython 3.12.10 interpreter. The interpreter's machine-local path is omitted.
Source path configuration was:

```powershell
$env:PYTHONPATH="$pwd/packages/contracts/src;$pwd/packages/features/src;$pwd/tests/unit;$pwd/examples;$pwd/examples/external_consumer/src"
$env:MYPYPATH="$pwd/packages/contracts/src;$pwd/packages/features/src"
$env:PYTHONDONTWRITEBYTECODE='1'
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
```

| Executed command | Result |
| --- | --- |
| `& $python -m unittest test_ef1_daily_observations test_ef1_anchor test_ef1_clock test_ef1_status test_ef1_path test_ef1_reference test_ef1_period_phase test_ef1_observable test_registry -q` | Exit 0; 427 methods; 91 complete literal results, 28 direct pure refusal codes, explicit minimum/common-gap/identity/date controls and retained regression |
| `& $python -m unittest test_purity_audit -q` | Exit 0; 3 audit methods; nested 1040 complete/1014 strict fixture methods; 57 module identities; no skipped subset |
| `& $python -m mypy --strict packages/features/src/equity_features/ef1` | Exit 0; all 14 EF1 source files |
| `& $python -m build --no-isolation --outdir work/ef1-daily-library/dist-reviewed packages/features` | Earlier source exit 0; archives bind daily source 67c805ff5114773454806ecb14a0594970bbef9f3c71d23bef1234c7cb3596f0; current corrected source build pending |
| `git diff --check` | Exit 0 |

The V3A1 original synthetic fixture SHA256 is
`479948037cd6d2fca3901cdb9cf3fcbba6256acbbcb9440bcd68e0362d7688c5`.
No numerical expectations were generated from implementation output. The
minimum/common-gap control is hand-specified from the gate rule: two causally
proved admitted raw observations cannot satisfy minimum three, so every
output is null/insufficient_history with proof counts 3/3, five actual input
bindings and no evidence, even with the common role absent.

First independent source review requested two structural identity corrections
and one deterministic duplicate-date correction. Four new methods exercise
proved absence with retained basis (empty and missing parents), contradictory
existing raw IDs with raw role missing (common and basis variants), duplicate
dates (calendar/raw/common) and civil-label independence. They first failed
with seven failed subcases plus one decoder error, before the corresponding
source fixes. They now pass with the unchanged 91/28 frozen corpus.

The initial author prose and receipt reported 1135 full/1109 strict nested
methods. Those manual figures were each 100 too high: the former source
assertions and actual discovery were 1035/1009. Current counts 1040/1014
include five added methods and are derived programmatically from actual
`countTestCases`/discovered test IDs, preserving all earlier cases. The earlier
receipt, audit logs and builds are retained as superseded evidence; their
successful executions do not substantiate the original incorrect prose counts.

The package source files checked have these SHA256 identities:

| File under `packages/features/src/equity_features/ef1/` | SHA256 |
| --- | --- |
| _context.py | 2781d934cb37ffb98e904655c1da7c3f311f2a638b920228dcc8b0c5296b4dc6 |
| _daily.py | 84e0d2a939e04bbf2457e0b43e11656c3767fea430647359c42493d4eb3d8450 |
| _daily_context.py | 17f3e6d6262e5f95c4d853bb0852b193492bc16fd1a1354746f36cca31cd9115 |
| _definitions.py | 792978d7bc7ad41d53645ab24db9ba7290e4b2861f43c9da448e6046c299b2c3 |
| _dispatch.py | 4482c3317c52c582f00cf6337499668ad38f0c821091a64d6411e2879c7cff7b |

Earlier-source local wheel SHA256:
`ad8b7eab74c09c5cd28e9107bcc443bb7c27d58c1925673179dd9baeb9f26b6a`.
Earlier-source local SDist SHA256:
`ca2b4a3d2423d635ca1a6e955cb719ace0773976ad2f3f5988fb575238abadb5`.
These builds do not validate the current final orphan-parent correction,
clean installed execution or another platform. Current-source build follows
the final bounded source recheck.

The second independent recheck found a remaining orphan basis with actual
empty raw/common batches and observation_coverage=None. The explicit new
control failed with no ContractError before the symmetric actual-raw-parent
guard and passes afterward. Raw=None and legitimate common capability gaps
remain covered by unchanged frozen full-result packets. V3A2 independently
clarifies that decoder civil syntax acceptance does not establish authentic
calendar intervals, factual timezone mapping or actual source representability.

An overbroad current-count replacement also corrupted unrelated historical
handoff IDs/counts/measurements. Failed complete copies are retained privately.
All historical bodies in SESSION_HANDOFF, PROJECT_KNOWLEDGE and knowledge/LESSONS
are restored directly from base Git commit 877f8aea0489da4e3d41e7f04bf551a2e8e4a470;
exact raw-byte suffix equality is asserted after the final owned-prefix edit.
No historical correction is inferred from current unit counts.

Earlier failures remain in local author logs: initial selector-key and
validation-order implementation defects, typing errors, one oracle mismatch
resolved through independent V3A1 clarification, a command quoting failure,
and missing example source path on the first full purity launch. The
minimum/common gate defect was found by source inspection; a separately
labelled retrospective reconstruction of its former one-line condition
failed the new control, then the active corrected source passed. This is not
a claim that the new control had been run before the original correction.
An initial successful build wrote only its two generated archives to an
unintended output folder; those files were moved into the owned work area,
and a later changed-source build used the intended folder directly.

Remaining gates: coordinator actual diff review before any commit/push,
fresh independent review, exact-commit local checks, actual I/O/worker/SDK
and storage composition, installed four-form Windows/Linux qualification,
original source/profile bindings, full EQ164 audit, browser demo and release
acceptance. No registry/package/release publication is authorized here.
