# Proposed three-layer implementation handoffs

Status: preparation only. No implementation, commit, push, release or shared-contract freeze is granted. Use the complete V3 contract and unchanged 100-packet oracle, not this handoff as a substitute for semantics. The coordinator must first attach actual generic transport evidence, resolve any findings, obtain distinct source-safe publication review and freeze exact hashes. All three tracks belong to the same EF1 release.

## Shared exact boundary

| Boundary | Required identity |
| --- | --- |
| Numerical owner | EQ166 #506 |
| Representation owner | EQ212 #570 |
| Worker owner | EQ213 #571 |
| Producer / config identity | `regular_bar_prices` / `ef1.regular_bar_prices` |
| Config schema / algorithm | `schema_version="1"`, `algorithm_version="v1"` |
| Result backend | `backend_id="python-exact"`, `backend_version="0.0.4a5"` |
| Result schema / math | `schema_version="1"`, `math_policy_version="v1"` |
| Declared / actual evidence | exactly 2 / at most 2 |
| Input roles | `calendar_provenance`, `bars`, `population_proof` |
| Present kinds | REFERENCE, BAR, REFERENCE |
| Lexical two result headers | `session.close.calculated_price`, `session.regular.first_completed_bar_open` |
| Output header type / literal unit | FLOAT64 / `currency/share` |
| Context / proof text | independent 4,096-byte ASCII limits |
| Input serialization | protocol-5 pickle <= 1,048,576 bytes, separately measured |

The canonical contracts package is `0.0.4a4`; the features result backend version is `0.0.4a5`. They are different identities. ConfigSpec has no build-version field. Existing exact DTO field lists are in EXISTING_DTO_FIELDS.json; those are public API field names, not a new record definition or factory.

CanonicalBatch is constructed with kind/columns/metadata only, and Column with name/values. A fixture schema_version must be validated against its existing canonical schema rather than passed as an invented constructor field. BatchMetadata retains namespace, SourceBinding, Coverage, PriceUnit or None, AdjustmentSpec, sampling, quantity_unit, ordering, duplicate_policy, InputScope or None and typed interval_coverage. SourceBinding has four fields only. Preserve supplied original metadata objects/values and do not infer a revision property.

The exact membership projection deliberately retains the historical `ef1-gap-membership-projection1` version. It is compatible BAR membership structure, not a gap proof or gap calculation. This new producer requires `ef1.regular_bar.population.v1` / `ef1-regular-bar-population1` / `regular-bar-membership-asof1` and producer/phase bindings. Never accept an old gap-family proof by its similar JSON shape.

## Library track: pure first-open and calculated-close prices

After an explicit coordinator grant, add this producer to the existing EF1 config decoder, definitions/discovery and compute dispatcher. Pure input remains exactly three nullable slots. Validate all structural contradictions before readiness, including supplied invalid OHLC on an unused positive-volume BAR and absent peer roles. Enforce target-only calendar, ordinary regular/no auctions, exact completed-bar bounds, source-neutral membership proof, independent endpoint selection and original numerical known-at.

The numerical kernel alone selects first/last definite positive-volume BARs and converts the relevant coefficient with one float(Fraction(...)) conversion. It cannot fetch, open files/databases, schedule jobs or publish output. Do not reuse an old all-row numerical-availability shortcut: an interior delayed price does not block independently proven endpoints; unknown membership on the applicable outer side does. Do not introduce prior-close/notional dependencies, official-close certification, phase inference or hidden thresholds.

Cover all 46 complete expected results and all 54 original stage-specific refusal requests without regenerating expectations from production. Preserve the expected early constructor/canonical cases as distinct from executed pure semantic cases. Add meaningful additional independent boundary/causality controls, strict typing/purity and relevant prior EF1 regressions. Preserve existing producer behavior and all bounds. Update formulas, API, examples, decisions, changelog and handoff in the same story.

## I/O track: supplied facts and unchanged result transport

After grant, provide three fixed nullable roles/slots and the present-only role-order batches, with an explicit synthetic/observed/unavailable provenance declaration. New public helper names remain subject to the coordinator's source-authoring handoff; no proposed name here is an already registered API.

Convert only exact supplied rectangular cells and original metadata. Preserve column order, row order, identity, clocks, volume classes, null/absent distinctions, basis, coverage and proof text. Do not filter, sort, repair invalid/null OHLC, infer phase/auction membership, select endpoints or calculate prices. Supplied proof text is preserved; a newly computed membership checksum cannot manufacture historical proof existence or availability. If a truthful observed-source capability is unavailable, report that fact or use explicitly labelled synthetic fallback. No N-drive dataset is admitted by this preparation.

Canonical validation may refuse a constructor/schema target before the pure producer; record the real stage. Do not reinterpret an absent OHLC column as a present-null price or rescue either by filling. Reuse existing SDK and output sink contracts; no new codec/schema or backend version rewrite. Later actual composition must compare full direct, worker, encoded, persisted and reopened results for all admitted fixtures, identical retry and new separate output DuckDB paths. No source/production database write is authorized.

## Worker track: exact declared input and result closure

After grant, add an opt-in family `regular_bar_prices` using existing TaskManifest/InputManifest/WorkItem and publication machinery. All three InputManifest roles are declared in fixed order, with original present InputBindings; batches are their exact present subsequence. The callback reconstructs nullable slots by role/binding, never by DataKind. InputManifest fields are role/acquisition_sha256/revision_id/state/binding/known_at_ns; revision_id is worker acquisition identity, not an invented SourceBinding field. Missing, empty, partial and complete states keep their existing constructor meaning.

TaskManifest retains its actual fields: job_id, generation_id, partition_id, family, instruments, config, features, inputs, governed_sessions, destination_scope, ownership, max_input_batches, max_input_bytes, ordered_history, warmup_sessions, initialization_sha256, merge_policy, protocol_version, canonical_package_version, canonical_schema_version, math_policy_version. Use one instrument, the exact target-only governed interval, `ordered_history=False`, no warmup or initialization, `merge_policy="none"`, and serialized destination ownership. Use three input-batch capacity and bounded actual protocol-5 bytes. Existing task protocol is `efworker-task1`, canonical_package_version `0.0.4a4`, canonical_schema_version `1`, math_policy_version `v1`. These do not substitute for the result's features backend_version `0.0.4a5`.

Bind exact config/headers/session/availability and full actual input identity. Invoke the pure library for all mathematics. Reject wrong family/role/binding/governed geometry; then close returned backend/version/config/entity/headers/math policy, exactly two values/quality cells, declared evidence_limit 2 and actual evidence <= 2 before any sink begin/write/commit/read. Include instrumented tamper controls for evidence declarations 1 and 3, unknown math version and wrong backend version. Generic current comparator acceptance is a missing future guard, not a conformance pass.

Keep the protocol-5 input budget, existing TaskJSON maximum (1,048,576 bytes), context/proof limits and configured output-codec/sink requirements separate. Record actual sizes in reviewed probes; do not treat one encoding's size as another's. No generic guard increase. Distinguish constructor/manifest/canonical/config/semantic failures from actual callback coverage.

Later integration must compute synthetic results through adapter -> worker -> pure library -> existing sink -> new output DuckDB, compare complete independent literals, retry and close/reopen readback, and produce truthful HTML. A generated HTML file does not prove browser inspection. Build/install/platform evidence belongs to later compatible pinned source cohorts, not this proposal.

## Reporting, review and protected work

Every author reports completion, actual source identities, commands/results/failures, documentation and remaining gates immediately so the coordinator resumes review and integration. Contract defects are escalated before altering semantics or fixtures. No commit/push without the coordinator's instruction; coordinator review precedes push and fresh independent actual PR review plus appropriate local validation precede merge.

This preparation changes no active release owner or resource reservation. No provider/paid service, original-source/prod write, benchmark/full-machine work, SaaS hosting, package/tag/release publication or later-release implementation is granted. Full EQ164, original parity, source rights/capability, integrated installed artifacts, browser and whole EF1 acceptance remain open.
