# EQ030 historical volatility pre-code plan

Issue35/E05#31/R2;8 provisional complexity points. Dependencies and preceding
EQ029 are verified Done; this public plan precedes source implementation.

history.return_volatility period N>=2/default20 uses Nsimple returns from exactly
N+1complete target-included governed closes. r=C_i/C_(i-1)-1; mean=sum(r)/N;
variance=sum((r-mean)^2)/(N-1); output=sqrt(A*variance). Parameter
annualization_factor is a positive int64 integer default1, explicitly declared
under v1/default or supplied configuration. Never infer252, log returns, RMS,
population denominator or standard deviation of prices. Output dimensionless
fraction; effective A and its square-root-time convention documented in config.

Extend compute_history for this one ID, completed_eod WindowSpec.count=N+1;
separate invocation/config from other families. All exact grid/unit/basis/context/
source/action/C/K/E/coverage/evidence guards remain. Quality counts required closes,
not Nreturns; missing middle closes never compress a window. Finite window recovers
only when every required slot recovers. Available flat history returns0; unavailable
stays null. Unknown/extra parameters and unsupported periods/factors are typed errors.

Use exact transient Fraction returns/centered variance over the finite selected
window, then an80-digit Decimal square root and final Float64. Exact nonnegative
variance needs no cancellation clamp. Near-int64 one-tick changes must remain
nonzero even where float price differences disappear. No retained recursive
fraction/state; transient numerator/denominator sizes and arithmetic work grow with
finite N and supplied prices, explicitly documented without throughput/constant
memory claims. Independently qualify rtol/atol1e-12; tiny nonzero regressions also
assert strict positivity/exact expected orders beyond absolute tolerance alone.

Actual API tests: period3 hand variance476449/44791488, explicit A4 doublesoutput,
defaultA1/no252, N2minimum, centered versus RMS/population, flat0, wide/scaled near
equal coefficients versus Decimal reference, large price-ratio inputs, missing/
null/middle/gap/finite recovery, causal completion/knowledge/reconstruction/future
mutation, action/source/config/unit revisions, invalid period/A/types/mixedIDs,
independent fields and false modes. Preserve all repaired session/previous history
and123reference cases. Batch-only under handoff; no public accumulator update/
restore/merge qualifies from a bounded finite mathematical window.

Pair0.0.3a4 adds one batch flag (31total/all8history);39definitions/equations and
session23update/restore22merge remain. Existing schemas unchanged; exact-version
state/registry compatibility requires caller replay/rebuild. Supersedes unqualified
private finite-window accumulator proposal, no scope waiver or future state promise.

Public API/conventions/precision/units/config/defaults/costs/example/contracts/
registry/version/changelog/lesson/continuity with source. Publish plan before code.
Author self-review+CI accurately labeled; local units/refs/types/purity/import/
registry/license/compatibility/docs and exact-head repeat4archives/fresh pairs/SIX
checks, guarded merge/tree/main docs/bothOS actual bundles/FOUR fresh pair installs
and final receipt/head/main byte equality before full eight-stage Done. No source
lookup/provider/private copying/performance/stable/tag/PyPI claim. R3 paused.
