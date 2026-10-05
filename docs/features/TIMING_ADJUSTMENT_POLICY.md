# Timing, availability and adjustment admission

EQ-006, policy version 1. This applies to every v1 formula; source truth remains a
caller qualification. No calendar, actions, revisions or timestamps are fetched.
EQ-011–014 encode these policies. R2 adjustment application remains later work.

## Bounds and knowledge

All bounds are supplied UTC int64 nanoseconds. Market cutoff C limits the market
observations consumed; reference cutoff K limits knowledge. Decision cutoff E is
the caller's evaluation time; require C<=E and K<=E for causal simulation. K may
exceed session close for genuinely delayed EOD availability, but never E.
Ordinary event eligibility is open<=event<C; closing auction at close
has the explicit EQ-002 exception when C=close and inclusion=true. Quotes have no
closing exception. Completed bars/daily slots require end<=C, complete delivery
and field-specific availability; forming EOD close cannot be consumed. Supplied
prior-close seed and quote seed must come from their declared prior context.
Feature generation/worker time is outside calculations and proves no availability.

Each fact carries valid/effective bounds, supplied known_at (nullable), immutable
source snapshot/revision and availability policy identity. Effective time describes
what period a fact applies to; known_at describes when that exact revision became
known to the source/caller. They are different. In `known_at` mode each consumed
revision and dependent reference/action must have known_at<=K (equality admitted),
plus applicable effective bounds. Unknown known_at → missing_input with reason
unknown_availability; later known_at → missing_input with reason future_knowledge.
Earlier event time or file creation time never substitutes for knowledge evidence.
The caller supplies the revision valid for that cutoff; current revised facts cannot
silently replace it. Evidence must bind the exact revision used.

`reconstruction` mode permits a caller-selected later-known or unknown revision
to reconstruct past observations. It records known_at unchanged, source/revision,
action basis and reconstruction reason. It cannot be labeled historical causal,
point-in-time available, or used interchangeably with a known_at result. Market
cutoff still prohibits later market observations. Return/composition identities
must include mode, K and E; incompatible identities are validation errors.

EOD availability is end<=C AND knowledge/coverage admitted, not merely C=close.
Intraday features can be complete for [open,C) without claiming completed EOD.
Prior-only baselines/extrema can be ready before target close. SMA/EMA/RSI/ATR and
completed horizon returns require their complete target/context slots. Sector and
universe membership require supplied effective intervals and known-at evidence;
missing sector evidence blocks sector comparison independently of market return.

## Supplied adjustment bases

Every price/quantity/reference input declares basis (`raw`, `split`, `total_return`),
policy ID/version, action snapshot and anchor session. Compare/combine only matching
bases/currency and explicit compatible scales. Different instrument-specific action
snapshots may be bound separately, but must use the same declared policy, anchor and
admission mode. Normalizing scale is explicit and exact; a basis conversion is not
an incidental scale conversion. Missing required action evidence gives unavailable
reference readiness; malformed/contradictory/incompatible bases raise validation errors.

Raw data needs no numerical adjustment, but raw price returns spanning a known action
represent raw price change, never split-neutral or total shareholder return. Preserve
action context. For adjusted data the caller supplies exact positive rational factors
with effective session, known_at, action identity/revision and anchor. A factor is
applicable only to historical slots before its effective boundary and toward the
declared anchor, never automatically before it was known in causal mode. Actions
effective after the target anchor cannot influence that target result.

For a 2:1 split, pre-split price 100 becomes 50 and pre-split shares 10 become 20
on the post-split basis: price'=price/2, quantity'=quantity*2. Notional remains 1000.
Apply the same price factor to OHLC/bid/ask/prior close; use reciprocal quantity
factor for volume/size only if the declared quantity basis calls for adjusted shares.
Nonintegral adjusted coefficients/quantities require explicit exact representation
or caller quantization; silently rounded int64 values are forbidden. Current-session
trade size and old raw volume cannot be mixed with adjusted price without declaration.
Action change invalidates recursive state/history identity and requires replay or
rebuild from the caller's compatible anchor.

`split` excludes cash dividends. A 100 prior close, 99 ex-dividend close and 1 cash
distribution gives raw/split price return -1/100. A declared one-period total-return
reinvestment policy gives (99+1)/100-1=0. The library never guesses dividend amount,
ex-date, taxes, reinvestment price, FX or revision availability. `total_return` requires
supplied policy specifying these conventions and transformed price series/factors;
absent policy/evidence is unavailable. Volume does not receive a dividend factor.
Do not add a dividend again to an already adjusted total-return series.

## Gaps, revisions and evidence

Keep governed missing slots and field nulls; do not forward fill or infer holidays.
Finite windows recover only after all required slots are ready; recursive EMA/RSI/ATR
remain unready after a gap until explicit new anchor or qualified replay. Admission
failure affects only dependent features. Invalid order/representation is an error,
not readiness. Retain market/reference cutoff, mode, original known_at, effective
bounds, decision cutoff E, policy/action/anchor/source/revision identities, missing reasons and coverage.
Future-input/reference mutations outside selected bounds cannot change admitted
results. Corrections alter input identity; stale state is incompatible.

Synthetic design fixtures establish policy consistency with all existing equations,
not that a vendor's history, action adjustment or reference knowledge is trustworthy.
