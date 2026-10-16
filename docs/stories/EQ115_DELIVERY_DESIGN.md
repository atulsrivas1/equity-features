# EQ115 conditional consumer qualification design

Prepared outside the repository while EQ114 remains in review. No EQ115
implementation or lifecycle transition is authorized by this document alone.
The actual accepted EQ114 main receipt must precede public plan admission.

## Concrete delivery

Add one public consumer script, `examples/continuous_supplied_week.py`, using
only installed public continuous APIs and stdlib. The caller reads the frozen
synthetic JSON packet, constructs input with its own public codec, dispatches
the matching public computation and checks complete result payloads and all
three own identities against independent literal expectations. File reading
belongs to this example, never to the calculation package. The script emits a
bounded JSON receipt with the twelve case IDs and actual result digests, and
the input packet identity. It uses no network, clock, provider, credentials,
calendar lookup, scheduler, output destination supplied to a calculation or
private kernel helper. Its CLI accepts only the fixture file, not arbitrary
Python/module code. It exits nonzero on any mismatch and never regenerates
expected values from production results.

Add independent consumer tests under `tests/continuous` for the complete twelve
new literal results, original-input preservation, own closed codec round trips,
and refusal of all three own envelope kinds by ConfigSpec.from_json(str)
(invalid_config), own ContinuousResult as FeatureResult metadata (invalid_schema),
and old typed ConfigSpec/FeatureResult values by the own encoder (invalid_schema).
Both old types already come from contracts in light forms; there is no old result
JSON decoder or new integration dependency. Existing original codec/kernel,
oversized-result and legacy parity tests remain intact. No old schema/version
migration is needed: own schema1 remains separate; old ConfigSpec1 and all39IDs
are unchanged. The example displays batch-only discovery and does not claim
incremental update/merge/restore support or SessionSpec migration.

The four-form dedicated builder adds the example and its fixture/plan/readiness/
review/validation docs to its exact selected verification input map. After each
fresh form is installed and source tests/strict typing have passed, run the
example under that form's isolated Python from outside the repository, parse
its bounded output and compare all12 case IDs/result digests to the selected
literal fixture. Save those actual receipts per form in qualification.json.
This is verification-source material, not data silently bundled in a wheel.

Keep continuous0.1.0a2 and contracts/features0.0.4a4 unchanged; this story delivers
guides, consumer checks and qualification. Do not version-bump or alter package
sources absent a real reviewed defect. Preserve all six repeated archives,
selectedSDist materialization/rebuild/source/metadata/license/RECORD checks,
old16 capability checks before/after combined installs and39-ID/config parity,
strict positive/eight negative typing, installed origins/maps and optional
dependency absence. The actual new example must run in all eight fresh forms
(four per Windows/Linux), not reuse EQ114 receipts for execution.

## Evidence and documentation

Keep the twelve literals independent from the existing99 kernel allocations and
219 codecs. Their seven-day caller labels are synthetic; no factual exchange
hours, timezone, holiday, launch, liquidity, token equivalence, price discovery,
entitlement or source completeness claim follows. Full supplied snapshots bind
unused facts as well as consumed proofs. The guide explains scheduled freeze
versus outage/stale/unknown/gap, census certification and first-boundary knowledge,
reduced normalization and original availability. Logical representation limits
remain unchanged; no benchmark, hard deadline or physical containment claim.

Update same-story API/formulas/design/registry/compatibility/limits/build/README/
changelog/knowledge/lesson/handoff links with explicit no-impact decisions for
old core, optional package API/version, session/config/result/state/worker/MCP
and receipts. Record actual prior EQ114 publication guard stop and reviewed
suffix-only recovery; the uncaptured failed response has unknown exact cause.
Do not retell it as a demonstrated propagation or runtime failure.

Publish/review plan and literal packet before Ready; review example, tests,
builder and docs at exact source before first new qualification. Current54
candidate and27 main checks plus two current OS ZIPs require existing exact
event/attempt/job/head/branch bindings and full archive/source/installed proof.
The external artifact auditor additionally checks every per-form example
receipt equals the selected twelve literals. Separate exact public source and actual candidate proof precede Test and Ready
to release. Actual main proof precedes Released and Done; original217 criteria
survive.

After217Done, review original E16 acceptance and exact seven milestone members
against individual receipts, final public source and current artifacts. Publish
the bounded R12 acceptance document and independently verify aggregate delivery
before closing212/milestone13. No R13 selection or new session follows.
