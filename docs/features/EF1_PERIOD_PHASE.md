# Bounded civil-period and extended-phase mathematics

The [frozen contract](../ef1/PERIOD_PHASE_CONTRACT_PROPOSAL.md) is normative.
Coefficients are exact integers at PriceUnit.scale. Prices divide by10**scale
once; returns use exact rational arithmetic before one FLOAT64 conversion.
Volume is checked INT64 shares; notional is checked DECIMAL128 currency
coefficient. No price-times-volume notional proxy is used.

Period membership is supplied calendar civil dates in `[start,end)`. Weeks start
ISO Monday; months/years use civil boundaries. Prior-complete selects the
immediately preceding civil period. Rolling prior ends at target date; rolling
current ends the following civil day. Rolling months clamp the destination day
to month end. Civil arithmetic consults no timezone database or system clock.

Current aggregation consumes completed member DAILY slots strictly before target,
then the positive target BAR prefix `[regular_open,min(C,actual_close))`. Target
DAILY is never consumed, even after close. Prior-complete consumes every required
member DAILY and forbids BAR. Missing members cannot become latest-available
substitutes. Scheduled count is full admitted membership; completed count compares
actual closes with C, independently of market delivery/prices or nominal close.

Extended aggregation consumes supplied BARs within the selected target phase
prefix. In both phases the denominator is the explicit immediately preceding
governed regular DAILY close:

`open_close_return = (phase_close - phase_open) / phase_open`

`prior_close_return = (phase_close - predecessor_regular_close) / predecessor_regular_close`

Current regular close is not the postmarket denominator. Every extended calendar
contains predecessor plus target. Before phase start all values are null/not
applicable; at start totals are zero and prices/returns null/not applicable.
Both require actual calendar proof, without fake scopes/batches. After start,
missing BAR delivery is distinct from actual complete empty coverage.

Positive-volume rows are price-bearing. Open/close use first/last original OHLC;
extrema use earliest ties. Known zero volume contributes notional0 even when that
optional column is absent. Unknown volume blocks price eligibility and volume
readiness, while independently supplied actual notional can remain ready. Absent
notional affects only notional. All original fields, including unused prior
OHLC/volume, undergo unchanged canonical structural validation first.

Every required delivered row retains original nonnull known_at<=K in both modes,
including zero-volume rows. Calendar readiness gates all fields; market delivery/
knowledge gates dependent numerical fields; prior DAILY gates only its return.
Missing/null/unknown/late reasons outrank governed gaps, which outrank proved
no-price outcomes. All applicable reasons remain lexically sorted. Checked totals
and population overflow cannot be masked by missing calendar proof.

Period numerical quality expected counts required DAILY slots plus BAR expected
population; observed counts delivered DAILY plus BAR rows. Unknown BAR expected
propagates null. Schedule quality is N/N only for complete causal calendar,
otherwise N/0. Phase quality counts BAR population; prior-close return adds one
required DAILY and its delivery. Complete causal no-price phases prove prior
unused, so its numerical count/knowledge is not consumed. Any supplied prior is
still structurally validated and bound. Available scalar counts are known/equal;
all unavailable scalars are null.

Evidence cites original completed interval ends and known-at values, original
bounds/input IDs. Each price field has its operand; returns have two operands,
deduplicated per feature. Totals/counts have no witnesses. Limits are six period/
eight extended rows. Selected explanations do not prove whole-population coverage;
complete original input metadata remains bound regardless of readiness.
