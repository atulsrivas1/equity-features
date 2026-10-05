# EQ-028 SMA/EMA pre-code plan

Issue #33; E05 #31, R2 milestone3;8 provisional complexity points. Depends on
accepted EQ027 and EQ033 and repaired baseline. This plan precedes source code.

## Mathematics and admission

SMA uses exactly N target-included governed complete closes: sum(C)/N. Defaults
20/50/200. Use exact wide integer coefficient sum and rational mean before final
Float64 scaling. EMA defaults20; explicit HistoryContext.initialization_anchor
seeds the mean of its first N closes, then E=alpha*C+(1-alpha)*E with alpha=2/(N+1).
Period1 equals latest close. Every anchor-to-target slot is required; no automatic
reset after gaps. Changed anchor starts a distinct identity and warm-up epoch.

Extend compute_history for the two IDs with completed_eod window count=N, explicit
positive integer period, same supplied grid/unit/basis/C/K/E/action/source guards
as EQ027. SMA and EMA may share a call/config but have independent readiness.
Quality/evidence dependencies count N for SMA and actual anchor-through-target
slots for EMA; too few anchor slots is insufficient_history. Missing required
closes/coverage stays unavailable. A prior gap can block EMA while SMA recovers.
Future valid rows are structurally checked and never consumed.

EMA uses bounded binary64 recurrence after an exact rational seed; no retained
recursive Fraction denominator. Qualify rtol/atol1e-12 in stated units against
independent high-precision references, including wide scaled and long histories.

## Exact supplied SMA dependency

Add owned SMAReference(schema1,result:FeatureResult,numerator:int|None,
denominator:int|None,price_unit:PriceUnit). It binds a single history.sma cell,
entity/quality/metadata. Available numerator is positive exact coefficient sum
within decimal128 range, denominator=N within positive int64, and their ratio is
within positive int64 price bounds. Denominator matches expected/observed count;
the scalar must equal float(Fraction(numerator,denominator*10**scale)), with matching
currency/share unit. Unavailable results carry neither operand.

compute_sma_reference(batch,config,*,context) qualifies the standard SMA result
and produces this exact witness from the same supplied selected inputs. Additional
finite pass/copy costs are documented; no throughput claim. Standard FeatureResult
and compute_history signatures stay compatible; no new scalar/Arrow witness type.
compare_price(coefficient,unit) validates positive int64 coefficient/exact unit and
returns sign(coefficient*denominator-numerator), rejecting unavailable witnesses.
This preserves ties/one-tick differences near int64 limits when Float64 loses them.
It is structural dependency admission, not source authentication. Later breadth
consumes supplied exact witnesses rather than silently recomputing missing SMA.

## Supported modes and version

Batch-first under the R2 handoff; no history update/restore/merge capability or API
is advertised. The issue's incremental criterion is conditional on supported modes.
This supersedes an unqualified local HistoryAccumulator proposal before publication;
no acceptance waiver or future release promise. Bounded scalar recurrence qualifies
batch precision, not a public accumulator. Registry adds two batch IDs to28;
session update/restore23 and merge22 remain. Pair0.0.3a2; schema1 result/context and
schema2 session state unchanged; exact-version state restore requires caller replay.
All39 frozen catalog definitions/mathematics remain unchanged.

## Independent validation and documentation

Hand golden six closes100,110,105,120,115,130: SMA3=365/3, anchor0 EMA3=975/8.
Qualify period1/all defaults, seed/warm-up, different anchors, null/absent/gap
prefix and finite recovery, target completion/C/K/E/reconstruction, future mutation,
action/config/source identity, wide/scaled integer sum, long high-precision EMA,
and exact witness equality/one-tick/unavailable/invalid projection/ownership guards.
Actual API cases retain all repaired session tests and123 formula references.

Update HISTORY/API/contracts/registry/version/migration/examples/changelog,
knowledge lesson and handoff alongside source. Public synthetic installed example.
Author self-review is explicitly not independent hosted/human review. Follow all
eight lifecycle stages; local tests/types/boundary/import/registry/license/docs,
repeat archives/fresh wheel+sdist pairs, SIX exact-head CI checks, guarded merge,
matching published tree, actual main docs/bothOS CI/bundles/source/epoch/hashes/
contents and FOUR fresh installed pairs precede Released. Final receipt publication
and actual main byte equality precede Done; source merge alone is insufficient.
R3 stays paused; no source acquisition/performance/provider/stable/tag/PyPI claim.
