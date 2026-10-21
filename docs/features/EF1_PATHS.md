# Sampled gap and completed opening drive

The [frozen authoring contract](../ef1/PATH_SOURCE_AUTHORING_FREEZE.json) governs
these additive pure calculations. Source and independent tests are authored;
runtime numerical acceptance is pending. The [API](../api/EF1_PATHS.md) describes
the exact supplied roles, context and scopes.

Let A be actual regular open, Z actual regular close, C market cutoff, K knowledge
cutoff. Eligible trade candidates supply original positive price and size; O is
the first eligible price and samples are all eligible prices in canonical order.
For bars, candidates have positive volume, O is the first candidate open and
samples are all candidate closes. Zero-volume bars supply no sample. Missing or
null volume makes eligibility indeterminate. High/low never substitute for
sampled extrema or hits. Structural validation covers every supplied row/cell.

Every candidate, first opening witness and prior close requires original nonnull
known_at<=K in both known-at and reconstruction modes. Earlier unknown/late
candidates cannot be replaced with later-known candidates. Ineligible trades and
zero-volume bar price/knowledge payloads are not operands. All delivered rows
still contribute to quality population counts. Complete coverage of path and
prior is required independently of operand knowledge; supplied incompleteness
adds governed_gap even when expected equals observed. Proof readiness gates all
values. Reasons are unique and lexically sorted; any missingness reason takes
missing_input precedence over incomplete_coverage. No sample mathematics or
evidence is emitted while readiness fails.

For gap, P is the positive close of the single explicit prior-session DAILY row,
G=O-P and x ranges over the complete supplied sample population:

- remaining_fraction = max(0,(last-P)/G), with no upper clamp;
- fill_fraction = max over samples of clamp((O-x)/G,0,1);
- filled = whether any sample satisfies (x-P)*G<=0;
- first_fill_ns = earliest hit's original trade event time or completed bar end.

After readiness, empty/no-candidate paths yield null/not_applicable with
no_eligible_observations. Otherwise G=0 yields all four null/not_applicable with
zero_denominator. With no hit, filled is available false and first_fill_ns alone
is null/not_applicable/no_eligible_observations. Maximum-prefix fill preserves a
previous hit after reversal; latest/current-last legacy GapFillPercent is a
different projection and no equivalence is asserted.

For drive let B=A+duration. A prefix with C<B adds governed_gap even if its
delivered coverage is complete. On completion: return=last/O-1,
excursion_up=max(0,maxsample/O-1), excursion_down=max(0,1-minsample/O).
All ratios use integer coefficients and exact Fraction arithmetic before a
single Float64 conversion. Count arithmetic is checked int64.

Selected gap evidence associates remaining with O/P/last, fill with O and the
earliest maximum-clamped sample, and filled/first_fill with the earliest hit
when present. Drive return associates O/last, up the earliest maximum sample,
down the earliest minimum sample even when clamped to zero. Canonical input
order resolves equal-time ties. Evidence deduplicates per feature/input/row;
trade IDs and timestamps remain original. Bars use `bar:start:end`, original
end/known_at and completed_interval bounds for both operands; prior uses
`daily:session_id` with original end/known_at and bounds. No evidence is emitted
for missing, incomplete, empty or zero-gap results. Limits are seven/four,
without truncation. Calendar proof remains bound and consumes no witness budget.
