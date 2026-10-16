# EQ114 pure batch kernels — conditional preparation

This is outside-repository preparation while EQ113 is in Code review. EQ114
remains Backlog/unassigned. No kernel source, runtime test, package version change,
Ready transition or new acceptance is authorized by this document alone. Publish
the complete pre-code packet only after actual accepted EQ113 and recheck accepted
EQ112/017/020/036, owner, current main and original issue216 criteria.

## Selected implementation proposal

Extend only optional equity-feature-continuous, version0.1.0a2. Existing
contracts/features0.0.4a4 and their39 builtins remain unchanged. Own config/input/
result schema1 and algorithm1 equations remain unchanged: adding implemented
capabilities advances the implementation alpha, not mathematics or old identities.
No companion worker/service/MCP or adapter change is required for pure supplied
batch data. No source acquisition, calendar inference, interpolation, FX lookup,
scheduling, persistence, output publication or physical resource/deadline claim.

Three public functions accept exactly ContinuousInput and return ContinuousResult:
compute_basis, compute_freeze, compute_reopen. Each revalidates the entire input
first, then requires its matching config.operation; mismatch is invalid_config.
Malformed input retains the accepted EQ112 structural/error precedence. There is
no caller callback, runtime backend/code selection, plugin loading or mutation.
Unsupported streaming/update/merge/restore is explicit in discovery, not an
unimplemented state API disguised as batch.

## Own immutable discovery, not a builtin override

Add an own frozen ContinuousFeature record and list_features() returning a fixed
tuple of six records. Each record contains id, operation, algorithm_version,
unit, batch, update, merge, restore. The last three are False and batch is True.
IDs already fixed in EQ112 result schemas:

- cross_venue.basis / basis / reference_currency_per_reference_quantity
- cross_venue.premium / basis / ratio
- cross_venue.freeze_max_abs / freeze / reference_currency_per_reference_quantity
- cross_venue.freeze_mean_abs / freeze / reference_currency_per_reference_quantity
- cross_venue.reopen_gap / reopen / reference_currency_per_reference_quantity
- cross_venue.reopen_premium / reopen / ratio

require_capability(feature_id, mode) validates exact string arguments; a known ID
with batch succeeds, any other ID/mode raises unsupported_capability, malformed
argument types invalid_schema. No global registration or executable metadata.
These records are descriptive own API values, not new JSON envelope kinds and not
old Registry/FeatureDefinition claims about CanonicalBatch/FeatureResult support.
Old builtin_registry still returns exactly39 IDs before/after opt-in imports.

## Arithmetic and readiness

Implement _engine.py using owned _model/_rational and stdlib Fraction only.
Implement _registry.py for closed static discovery. Extend only the dedicated
continuous relative-module policy with these two exact modules; previous package
profiles/dependencies/denials remain unchanged. Public contracts-only imports are
already sufficient. No new optional numerical dependency.

Use the accepted99 complete independent records and EQ112 mathematics/decisions,
not a rewritten approximate interpretation. Structural admission precedes all
selection/quality. Compute seven roles in fixed order, their unique ordered
reasons and bounded input proof pointers. Assess independent roles despite other
failures; dependent roles are blocked without invented failures. Empty freeze is
not_applicable only when all nonpopulation prerequisites are ready. Freeze count
always equals all delivered continuous population rows, even when quality fails.

Basis uses latest market-eligible row already known by K, including null as a
blocking selected candidate; reference looks backward from the selected
continuous event. No future-nearest or fallback after selected age/feed/mapping
failure. Freeze/reopen select immutable market boundaries before knowledge;
unknown/late/null boundary values block instead of substituting another row.
Feed facts bind the exact selected points/anchor, full freeze coverage or reopen
transition as specified. Mapping is chosen at each selected continuous event;
all unused facts remain structurally validated and input-digest-bound.

Only after all required roles admit numerical output, calculate reduced checked
X=(pc/10^sc)*D/N, Y=pr/10^sr, X-Y and corresponding ratio. Freeze checks every
chronological absolute-deviation prefix and final division, mean over every row.
Each intermediate has abs(numerator)<10^38 and0<denominator<10^38 after reduction;
overflow is the public overflow error, never clipping/reorder/float fallback.
TopK uses descending absolute deviation then ascending(event,order,UTF8 ID), stores
signed deviations and exact selected reference/conversion witness identities.
Availability preserves maximum original consumed knowledge and the completed
analysis window; it is not refreshed to evaluation or borrowed from an unused
future fact. Exact full role/proof/selected/metric/digest outputs must match literals.
Before returning, enforce the existing own1MiB result-envelope bound through the
owned in-memory codec; valid row counts and128UTF8-byte IDs do not guarantee the
ASCII-escaped result fits. Oversize raises bounds, with no clipped rows/proofs or
recomputed aggregate. This is a logical encoding bound, not physical containment.

## Independent tests before runtime implementation

Freeze an explicit case manifest mapping every accepted99 case to one of the
three public functions, expected constructor/config error or one of the two
arithmetic overflow cases. The65 full expected results remain original literals;
32 structural/config errors and2 arithmetic errors remain distinct. Never derive
expected output with production helpers or relax a quality field for parity.
Reuse the independent large Fraction arithmetic control and existing Rational
boundaries. Add meaningful direct wrong-operation, discovery exact6/39-old-parity,
unsupported modes and input/config snapshot preservation checks.
Freeze a synthetic4096-row freeze with distinct31-emoji-plus-four-digit IDs
(128UTF8 bytes each) as a logical result-size negative: ASCII escaping alone makes
the selected ID payload exceed1MiB while the complete input remains within16MiB.
Expect bounds without truncation; derive the lower bound independently from the
literal row count/escape lengths, not the production encoder output.

The existing EQ113 absence-of-compute assertion is a historical capability check;
replace that specific assertion with the newly frozen positive callable/catalog
contract while retaining its old-type/coercion refusal checks. Do not remove
malformed/callback/order/population regressions. All219 old codec identity records
and old golden remain unchanged. Freeze positive/negative installed typing examples
with actual exact diagnostic line/code/message expectations; append a wrong input
to a calculation function, with no missing-import false pass.

## Packaging, documentation and qualification

Before first build/install qualification freeze complete source/tests/typing/
public API, formulas, registry decision, version/compatibility/build guides,
decision/lesson/changelog/knowledge/handoff, builder/checkers/workflow and effective
input map. Obtain independent exact source/controller review. Author source-unit
tests/mypy are distinct from actual fresh installed qualification.

Retain the reviewed EQ113 closed archives, no truncated ZIP names, selected-platform
directory policy, whole source/metadata/license/RECORD maps, full selectedSDist
materialization and exact generated SOURCES transition. Version only continuous
to0.1.0a2 in its pyproject/export/builder selection; old package sources/versions
remain unchanged. Repeat six archives; rebuild all three SDists; four fresh
light/combined wheel/SDist forms per Windows/Linux now execute every new kernel
golden and existing contracts/typing/old16-probe parity. Full input/result identities
remain source-bound. Actual current54candidate/27main gates are unchanged in count
and exact event/run-attempt/job/OS/head/branch bindings; two actual current retained
ZIPs require provider size/digest/expiry/every-member proof, not old artifact reuse.

Document public constructor/compute/discovery usage and unsupported modes with
synthetic inputs. Keep source tests, actual installed forms, captured evidence,
independent readback and independent reinstall distinct. Preserve all EQ113
initial review/source/build/tool failures; do not rerun accepted EQ113 merely to
manufacture a new receipt. Complete original216 criteria and each actual lifecycle
stage before EQ114 Done. EQ115 then owns final installed end-to-end synthetic
weekend/gap/feed/reopen guides and whole R12 acceptance; no R13 or unrelated scope.

## Complete pre-code refinements

The three reviewed own APIs use the accepted finite ContinuousInput model. Exact
stage checks are Fraction(pc,10**sc), reduced conversion X=scaled*D/N, Y,
X-Y, basis/reopen premium, each chronological absolute-deviation prefix, and
the final freeze division. A comparison cross-product or unreduced multiplication
temporary is not a returned rational stage and has no added10^38 cap. Freeze
does not compute an unused premium. Consume no arithmetic before required quality.

ContinuousFeature is frozen/slots; its constructor admits exactly the six static
records described above. Its fields match the fixed ID's operation, algorithm1,
unit and exact bool capabilities. Nonstring ID/operation/version/unit and nonbool
capabilities are invalid_schema; unknown ID or a field/capability combination
different from the static record is unsupported_capability. list_features returns
the same immutable tuple; require_capability returns None on supported batch.
Exact string arguments may have unsupported values, which fail
unsupported_capability. No old registry metadata, global state or wire kind changes.

EQ114_CASE_MANIFEST.json allocates all99 existing immutable cases without changing
their literals: basis39results/19structural/1overflow, freeze12/6/1,
reopen14/7/0. Structural cases are rejected by construction before any calculation;
the manifest's function identifies the owning entry point, not an executed call.
EQ114_OVERSIZE_INPUT.json is a frozen canonical input envelope from the independent
freeze literal. Its4096 ordered rows have event/known_at101, price101 and unique
128UTF8byte IDs. The selected IDs alone require1,540,096 ASCIIescaped bodybytes,
above1,048,576; full input remains below16MiB. Numerical values otherwise fit;
the planned kernel must raise bounds before returning without truncation.

Before runtime qualification freeze strict installed typing sources and exact
diagnostics for the new entry points/record/mode APIs. The existing wrong-type,
negative coercion, callback, ordering and population checks remain. A source-only
success is not installed-platform or delivery evidence. Include all new plan,
manifest and size-literal files in the builder's effective-input map.

The data-only case preparer initially mistook a present null expected_result for
a full result and expected a scalar error. Its count assertion stopped before
writing a manifest. Corrected nullable-result and structured error_code handling
produced the separately reviewed65/32/2 allocation, with unchanged original data.
This was preparation tooling only, not a product runtime failure or fixture change.
