# Minimal supplied-input quickstart

Use the existing synthetic example to see typed calculations, explicit missing inputs and an external custom calculator without a market-data account. The selected packages are experimental: contracts/features0.0.4a4 and consumer0.4.0. The [EQ132 issue](https://github.com/atulsrivas1/equity-features/issues/313) records the actual accepted source revision and qualification. Use the exact reviewed source and accepted revision recorded there. Source instructions and frozen input metadata alone are not release evidence.

## Prerequisites and channel

- CPython3.12 x64 on Windows or Linux, available as `python`; Git and GitHub CLI.
- Existing GitHub CLI authentication with read access to this repository's Actions artifacts. Public repository visibility does not provide anonymous artifact access. Account setup belongs in the separate setup process; no paid market-data/provider credential is needed.
- A reviewed checkout of this repository, using the exact revision in EQ132's accepted delivery receipt. Obtain the repository with `gh repo clone atulsrivas1/equity-features`, enter `equity-features`, and `git checkout` that recorded 40-character revision. Do not treat an arbitrary latest checkout as a pinned release.
- An absent `work/eq132-quickstart-Windows` or `work/eq132-quickstart-Linux` directory in that checkout. The helper creates a new owned environment and refuses to overwrite an existing destination.

This path selects three **wheels only** from accepted [Foundation run39089365385](https://github.com/atulsrivas1/equity-features/actions/runs/39089365385), main `a0a5c3a5fbeeeca93dbc4d76dbb450361acbc84d`. Windows bundle12122147674 expires November17,2026 at02:17:33UTC; Linux bundle12121724243 expires at02:17:43UTC. [The input manifest](stories/EQ-132_INPUTS.json) contains exact ZIP/wheel sizes, hashes, every entry and source/RECORD bindings. WindowsCRLF and LinuxLF source payloads have separately pinned raw bytes. No new SDist installation, registry release, I/O/worker package, NumPy or PyArrow is selected.

Expired, missing or changed artifacts are unavailable for this pinned path. The helper fails rather than substituting latest, rebuilding, using another index or silently changing dependencies. A new channel requires newly reviewed evidence.

## Run from the reviewed checkout

The same command works in PowerShell and a Linux shell:

```text
python tools/verify_quickstart.py
```

The helper verifies current artifact/run/job identity and complete archive maps, then performs these steps with the explicit fresh environment's Python; no activation or global installation is needed:

1. Current Python runs `-I -B -m venv` to create the new environment.
2. Fresh Python runs `-I -B -m pip --isolated install --no-index --no-deps --no-compile` with the two exact local core wheel filenames, fingerprints every installed core file, then installs the exact local consumer wheel with the same options.
3. It runs `-I -B -m pip check`, checks distribution versions/absence/origins/payloads/RECORD, and invokes `-I -B -m equity_feature_demo.walkthrough` from an empty directory outside checkout.
4. It checks independent whole results and the unchanged public consumer qualification object, then rechecks the complete installed payload. No calculation module is imported from checkout.

The documented walkthrough must produce all four lines:

```text
Installed batch OHLC100/104/99/103; streamed prefix102/final parity; absent bars remain null.
Installed history100/110/121 gives h1=1/10,h2=21/100; missing history/instance stay explicit.
Installed external custom range/open=0.05; unchanged built-in range/close=5/103 verified.
Installed external BAR adapter passed public SDK conformance and custom5/100 binding.
```

After complete verification the helper prints those lines, a PASSED summary and the relative report location. A partial run, timeout, extra/missing line, unexpected dependency or payload drift does not produce a passing report. Qualification compares all43 accepted case identities/outcomes/catalog bindings; that is installed engineering evidence, not a new feature, independent reviewer reinstall, production certification or human usefulness measurement.

## Understand the numbers and absence

Two supplied bars produce open100/high104/low99/close103, volume500 and actual notional20300+30900=51200. Close-weighted price is a different quantity: (102×200+103×300)/500=102.6. Open-close return is3/100, range/close5/103 and close location4/5. With no supplied prior close, overnight and close-close returns are null with MISSING_INPUT. With no supplied bars, all twelve outputs remain null/MISSING_INPUT, never zero.

The stream prefix closes102 at cutoff150; final cutoff200 matches batch values/quality without changing the earlier prefix. Daily closes100/110/121 give one-period return1/10 and two-period21/100. Missing history and a missing composition instance stay explicit. The custom range/open is5/100, distinct from the builtin range/close5/103; the synthetic BAR adapter binds its returned source to that custom result. Full supplied inputs/configuration/results/quality/metadata are retained in the report. Calculations fetch no data, calendar or clock and schedule no jobs.

## Read timings and failures honestly

`work/eq132-quickstart-<system>/report.json` records actual Python/OS, selected channel, source and installed maps, command exits and monotonic durations. The adjacent `logs` directory contains public-safe command output; ignored `raw-private` logs can contain local absolute paths and must not be published. The report separates artifact access, verification, environment creation, installations, checks and replay. Existing Python/Git/CLI/account setup and obtaining the checkout are outside that measured interval.

The pre-publication author run on Windows/AMD64, CPython3.12.10/pip25.0.1, passed in45.094seconds across the declared acquisition/verification/environment/install/check/replay stages. Its complete report SHA256 is `c4824d6cdc553da80a89e62955464863e319d61a60723425dc0724d22b40232a`; the [validation record](stories/EQ-132_VALIDATION.json) preserves its exact reviewed input/source binding. This is one scoped automated maintainer observation, with prerequisites/checkout excluded. It is not Linux qualification, current-CI/default-branch proof or independent reviewer reinstallation; those actual receipts belong to EQ132. “Five-minute” remains an onboarding goal, not a novice guarantee or pass threshold. There are no human participants or adoption results.

| Failure | Meaning and next action |
| --- | --- |
| Unsupported Python/platform | Use the declared CPython3.12 x64 Windows/Linux prerequisite; do not reinterpret another runtime as qualified. |
| Artifact access/expiry/drift | This channel is unavailable or has changed. Retain the failure and request reviewed replacement evidence; do not substitute another build. |
| Existing work destination | The previous directory is preserved. Inspect it before selecting a fresh reviewed checkout; the helper never deletes or overwrites it. |
| Install/check/output/RECORD mismatch or timeout | Qualification failed. Preserve its report/logs, diagnose and review a correction before a new execution. No automatic retry or completed cleanup is claimed. |

Command timeouts are cooperative controls, not hard physical containment or proof every descendant stopped. Failed work directories remain owned and retained for diagnosis. The tool performs no recursive cleanup of existing user paths.

## Next example and limits

Use the [example catalog](EXAMPLES.md) for supplied-input batch/stream/history/composition details, then the [extension guide](api/EXTENSIONS.md) for custom calculator and adapter contracts. [Start here](START_HERE.md) maps optional I/O/workers and independent research. Installed local checks do not authenticate an external source, establish market-data rights, prove profitability or production safety, or complete research M2/M3/M5/combinedC1. The failed R13 study and deferred witnesses remain unchanged.
