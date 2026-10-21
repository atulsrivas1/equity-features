# EQ165 observable pure-library candidate

This implementation follows [source freeze1](OBSERVABLE_SOURCE_AUTHORING_FREEZE.json)
read with the reviewed [publication amendment](OBSERVABLE_PUBLICATION_AMENDMENT.md)
and [publication freeze](OBSERVABLE_PUBLICATION_FREEZE.json). The authoritative
publication fixtures have SHA256
`646e402e321eb97a171a2f8f64ce3c1ee399f7bcb81906fd929be4e6477170a6`;
original V4 JSON `d0fb7b4f...` remains unchanged. Only58 successful result global
math-policy metadata values changed to `v1`; algorithm/context/mapping remain
observable-v2/context2/map2. All numerical inputs, configs, values, quality,
evidence and31 intentional errors remain identical. See [formulas](../features/EF1_OBSERVABLES.md)
and [API/examples](../api/EF1_OBSERVABLES.md).

Two new pure modules implement closed observable context admission and physical
population reductions. Existing public EF1 context/build/discovery/dispatch
functions gain an explicit observable-v2 route. Legacy v1 identities, default
registry, canonical schemas/codecs and package versions remain unchanged.

`test_ef1_observable.py` has111 methods:58 exact frozen full results,29 canonical/
pure refusals and24 independent controls. Each successful packet checks full
values, quality, metadata and evidence, unchanged input data and deterministic
replay. P2 controls exercise both-mode history/event/proof/seed knowledge,
independent dependencies, initial/unknown/resume relations, checked int64 quality
addition, actual coverage.observed, wrong-family proof, nullable transport,
missing-vs-empty positions and strict configuration identity.

Intentional-error stages are explicit: X10 timestamp overflow refuses during
CanonicalBatch construction;28 other packets refuse during pure context or
semantic calculation admission. X13 is an outer worker task-wire bound and X15
is a canonical candidate-result evidence bound; neither is falsely counted as a
pure callback refusal. E16 retains its intentionally wrong all-zero target hash.

The purity census adds111 independent fixtures and two owned modules:1030 full /
1004 strict fixtures and55 owned modules. Existing26 Arrow bridge cases and
entrypoint-denial, mutation-detection, exact-count and no-skip controls remain.

Author checks are source-selected Windows Python3.12.10 checks in the existing
private isolated driver, based on06841dc45b849185be3a46554094eeaf4f26dae0 plus this
working diff. They are not exact-commit installed or cross-platform evidence.
Final commands, exits and limitations are recorded in the coordinator's author
handoff. Initial runs exposed author implementation/test bookkeeping defects;
corrected runs keep independent expected results unchanged and retain failed logs.

Fresh coordinator and independent review, exact-commit build/install/platform
qualification, adapter-worker-sink integration, browser demonstration and the full
original inventory audit/release gates remain. Original source/consumer bindings
and original-version parity remain unaccepted. No release, registry publication,
provider/N-drive qualification, benchmark or whole-story completion is claimed.


The original computed V4 candidate passed source fixtures but worker publication
exposed the unchanged SDK/sink rejecting its global `observable-v2` policy. The
reviewed amendment keeps global policy `v1` because no global precision or
representation rule changed. Independent literal construction plus unchanged SDK
prepare accepted58/58 amended literal results and rejected58 unsupported-policy
variants; that preparation called no producer or database. Actual computed
source/worker/sink checks must be recorded separately from that literal probe.
Earlier original-V4 source logs remain retained and are superseded only for the
metadata binding by new publication-fixture runs; they are not relabelled.


Actual amended publication-fixture source checks, with Python3.12.10 on Windows:

- `python -B -m unittest discover -s tests/unit -p test_ef1_observable.py -v`:111 methods PASS, exit0.
- `python -B -m unittest discover -s tests/unit -p 'test_ef1_*.py' -v`:395 methods PASS, exit0.
- `python -B -m mypy --strict --cache-dir=nul packages/contracts/src packages/features/src examples/in_memory_adapter.py examples/external_consumer/src examples/typed_caller.py`:61 source files PASS, exit0.
- `python -B -m unittest discover -s tests/unit -p test_purity_audit.py -v`:3 audit methods PASS, exit0, with1030/1004 fixtures and55 owned modules.

These checks cover the working implementation on published amendment base
06841dc45b849185be3a46554094eeaf4f26dae0. They do not establish a final-commit
installed distribution, another platform, source-data parity or release status.


Fresh full independent review found a P2 quality dependency defect: an irrelevant
physical event preserves the unresolved initial relation, so a later first active
still requires the boundary seed. The reducer now tracks initial-relation origin
independently of event index; an unknown/local relation reset clears that origin.
Three independent methods cover absent, clear/interrupted/unknown, unknown/late
seed in both modes and a true unknown reset. The irrelevant/active absent-seed
resume remains null with missing_action_evidence and proof-only evidence, now
correctly expected6/observed5. Unknown/active remains5/5. The original58 result
packets and31 intentional errors are unchanged. Earlier108/392 and1027/1001 source
runs remain retained; current111/395 and1030/1004 runs supersede their source coverage.
