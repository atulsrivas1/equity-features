# EQ-015 execution plan

Story #18, E03/R0;8points confirmed on pull. Prerequisites: delivered EQ-001–006
39-ID mathematics and EQ-011–014 alpha4 contracts/validation. Inspect live issue/
Project/clean main. First action: map every frozen ID to input/output schema,
formula/units, window/initialization, cutoff/knowledge and actual capability metadata.

Implement immutable in-memory FeatureDefinition/InputRequirement/OutputField/
Capabilities and caller-owned Registry.39built-ins are a reviewed literal metadata
dataset, never read from docs/files at runtime. Each definition binds schema1,
algorithmv1, accepted formula document, required canonical/result/reference fields,
units, governed warm-up/defaults, sampling, initialization, timing and missing rules.
All actual batch/update/restore/merge capabilities false in R0; discovery metadata
is implemented, numerical calculators are not. Logical multi-output schema fields
are declaration metadata; future kernels must qualify their concrete result mapping.

Reserved IDs cannot be overwritten/expanded implicitly. Custom definitions use
<caller_namespace>:<name>, are scoped to immutable Registry instances, and must
validate schema/requirements/version/capability metadata. Registration returns a new
registry and cannot import/call callbacks, execute formula strings, discover plugins
or mutate global state. Metadata JSON round trips revalidate versions/keys and the
built-in definition digest; serialize no code. Actual custom execution remains
EQ-093/R3, with independent consumer correctness/purity responsibility.

Tests: exact39ID set/definition completeness, canonical required field/schema checks,
formula/warm-up/timing snapshots and representative edge conventions, actualfalse
capability discovery, unknown ID/mode, namespace/collision/duplicates, malformed
schemas/versions/metadata and attempted execution capabilities, deep ownership,
scoped immutability, metadata serialization/digest and no source/backend import.
Keep123unit/123reference checks, strict typing/boundary/isolation, installed synthetic
registry example and repeat builds, exact-head/main Linux/Windows CI, published
blobs and downloaded/installed alpha0.0.1a5 main artifacts before Done. Update issue/
epic/API/README/plan/continuity and record author self-review only. EQ-016 follows;
E03 stays open and unassigned to a single milestone because EQ-093 remains R3.

EQ-014 was reopened for close-only price admission and reaccepted via PR139, main
12d7fea0b6f218963a8569c18665bd6a258cb0fe, alpha4.post1. Both actual OS bundles
and four fresh installations passed123tests/examples. Registry work resumed on
corrected main, preserving the price fix; four version conflicts resolved to alpha5.
