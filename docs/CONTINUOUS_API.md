# Experimental continuous batch API

EQ114 extends the opt-in distribution to `equity-feature-continuous==0.1.0a2`.
It depends only on `equity-feature-contracts==0.0.4a4` and Python's standard
library. [EQ113 contracts acceptance](https://github.com/atulsrivas1/equity-features/issues/215#issuecomment-6223048289)
is complete. [EQ114](https://github.com/atulsrivas1/equity-features/issues/216)
records current kernel review, qualification and delivery status; source tests alone
do not qualify a new installation.
The original contracts/features distributions, 39 feature IDs and schema remain
unchanged. The new entry points and six feature IDs belong only to this namespace.

`compute_basis`, `compute_freeze` and `compute_reopen` each accept an exact
`ContinuousInput` and return an immutable `ContinuousResult`. The full supplied
snapshot is structurally revalidated before its operation is matched to the
entry point; a well-formed different operation is `invalid_config`. No callbacks,
backend selection, acquisition, clocks, persistence or publication are accepted.
Malformed inputs raise public `ContractError`; admitted missing/late/stale/null
facts produce the defined unavailable quality rather than invented prices.

`list_features()` returns a fixed tuple of six frozen `ContinuousFeature` records
with `id`, `operation`, `algorithm_version`, `unit`, `batch`, `update`, `merge`
and `restore`. Batch is true; the last three are false. `require_capability(id,
'batch')` returns `None` for a known ID. Unsupported IDs/modes raise
`unsupported_capability`; nonexact string arguments raise `invalid_schema`.
Metadata is descriptive and does not claim old `Registry`, `CanonicalBatch` or
`FeatureResult` integration. Its constructor accepts only the exact six fixed
declarations; wrong primitive types are `invalid_schema`, unsupported declarations
are `unsupported_capability`.

| IDs | Operation | Unit |
| --- | --- | --- |
| `cross_venue.basis`, `cross_venue.premium` | basis | reference currency per reference quantity; ratio |
| `cross_venue.freeze_max_abs`, `cross_venue.freeze_mean_abs` | freeze | reference currency per reference quantity |
| `cross_venue.reopen_gap`, `cross_venue.reopen_premium` | reopen | reference currency per reference quantity; ratio |

Basis aligns latest-known observations backward. Freeze assesses every supplied
population observation against the held pre-window reference; mean is count
weighted over all rows, while topK is separate bounded evidence. Reopen selects
immutable boundary observations before knowledge validation; a late first
reference cannot be replaced by a later row. The seven readiness roles retain
ordered reasons and consumed input pointers. All input records, including unused
facts, remain digest-bound. Available time retains original consumed knowledge
and the completed analysis end, with no freshness reset.

Normalize `X=(pc/10**sc)*D/N`, `Y=pr/10**sr`; difference is `X-Y` and ratio is
`(X-Y)/Y`. Every supported reduced stage, chronological absolute-deviation prefix
and final mean must fit the declared rational cap. Unreduced/comparator temporaries
have no extra returned-value cap. Quality precedes arithmetic; missing prerequisites
cannot be turned into an overflow. Empty freeze is not applicable only when its
other prerequisites are ready; an old held reference leaves population blocked.

`PriceObservation`, `Leg`, `FeedFact`, `ConversionFact`, `ContinuousConfig` and
`ContinuousInput` represent supplied immutable snapshots. `Rational`,
`RoleReadiness`, `MetricValue`, `SelectedObservation`, `DeviationWitness` and
`ContinuousResult` represent the closed result structure. Collection arguments
are bounded concrete lists/tuples detached into tuples; arbitrary iterators,
subclasses and dictionaries as typed records are refused. UTC nanoseconds are
exact nonboolean signed64 integers. Identifiers are trimmed nonempty exact UTF8
strings of at most128 encoded bytes. Feed facts do not establish provider truth.

`to_json`/`from_json` handle only own config/input/result envelopes at schema1.
Typed `config_from_json`, `input_from_json`, `result_from_json` require their
respective kind. Sorted compact ASCII-escaped UTF8, with no terminal newline,
defines the SHA256 returned by `config_digest`, `input_digest`, `result_digest`
and each record's `identity_digest`. Old serializers do not coerce these objects.
Duplicate/unknown keys, nonfinite numbers, trailing data, noncanonical rational
wire values and unsupported versions are refused with public `ContractError`.
Direct `Rational` construction reduces positive-denominator fractions before the
strict numerator/denominator10^38 stage cap.

Typed decoders enforce64KiB config,16MiB input and1MiB result caps before parsing.
The generic decoder applies16MiB before parsing, then the selected kind's cap.
Logical byte/count caps are package admission limits, not physical memory or
execution deadlines. Result validation checks structure, ordered roles, selected
cardinality and witnesses; it cannot authenticate input membership or recompute
the supplied numerical values. Kernel-produced results enforce the complete1MiB
envelope before returning; valid counts/UTF8 identifier sizes do not guarantee an
ASCII-escaped result fits. Oversize raises `bounds`, without omitted evidence.
The original219 codec vectors and the separate65 complete kernel outputs are
different validation axes; see the [kernel validation](stories/EQ114_VALIDATION.json).

The [typed synthetic example](../examples/typing/continuous_positive.py) uses
only public constructors and codecs. The [normative specification](api/CONTINUOUS_RESEARCH.md),
[mathematics](stories/EQ112_MATHEMATICS.md), [decisions](stories/EQ112_DECISIONS.md)
and [99 independent vectors](stories/EQ112_FIXTURES.json) define the exact profile.
No source fetching, calendars, credentials, scheduling, persistence or publication
is added to the pure package. Experimental delivery is through verified GitHub
source/artifacts; no stable package-registry release is claimed.
