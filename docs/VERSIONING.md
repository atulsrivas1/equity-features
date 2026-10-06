# Experimental version identities and replay

EQ044 documents the actual release interfaces, not a stable compatibility promise.
Matching core distributions are `equity-feature-contracts==0.0.4a4` and
`equity-features==0.0.4a4`; the independent example consumer is0.4.0.
The consumer's mathematical algorithm remains v2 despite implementation changes.
Git commit, artifact SHA256 and environment identify delivered bytes independently
of these labels. [Delivery](BUILD_DELIVERY.md), [platform qualification](COMPATIBILITY.md),
[public API](api/PUBLIC_API.md), [plan](stories/EQ-044_PLAN.md).

## Identities and enforcement

| Identity | Current meaning and admission |
| --- | --- |
| Distribution/implementation | Corepair versions match exactly; features depends on the matching contracts distribution. Results identify actual backend implementation. Saved session state requires the exact features implementation version; equal schema numbers alone are insufficient. |
| Canonical input | `schema_for(kind)` describes canonical schema1. `CanonicalBatch` carries kind/columns/metadata rather than a configurable schema-version field; admission uses the owned schema, precision and semantic validators. Constructing an arbitrary InputSchema does not install another input schema. |
| Config | ConfigSpec schema1, explicit identity/algorithm/parameters/session/grid/availability/adjustment/unit. Unsupported schema rejects INCOMPATIBLE_VERSION. Canonical sorted JSON represents floats by exact hexadecimal strings; SHA256 digest changes with meaningful configuration identities. It is not authentication or proof that supplied facts are true. |
| Discovery | FeatureDefinition/Registry schema1, builtin scope1 and builtin snapshot digest. Registry decoding checks the current delivered catalog snapshot and actual capabilities. JSON is descriptive metadata, never executable registration/code loading. |
| Feature mathematics | All39 builtins currently advertise algorithmv1; family calculators admit their own supported configuration and formulas. A changed equation/initialization/timing/missingness meaning needs an explicitly versioned numbered change and independent fixtures; implementation-only changes do not silently rename mathematics. |
| Results | FeatureColumn/InputBinding/ResultMetadata schema1; current producers emit math_policy_version v1. Generic columns allow nonempty algorithm labels and metadata allows nonempty math-policy labels: construction alone does not certify an equation. Custom execution compares its declared request/result identities; FamilyResult composition separately requires delivered v1 mathematics and matching catalog columns/config/provenance. |
| Source/policy | SourceBinding mapping/snapshot/input and adjustment/action-policy identities are caller-supplied bindings. Their text is not source authenticity or an automatically executable mapping. Owned consumers enforce their supported adjustment/sampling/availability rules independently. |
| Session state | AccumulatorState schema2, exact implementation0.0.4a4, canonical bounded JSON with payload/binding digests. Binding covers family/config/entity/population/fixed prior/seed and the internal `r1-exact-compensated-v1` math/backend identity. This internal binding label is distinct from result math_policy_version v1 and is not a migration API. |
| Custom | CustomDefinition wraps schema1 metadata with namespaced ID, algorithm/config rule/primitive parameter types, explicit implementation ID/version and actual batch capability. Example demo:range_over_open/v2 computes5/100 while builtin range_fraction/v1 computes5/103. Definition JSON omits the callable; no executable from_json or saved custom state exists. |

History/context/breadth/composition wrappers retain their own schema1 validators;
adapter request/capability/delivery contracts retain schema1 and exact UTCns-int64
precision. These are distinct from session saved-state schema2. Static annotations
and labels do not replace runtime admission or provenance comparison.

Actual modes remain39 builtin batch,23 session update/restore and22 conditional
merge IDs; all16 R2 IDs and custom execution are batch-only. Continuous quote
arbitrary merge is unsupported. Read current discovery capabilities rather than
inferring another execution mode from the package version.

## Typed incompatibility depends on the boundary

| Boundary | Actual rejection and evidence |
| --- | --- |
| State schema/implementation mismatch or rehashed invalid internal facts | INVALID_SCHEMA; [state fixtures](../tests/unit/test_state.py), [six-family exact-code checks](../tests/unit/test_resource_behavior.py). No state is returned and existing accumulator state is unchanged. |
| Envelope payload digest mismatch | INCONSISTENT_IDENTITY; oversize UTF8 text rejects BOUNDS at16MiB. A valid digest does not make malformed/nonfinite content valid. |
| Changed state family/config/entity/source/prior/seed binding | Restore rejects rather than mixing populations; exact binding admission is separate from source truth. [Restore fixtures](../tests/unit/test_state.py). |
| Config/definition/result-metadata/registry schema incompatibility | INCOMPATIBLE_VERSION at their supported-schema validators; malformed values/fields use the corresponding INVALID_CONFIG/INVALID_SCHEMA codes. [Specs](../tests/unit/test_specs.py), [registry](../tests/unit/test_registry.py), [results](../tests/unit/test_results.py). |
| Custom config ID/algorithm mismatch | INCOMPATIBLE_VERSION before callback. Incorrect declared output identity/algorithm/entity/backend/config/input binding rejects INCONSISTENT_IDENTITY; wrong dtype/unit or malformed returned components rejects INVALID_SCHEMA. [Custom fixtures](../tests/unit/test_custom.py). |
| Unsupported custom mode | update/restore/merge reject UNSUPPORTED_CAPABILITY before callback; unknown mode rejects INVALID_CONFIG. Metadata execution flags do not implement a kernel. |
| Supplied composition mathematics/config | FamilyResult/compose_features reject incompatible mathematics and catalog/config identities; distinct instance IDs allow supported configurations of the same builtin rather than renaming its equation. [Composition fixtures](../tests/unit/test_composition.py). |

Callers should handle ContractError.code rather than assuming every version-related
failure is INCOMPATIBLE_VERSION. In particular, exact saved-state mismatches are
INVALID_SCHEMA. Generic FeatureResult.require_same_identity compares complete
metadata/column identities; it does not promise identical values across changed
implementations merely because equations have the same label.

## Migration is replay, not state rewriting

No automatic cross-version session-state migration is implemented or declared.
BUG003 changed schema1 to2 to retain known closed-window omissions. An old state
cannot reconstruct discarded facts, even when its checksum is valid. BUG004
normalized overflowing/nonfinite hexadecimal saved floats to typed errors; exact
implementation matching still requires replay across that correction.
[Incremental corrections](api/INCREMENTAL.md), [changelog](CHANGELOG.md),
[overflow fixtures](../tests/unit/test_state_float_overflow.py).

1. Preserve the original source commit/artifact hashes/environment, admitted supplied
   inputs, ordering/coverage certificates, C/K/E, configuration/unit/action identities
   and fixed prior/seed context. State digests alone cannot recover missing inputs.
2. To resume the original implementation, rebuild/install its recorded matching
   artifacts and use its exact supported state/schema. Historical versions retain
   documented defects and are not certified by the current release.
3. To use the current implementation, create a new accumulator and replay complete
   admitted original facts under its supported configuration and truthful coverage.
   Where facts are missing, preserve unavailable results; do not fabricate omission
   history or upgrade a partial prefix to complete.
4. Check independent goldens, availability/quality and supported batch/stream/restore
   parity. Record the new implementation/config/source identities and any deliberate
   mathematical change. Different backend identities remain different provenance.

Do not edit schema/version strings, rehash incompatible payloads to bypass admission,
deserialize callbacks or infer compatibility from a version prefix. A future migration
needs its own explicit source/target mapping, retained facts, mathematical equivalence
fixtures and numbered acceptance; none is promised by this guide. Source acquisition,
state persistence and scheduling remain outside calculations.

## Validation and publication

Existing independently meaningful specs/registry/results/composition/custom/state/
overflow/resource fixtures cover compatible roundtrips, config identity changes,
incompatible schemas/versions/modes, original-state immutability and exact finite
saved floats. EQ044 adds no mirror tests or runtime/schema/version changes.
626units, strict48 and applicable policies are checked; final-head separate review,
bothOS CI and actual-main publication remain required before acceptance.

For this documentation-only change, package/test/build/consumer bytes must remain
equal to accepted [EQ042 qualification](stories/EQ-042_DELIVERY.md). Verify actual
main bundles and archive equality to its FOURfresh-qualified pairs, plus independently
verify current variable benchmark/resource provenance and facts. Current bothOS CI
also rebuilds and fresh-installs each wheel/sdist pair. The issue records final
main/run/hash/postrelease evidence; this guide alone is not R3 completion, stable
registry publication or hosted/human review.
