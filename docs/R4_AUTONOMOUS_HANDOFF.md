# R4 autonomous DuckDB adapter execution

Prepared under [GOV013 #258](https://github.com/atulsrivas1/equity-features/issues/258)
at the owner's request on October 6, 2026. Owner requested this package and a new
execution chat after accepting R2/R3 and requiring both synthetic and real tests.
Preparation is not implementation, test execution or adapter acceptance.

## Mission, authority and limits

Complete [R4 milestone5](https://github.com/atulsrivas1/equity-features/milestone/5)
and [E07 #55](https://github.com/atulsrivas1/equity-features/issues/55): EQ049–056.
Use one dependency-ready active story, public issue/Project updates, plans before
code, documented routine choices, short-lived codex/ branches, PRs and actual
review/test/installation/publication gates. Exact lifecycle is Backlog → Ready →
In progress → Code review → Test → Ready to release → Released → Done.

Develop an optional installable DuckDB adapter outside numerical packages.
Calculations never fetch, open files/databases, schedule jobs or publish outputs.
Do not implement R5 workers, provider acquisition, remote/chart services, unrelated
products, account administration, stable release/tag or PyPI publication. Continue
the experimental CI artifact channel until separately authorized. No original
source deletion, data regeneration or owner-stopped historical build restart.

Read AGENTS.md, PROJECT_KNOWLEDGE.md, PUBLIC_DEVELOPMENT.md, DELIVERY_POLICY.md,
SESSION_HANDOFF.md, BACKLOG.md, PACKAGE_DESIGN.md, R2_ACCEPTANCE.md,
R3_ACCEPTANCE.md, contracts/INPUTS.md, contracts/ADAPTERS.md,
contracts/ADAPTER_KIT.md, timing/action/history/API rules, CODE_REVIEW.md,
BUILD_DELIVERY.md and COMPATIBILITY.md. Follow the live Project as status authority.

## Baseline and separate review

Preparation readback: R2 milestone3 and R3 milestone4 closed, all their stories
Project Done, no open PRs. Main28879e3adf78e17c3ed37150010f16399cdea518 has successful
Foundation37508048990 and documentation37508048897. R3 reports633 unit tests,
123 mathematical references and accepted experimental contracts/features0.0.4a4,
consumer0.4.0. Recheck live artifacts/expiry, actual main and prerequisites; these
are recorded observations, not new test execution or permanent artifact hosting.

CODE_REVIEW.md's local alternatives explicitly cover bounded R2/R3; hosted
activation remains unverified. Require an actual final-head separate review under
an owner-authorized R4 alternative or working hosted integration. Missing review
blocks merging/Done, not independent baseline inspection and preparation. Do not
silently extend the earlier alternative, invent approval or call self-review
independent. Record findings/disposition and actual reviewer limits. An execution
chat may independently inspect the prepared handoff, but that alone does not waive
the policy gate for implementation.

## Story order, estimates and end states

All points are provisional effort estimates, not dates; total52. Revise with
observed evidence when pulling, rather than inventing completion forecasts.

| Story / issue / points | Dependencies and start | Design and unresolved decisions | Required tests and docs | Done boundary |
| --- | --- | --- | --- | --- |
| [EQ049 /56](https://github.com/atulsrivas1/equity-features/issues/56) /5 | R3 accepted; inspect catalog/protocols | Explicit bounded generation resolver; original/optimized pins, overlap, substitutions, unknown admission; freeze optional API and missing-hash receipt binding | Synthetic ambiguous/missing/empty/overlap/substitution/stale pin/schema/limits; resolver API/evidence docs | Installed verified resolver only; [plan](stories/EQ-049_PLAN.md) |
| [EQ050 /57](https://github.com/atulsrivas1/equity-features/issues/57) /8 | EQ049 interface frozen | Trades/TBBO/minute/daily mappings; exact UTCns, price/share units, original identities, nulls, eligibility, known-at; freeze precision policies and unsupported fields | Independent row expectations, overflow, ties, absent/null/zero, invalid clock/scale and sampling; mapping/normalization guide | Qualified canonical mappings; no invented source fields |
| [EQ051 /58](https://github.com/atulsrivas1/equity-features/issues/58) /8 | EQ049/050 | Private read-only connections, bound filters, owned source populations, bounded batches/cancellation; choose tested DuckDB/backend pins | Predicates, chunks/limits/order/cancellation/errors; measure SQL plus conversion/copy/native memory; optional install/read API | Bounded historical acquisition; no scheduler/live feed |
| [EQ052 /59](https://github.com/atulsrivas1/equity-features/issues/59) /8 | EQ049–051; accepted timing/history rules | Versioned caller-governed sessions, warm-up and effective/known-at references; freeze calendar/reference support without file-date inference | Holidays/DST/early closes, missing EMA prefix versus finite-window recovery, prior-only baselines, action/membership revisions; gap/reference guide | Explicit supported sessions/history/references; unsupported causal references remain unavailable |
| [EQ053 /60](https://github.com/atulsrivas1/equity-features/issues/60) /5 | EQ049–052 evidence boundaries | Bind source snapshots, receipts, normalization/schema versions, substitutions, original/optimized identity and admission; reuse contracts for later EQ103 | Changed/stale/missing pins, schema/snapshot mixing, unknown provenance/availability; receipt semantics and limits | Bounded acquisition evidence, no provider-truth or PIT certification by hashes |
| [EQ054 /61](https://github.com/atulsrivas1/equity-features/issues/61) /5 | EQ043 plus EQ049–053 | Existing SDK against actual installed DuckDB adapter, public synthetic DuckDB/Parquet fixtures; independent expectations | [Test matrix](R4_TEST_STRATEGY.md), bothOS clean wheel/sdist conformance, limits/cancellation, core isolation; executable fixture guide | Actual DuckDB conformance and synthetic integration, not an in-memory substitute |
| [EQ055 /62](https://github.com/atulsrivas1/equity-features/issues/62) /8 | EQ054 accepted; source scope supported | Freeze bounded licensed real instruments/sessions/identities after inspection; independent feature goldens and justified tolerances; record blocked cases | Source/optimized counts/identity/time/price/units/coverage, installed numerical APIs, evidence/quality, measured reads; private pinned report plus publication-safe methodology | Actual-data adapter and numerical integration evidence; no full-corpus inference |
| [EQ056 /63](https://github.com/atulsrivas1/equity-features/issues/63) /5 | EQ049–055 accepted | Optional installable artifacts, mappings/docs/examples, synthetic and actual evidence; preserve experimental source limits | Final-head review/CI, reproducible builds/installed examples/core isolation, published artifact/readback, eight-stage issue reconciliation; R4 acceptance | Eight stories Done, E07 and milestone5 closed; stop bounded R4 |

Each linked pre-code plan must be concretized with signatures/configurations,
expected fixtures, source limits, tests/docs and acceptance before coding. Update
plans with actual decisions and keep reviewed code and delivery evidence aligned.
Do not declare all eight In progress to reflect an autonomous mission.

Individual plans: [049](stories/EQ-049_PLAN.md), [050](stories/EQ-050_PLAN.md),
[051](stories/EQ-051_PLAN.md), [052](stories/EQ-052_PLAN.md),
[053](stories/EQ-053_PLAN.md), [054](stories/EQ-054_PLAN.md),
[055](stories/EQ-055_PLAN.md), [056](stories/EQ-056_PLAN.md).

## Two required testing layers

Follow [R4_TEST_STRATEGY.md](R4_TEST_STRATEGY.md). Synthetic temporary databases
exercise known independent edge cases publicly with no credentials. Real-data
tests then freeze actual bounded source populations and run installed public
calculations against independent expectations. Missing versus empty, availability,
precision, provenance, query/copy/resource costs and unsupported capabilities
must remain visible. Independent goldens cannot be blindly copied from legacy
worker outputs. Physical rewrite verification and formula correctness are separate.

Record actual completed checks, not planned test counts. No private paths or paid
rows in public fixtures/docs/artifacts. Use a private local companion for catalog
paths and actual licensed-source evidence. Published methodology/limits may be
sanitized; source redistribution rights are not granted by the code license.

## Current data readiness and known gaps

Retained optimized market catalogs contain trades, trade-sampled quotes, minute
and daily bars. Longer daily/minute history is present, but per-instrument warm-up
and completeness need qualification. Existing source schemas may store times as
strings and prices as floating point; do not invent exact original price precision.
Validate declared normalization with raw support where necessary, int64 bounds,
share units and preservation of nulls/unknown known-at. File/row occurrence identity
does not prove exchange sequencing or execution uniqueness. Curated/prepared
overlap and daily dataset substitutions need explicit selection and lineage.

TBBO cannot certify continuous quote coverage. Versioned session calendars,
holidays/early closes/DST, trade eligibility and reference admission need explicit
governance. Corporate actions/index references and recent sector snapshots exist,
but do not infer complete historical sector/universe membership from present files.
Unavailable reference/PIT/precision cases may remain typed unavailable with exact
limits. Do not secretly buy/fetch provider data to fill gaps.

Existing derived equity/option outputs are historical audit/comparison data, not
production-authoritative goldens. Context/watchlist/legacy baseline imports are
not prerequisites for basic adapter work: explicit caller composition can compute
required baselines from admitted supplied market history. Future outcome tables
must stay outside feature inputs. More imported bytes do not remove admission gaps.

## Bootstrap, progress, failures and exit

Use a dedicated checkout, fetch and inspect actualmain, preserve unrelated work,
establish pinned supported CPython3.12/development requirements, run baseline
units/reference/typing/boundary/import/registry/compatibility/license checks and
existing consumer qualification. Editable baseline checks do not establish clean
artifact acceptance. Add DuckDB only to the optional adapter and its tests; retain
core import/run checks with DuckDB forbidden.

Publish pre-code plans and maintain per-story delivery receipts, actual issue/
Project stages, changelog/API/install/evidence and SESSION_HANDOFF.md. Required
checks and independent review gate each final head; choose relevant tests, avoid
redundant mirror tests, and investigate failures rather than bypassing them.
Installed acceptance runs must use actual built/downloaded artifacts, not source
fallback. Record Windows local versus nativeLinux CI provenance honestly.

Proceed autonomously within R4; if blocked, retain the exact issue/evidence and
advance independent authorized work. When review/source/external access leaves
no dependency-ready work, report the blocker and required owner action rather than
poll forever, fabricate Done or expand scope. No recurring automation is created.
Close R4 only after all eight accepted delivery/readback records and actual
synthetic plus representative real-data qualification. Stop before R5.

## Kickoff prompt

Complete bounded R4 in atulsrivas1/equity-features using this handoff, current work
agreements, all eight plans and R4_TEST_STRATEGY.md. Recheck R2/R3/main/Project/
artifact evidence, dedicated checkout and private readiness companion. Begin with
EQ049; one active story, plans before code, required separate final-head review,
real lifecycle, installed artifacts and documentation alongside every story. Require
both actual DuckDB synthetic conformance and frozen representative real-data
numerical integration. Preserve source gaps/originals and private data; no R5,
providers, remote service, stable/PyPI/tag or historical generation. Resolve review
authorization explicitly where necessary; do not infer it from earlier bounded R3.
