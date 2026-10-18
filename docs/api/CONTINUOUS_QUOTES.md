# Continuous quote time weights — experimental0.0.2a5

`equity_features.session.compute_time_weighted(batch, config, *, entity, seed=None)`
returns session.quote.time_weighted_spread. Parameters must be eligibility_policy,
max_age_ns exact integer1..int64max and initial_state (`seed`, `inactive`, `unknown`).
Continuous canonical quote sampling is required; snapshots reject. The supplied
scope is[open,C), positive duration fitting int64; quote events at C reject.
One entity/unit/basis/source/mapping and governed coverage/C/K/E remain caller supplied.

Every row is full current bid/ask, never a delta or silent carry for missing sides.
Invalid/crossed replace previous valid state; locked is valid0. Initial inactive
means known no quote (invalid time) until updated. Unknown initial time lasts until
the first admitted update; no backward fill. Each update, including equal-time
ordered updates, installs a new original expiry anchor. Earlier tied states have
zero time; the last governs positive duration. Freshness is[event,event+max_age).
Split at next update, original expiry or C. At exact expiry state is expired.
Wide Python expiry addition and clipped checked duration avoid int64 wrapping.

In seed mode, caller may supply a separate complete one-row continuous quote with
bid/ask explicitly present (null permitted), matching namespace/entity/unit/basis/
policy and source_id/mapping. Seed snapshot/input IDs are separately bound; input ID
must differ from target and seed event ID cannot duplicate target. Event must lie
inside supplied preopen scope ending<=open. Row at open belongs in target, not seed.
Original seed timestamp anchors expiry, never reset at open. Unavailable or absent
seed contributes unknown initial time and exclusion/absence reason; no future state
is consumed. A target update at open can leave zero unknown duration independently.
Extraneous seed in inactive/unknown mode rejects. Nothing is fetched.

`QuoteDurations(normal,locked,crossed,invalid,expired,unknown)` has exact int64
categories, total=C-open, valid=normal+locked and derived valid_fraction.
`TimeWeightedSpread(durations,mean_spread,mean_bps,max_age_ns,initial_state)` is an
immutable typed result. Valid-only mean spread uses checked decimal128 sum of
(ask-bid)*dt divided by(valid_ns*10^scale). Bps uses individually exact wide
fractions 20000*(ask-bid)/(ask+bid) before compensated float64 sum(z*dt)/valid_ns.
No ratio of mean prices, tick midpoint rounding or abs(crossed spread). Tolerances
rtol/atol1e-12 in stated units; all durations compare exactly.

Complete initialized input with positive valid time is available even when known
crossed/invalid/expired time exists. Zero valid time gives null means/not_applicable
with typed known duration diagnostics. Complete source with unknown left time gives
null means/incomplete_coverage and typed durations. Missing input gives null cell/
missing_input. Incomplete delivery gives null cell/incomplete_coverage: unspecified
feed-gap locations cannot certify carried category durations. Expiry is freshness,
never delivery proof. Known feed outage must be declared incomplete or normalized
into verified no-quote states where that is what happened.

Schema1 envelopes now carry time_weighted_spread dtype. Prior provisional scalar
registry outputs migrate into one typed cell: *_duration_ns maps to durations.*,
valid duration/fraction are derived fields and means retain their original units.
Unknown duration remains explicit. Arrow copies nested typed duration structs;
duration ns are int64 intervals, not UTC timestamps. Root target/seed bindings and
config digest distinguish source/initialization/age choices. At most one consumed
or excluded seed EvidenceRow; target integration keeps no growing row evidence.
Quality expected/observed is raw target delivery count, not duration denominator.

```mermaid
flowchart LR
    A[Unknown or known inactive start] -->|admitted full update| B[Fresh current state]
    S[Admissible preopen seed] -->|original expiry anchor| B
    B -->|next admitted update replaces state| B
    B -->|cursor reaches original event plus max age| E[Expired]
    E -->|admitted update| B
    B -->|cutoff| D[Publish known durations and valid means]
    E -->|cutoff| D
```

Reducer retention is six counters, checked numerator/compensated pair, integration
cursor and one current quote/anchor. Batch canonical ownership/validation and
Arrow copies remain input proportional. R1 qualifies batch/update/restore through [SessionAccumulator](INCREMENTAL.md);
continuous merge and measured throughput remain unsupported. [Example](../../examples/continuous_quotes.py).


## Walk through the supplied continuous-quote example

The [existing example](../../examples/continuous_quotes.py) uses the synthetic
prices in [session_quotes.py](../../examples/session_quotes.py), replacing the
four event/known-at timestamps with `100`, `103`, `107`, `109` and using cutoff `112`.
Times are synthetic UTC nanoseconds; price scale 0 means the supplied integer
prices below are USD. The existing [quote formulas](../features/QUOTE_FORMULAS.md)
define full-update replacement, original-anchor expiry and valid-only means.

| Half-open interval (UTCns) | Bid / ask (USD) | State | Duration (ns) | Original expiry (UTCns) | Earlier boundary |
| --- | --- | --- | --- | --- | --- |
| [100,103) | 100 / 102 | normal | 3 | 106 | next update 103 |
| [103,107) | 102 / 102 | locked | 4 | 109 | next update 107 |
| [107,109) | 105 / 104 | crossed | 2 | 113 | next update 109 |
| [109,112) | null / 102 | invalid | 3 | 115 | cutoff 112 |

Max age is 6 ns, so each original expiry is event time + 6, without resetting an
anchor at a partition boundary. Every row ends at an earlier next update or the
cutoff, leaving expired time 0 ns. The first update is at the open 100, leaving
unknown time 0 ns despite unknown initial state. Durations conserve the 12 ns window:
`3 normal + 4 locked + 2 crossed + 3 invalid + 0 expired + 0 unknown = 12 ns`.

Valid time is normal + locked = 7 ns. The locked quote contributes zero spread but
remains in the valid denominator. Thus the valid-only mean spread is
`(2 USD * 3 ns + 0 USD * 4 ns) / 7 ns = 6/7 USD`. For the normal quote,
`20000 * (102 - 100) / (102 + 100) = 20000/101` basis points; the locked quote contributes
zero, giving mean bps `(3 * 20000/101 + 4 * 0) / 7 = 60000/707`.
Crossed and invalid durations are counted in the 12 ns coverage partition but
excluded from both valid-only means. The null bid at 109 is an invalid full update:
it replaces the previous quote, rather than carrying an older bid forward.

The independent stdlib check is `python tools/verify_quote_examples.py` from the
repository root. It checks independent mathematical fixtures, not this prose or
production execution. Review the table against the linked example and formulas;
follow [contributor setup](../../CONTRIBUTING.md) before separately executing the
production example. No new numerical behavior or measured performance is claimed.
