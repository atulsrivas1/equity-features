# EF3 contract E amendment E-A2: knowledge gating of bounds, edge and population facts

Status: decided by the architect/PO ruling R5 of 2026-10-27 ([EF3_SHARED_AMENDMENT.md](EF3_SHARED_AMENDMENT.md)), pending owner review; nothing is accepted. It amends the frozen [ROBUST_PACE_CONTRACT_PROPOSAL.md](ROBUST_PACE_CONTRACT_PROPOSAL.md) (producers `ef3.robust_history`, `ef3.volume_pace_robust`, `ef3.volume_ratio_mean`) additively; the frozen contract files are not edited. Fixtures: [ROBUST_PACE_AMENDMENT_E_A2.json](ROBUST_PACE_AMENDMENT_E_A2.json); checker: `tools/verify_ef3_robust_known_at.py`.

## Why

The contract states "Knowledge is enforced identically in `known_at` and reconstruction modes" and gates data rows and exclusion facts, but is silent on the other reference facts. Contract F ([BREADTH_ADAPTIVE_CONTRACT_PROPOSAL.md](BREADTH_ADAPTIVE_CONTRACT_PROPOSAL.md)) gates declared-population rows (`ef3.population.member`) and its code does so, so the same fact kind was gated in F and only disclosed in E. A point-in-time result must not use a session boundary, grid edge or cohort membership that was not yet known at the knowledge cutoff K.

## Rule

For a reference fact of kind `ef3.session.bounds`, `ef3.bucket.edge` or `ef3.population.member` that a selected output uses, with original `known_at_ns` and knowledge cutoff K (the same rule as data rows and exclusion facts):

| `known_at_ns` | Result |
| --- | --- |
| null (or the column absent) | reason `unknown_availability` |
| greater than K | reason `future_knowledge` |
| at most K (K itself is available) | none |

The reasons join the output's other reasons; status follows DP-Q1 (`unknown_availability` and `future_knowledge` rank above `null_field`, `governed_gap` and the rest, all `missing_input`); the value is null while any reason applies. `expected` and `observed` are unchanged. Witness rows are emitted only for an available value, as before. No new reason, status or error code: there is no typed refusal for knowledge, exactly as in F, where the same two reasons are quality reasons. Refusal fixtures RF01 to RF48 are unchanged.

Facts used by a selected output:

- **Session bounds** (history, pace, mean): the bounds fact of the target session and of every session in the governed window of that output, including a session removed by a declared exclusion (the exclusion removes it from the sample, not its bounds from the grid). Sessions outside the window are not read. In `ef3.volume_ratio_mean` each of `mean.numerator` and `mean.baseline` uses its own window plus the target; `mean.ratio` takes the union.
- **Population members** (`cohort.rank`, `cohort.percentile_rank`): every declared member fact, the target member included; one unknown or late member fact makes both cohort outputs unavailable (F treats the declared population the same way).
- **Bucket edges** (every pace output): every edge of the grid, because the evaluation bucket is derived from the whole grid.
- A role no selected output needs is neither validated nor gated (unchanged): history-only selections do not read the population facts, and so on.

Population-only fallback: not needed. The 124 existing result fixtures give these facts known_at 50 against K 100, so none changes (typed refusals precede assessment, so the 48 refusal fixtures are unaffected); a run of all of them through the amended library matches the frozen literals (530 runs, 0 differences).

## Fixtures (independently derived by hand)

Base cases are H01 (volumes 7,3,9,1,5; median 5, MAD 2, type-7 median 5, rank 3/5), a cohort of A=10, B=20, C=30 with target A (rank 3, percentile 1/6, declared 3), P01 (bucket-1 median 300, MAD 100, ratio 3/2, z 1 at k 3/2) and a mean case of volumes 10,20,30,40 (numerator window 2 mean 35, baseline window 4 mean 25, ratio 7/5). Each fixture changes only the listed `known_at` (all others 50, K 100). A late value is 150, an unknown value is null.

| Id | Producer | Change | Expected |
| --- | --- | --- | --- |
| KA01 | history | bounds of window session 2 late | all four outputs `missing_input`, `future_knowledge`, counts 5/5 (rank output 6/6) |
| KA02 | history | target bounds null | `unknown_availability` |
| KA03 | history | window session 2 bounds exactly K | available, equals H01 |
| KA04 | history | bounds of session 0, outside the window of 5 (6 prior sessions), late | not used: available, equals H01 |
| KA05 | history | window bounds late and null | reasons `future_knowledge`, `unknown_availability`, `missing_input` |
| KA10 | cohort | member B fact late | both outputs `missing_input`, `future_knowledge`, counts 3/3 |
| KA11 | cohort | member C fact null | `unknown_availability` |
| KA12 | cohort | B late and C null | both reasons |
| KA13 | cohort | B fact exactly K | available: rank 3, percentile 1/6 |
| KA14 | cohort | target member A fact late | `future_knowledge` |
| KA20 | pace | interior edge (index 2) null | `baseline_median` 5/5, `ratio` and `robust_z` 2/1, `unknown_availability` |
| KA21 | pace | last edge (index 3) late | `future_knowledge` |
| KA22 | pace | bounds of prior session 1 late | `future_knowledge` |
| KA23 | pace | target bounds null | `unknown_availability` |
| KA24 | pace | edge 1 and bounds of session 1 exactly K | available, equals P01 |
| KA25 | pace | bounds late and an edge null | both reasons |
| KA30 | mean | bounds of session 0 (baseline window only) late | baseline and ratio (2/1) unavailable, numerator 35 available |
| KA31 | mean | target bounds null | all three unavailable, `unknown_availability`, ratio 2/0 |
| KA32 | mean | bounds of session 0 exactly K | available: 25, 35, 7/5 |
| KA33 | history | window session 2 excluded (exclusion fact known 50), its bounds late; min_history 4 | the exclusion removes the session from the sample, not its bounds from the grid: all four outputs `missing_input`, `future_knowledge`, counts 4/4 (rank 5/5) |
| KA34 | history | same, bounds null | `unknown_availability` |
| KA35 | history | same, bounds exactly K | available on sample 7,3,1,5: median 4, MAD 2, quantile 4, rank 3/4 |
| KA36 | pace | prior session 1 excluded, its bounds late; min_history 4 | `future_knowledge`, `baseline_median` 4/4, `ratio` and `robust_z` 2/1 |
| KA37 | pace | same, bounds exactly K | sample 100,300,400,500: median 350, MAD 100, ratio 9/7, z 2/3 |
| KA38 | pace | no bucket ends by the market cutoff (`future_market`) and edge 3 late | reasons `future_knowledge`, `future_market`; status `missing_input` (knowledge ranks above); counts 5/0, 2/0 |
| KA39 | pace | `future_market` alone | `incomplete_coverage`, reason `future_market` (control) |
| KA40 | pace | first bucket end beyond the session (`ineligible`) and prior session 3 bounds null | reasons `ineligible`, `unknown_availability` |
| KA41 | history | history-only selection; population facts Y null and Z late are present | not read: equals H01 |
| KA42 | cohort | cohort-only selection; target session bounds null are present | not read: rank 3, percentile 1/6 |
| KA43 | history and cohort | both selected, member Z late | history equals H01; cohort `future_knowledge` |
| KA44 | history and cohort | both selected, bounds of session 2 late; members 6, 20, 2 | history `future_knowledge`; cohort rank 2, percentile 1/2 |
| KA45 | history | bounds role without a `known_at_ns` column | `unknown_availability` |
| KA46 | pace | edge role without the column | `unknown_availability`, counts as KA20 |
| KA47 | pace | bounds role without the column | `unknown_availability` |
| KA48 | cohort | population role without the column | `unknown_availability`, counts 3/3 |
| KA49 | mean | bounds role without the column | all three `unknown_availability`, ratio 2/0 |

`tools/verify_ef3_robust_known_at.py` expands each fixture to canonical batches and checks value, status, reasons and counts: 36 of 36 match on the amended library (KA01 to KA32 also: on the unamended library only the five available controls matched).

## Open items for the owner

1. The freeze says a change of convention needs a new policy label. The behaviour differs from the frozen contract only where bounds, edge or population facts carry null or late `known_at`, so the labels `ef3-robust1`, `ef3-pace1` and `ef3-mean1` and the config digests were kept. Whether to bump them with the version change is an owner decision; a bump changes content hashes.
2. Downstream: equity-feature-io and equity-feature-workers need no change for the 124 existing fixtures (their adapters write known_at 50 on these facts). To exercise the amendment end to end they would add per-fact `known_at` for bounds, edge and population facts and the fixtures KA01 to KA49; the I/O adapter currently fixes those at `KNOWN_AT_DEFAULT`.
