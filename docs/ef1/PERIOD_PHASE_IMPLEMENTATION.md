# EQ166 bounded period/phase library candidate

Implementation follows [source freeze1](PERIOD_PHASE_SOURCE_AUTHORING_FREEZE.json),
JSON SHA256 `b4c78f03b3c1ec5100740803d4b853920f9aa28cb58d73446dea6b3f403db09c`.
Original17 headers,62 packets, six original fixture nodes, canonical schema/
codec/defaults and package versions remain unchanged. See [API](../api/EF1_PERIOD_PHASE.md)
and [mathematics](../features/EF1_PERIOD_PHASE.md).

New pure `_period.py` admits complete original canonical rows and exact governed
scope/coverage, then computes the two complete families. Context/discovery/dispatch
extend additively. Calculation packages have no I/O, wall-clock, provider,
scheduler, worker or sink dependency. Civil arithmetic is explicit and bounded.

`test_ef1_period_phase.py` has75 methods:62 full frozen packets (42 successes,
20 intentional typed errors) plus13 admission/source/discovery controls. Literal
FLOAT64 expected values pass unchanged; no dtype coercion or calculator-generated
oracle is used. Repeated calls compare full values/quality/metadata/evidence
and unchanged inputs. Existing26 Arrow bridge cases, denial/mutation/no-skip
guards remain. The owned purity census adds exactly75 fixtures and one module:
919 full/893 strict fixtures and53 owned modules.

Actual source-selected Windows checks used Python3.12.10, coordinator's isolated
driver, explicit current contracts/features/external-consumer source roots,
PYTHONDONTWRITEBYTECODE=1 and bounded BLAS threads. On authored working-tree
changes based on73406b2b476d75ef80440ab1ddacf0cd1d85bb97:

- `python -B -m unittest discover -s tests/unit -p 'test_ef1_*.py' -v`:284 methods PASS.
- `python -B -m mypy --strict --cache-dir=nul packages/contracts/src packages/features/src examples/in_memory_adapter.py examples/external_consumer/src examples/typed_caller.py`:59 source files PASS.
- `python -B -m unittest discover -s tests/unit -p test_purity_audit.py -v`:3 audit methods PASS, including actual919/893 fixture and53-module guards.

First combined execution found a historical anchor capability control using
producer `period` to mean unsupported. That malformed anchor-shaped request now
correctly gives INVALID_CONFIG. The control now uses `unimplemented_producer`,
retaining its original UNSUPPORTED_CAPABILITY assertion and test count; no
numerical oracle changed. Initial typing found a reused int/string local name;
civil_start/civil_end names corrected it without mathematical change. Failed
logs remain separate from corrected passing evidence.

Source self-review also narrowed first-open/last-close dependencies to their
actual endpoint fields while retaining every required volume/coverage/knowledge
dependency and all original structural checks. An independent nine-value test
omits only unused earlier-close/later-open columns and expects the complete
PERIOD_BASE numerical values unchanged. Frozen fixtures are untouched.

Source checks are not exact-commit installed qualification. Fresh coordinator/
independent review, final local build/install and complete I/O-worker-sink/browser
integration remain required. Original observed counts, fixed windows, regular-open,
other-denominator, large-period and full EQ164 audit obligations stay open.
No whole-story completion, Linux, private parity, benchmark, provider/N-drive
qualification, release or publication is inferred.


Final source composition selects I/O89bc3d0d61cda5e8b1f5056b500c1f660a051045 (PR23) and workerb40adfbae5a9fa442aea20af3f32ba2e3ba6a4e9 (PR64). Worker lanes pin this library's reviewed bootstrap37ac44a3d0406231caf481c44f4ccce70fb2aba0; the standalone lane uses its actual current core checkout. This finite immutable graph preserves all older16 suites/19 demos and adds core75/I-O17/worker17 methods and two period demos in each installed form. All three implementation candidates have fresh independent source approval and bounded Windows source checks, while exact-commit four-form/platform/browser/full-original-audit/release qualification remains pending. Source selections do not establish installed acceptance.
