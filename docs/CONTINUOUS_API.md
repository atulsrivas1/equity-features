# Experimental continuous contracts

EQ113 introduces the opt-in `equity-feature-continuous==0.1.0a1` distribution.
It depends only on `equity-feature-contracts==0.0.4a4` and Python's standard
library. Author Windows/CPython3.12.10 four-form qualification passed at5a154567; current bothOS CI, actual artifact and default-branch delivery gates remain.
The original contracts/features distributions, 39 feature IDs and schema remain
unchanged. Calculation entry points and six new registry IDs belong to EQ114.

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
strict numerator/denominator10^38 stage cap; no calculation kernel runs here.

Typed decoders enforce64KiB config,16MiB input and1MiB result caps before parsing.
The generic decoder applies16MiB before parsing, then the selected kind's cap.
Logical byte/count caps are package admission limits, not physical memory or
execution deadlines. Result validation checks structure, ordered roles, selected
cardinality and witnesses; it cannot authenticate input membership or recompute
the supplied numerical values. The accepted65 literal result vectors qualify
codecs, not executed calculation results.

The [typed synthetic example](../examples/typing/continuous_positive.py) uses
only public constructors and codecs. The [normative specification](api/CONTINUOUS_RESEARCH.md),
[mathematics](stories/EQ112_MATHEMATICS.md), [decisions](stories/EQ112_DECISIONS.md)
and [99 independent vectors](stories/EQ112_FIXTURES.json) define the exact profile.
No source fetching, calendars, credentials, scheduling, persistence or publication
is added to the pure package. Experimental delivery is through verified GitHub
source/artifacts; no stable package-registry release is claimed.
