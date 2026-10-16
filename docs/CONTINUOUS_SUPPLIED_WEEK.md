# Installed supplied-week research example

Use the accepted public `equity-feature-continuous==0.1.0a2` API with synthetic
caller-supplied facts. [EQ115/PR420](https://github.com/atulsrivas1/equity-features/pull/420)
records actual current review and delivery. [Frozen twelve full expectations](stories/EQ115_SYNTHETIC_ORACLES.json)
were hand checked before consumer code; they are distinct from the99 kernel
allocations and219 codec vectors. [Plan](stories/EQ115_PLAN.md),
[API](CONTINUOUS_API.md), [R12 receipt](R12_ACCEPTANCE.md).

## Run with selected experimental artifacts

Download the current qualified contracts and continuous wheels from the linked
issue's Windows/Linux CI artifact, verify its published identity and use the
matching source checkout for this script and fixture. From a fresh Python3.12
environment, install the two selected wheels with `python -m pip install
--no-index --no-deps equity_feature_contracts-0.0.4a4-py3-none-any.whl
equity_feature_continuous-0.1.0a2-py3-none-any.whl` (one shell line). Then run:

```console
python -I -B examples/continuous_supplied_week.py docs/stories/EQ115_SYNTHETIC_ORACLES.json
```

There is no stable registry publication or provider setup. Source execution alone
does not verify a fresh install. Dedicated current qualification runs this exact
script from the selected verification snapshot, outside the repository, in each
fresh light/combined wheel/SDist form per Windows/Linux. The per-form receipt
binds the fixture SHA256, all12 case IDs/result digests and six own batch IDs.
All complete outputs are compared before that receipt is emitted; a digest-only
summary never substitutes for the full comparison. Preserve original quality.

## Supplied seven-day timeline

One synthetic day is86,400,000,000,000ns. The caller labels the finite epoch
Friday through Thursday, declares a reference pause [day1,day3) and reopening
atR=day3. These are supplied labels, not inferred calendars/holidays/DST or factual
exchange hours. Continuous live state covers the supplied seven-day range;
delivery census certificates cover only their explicit finite analysis scopes.
No completeness of observations outside those scopes is asserted.

| Case | Full expected interpretation |
| --- | --- |
| Friday basis |120-100=20 and20/100=1/5; availability is the original day1 coverage certificate. |
| Basis during reference pause |The chosen98/100 prices exist, but scheduled freeze is not live: missing_input/not_live. |
| Supplied weekend freeze |101,98,102 versus held100 gives1,-2,2; maxabs2, count mean5/3. Equal top deviations retain signed-2 then+2 in chronological order. |
| Continuous outage, stale or unknown |Three independent missing_input cases retain the actual continuous-feed reason. |
| Reference fact gap |A one-nanosecond gap at pause start is absent_fact, not scheduled-freeze evidence. |
| Incomplete census |Expected4/observed3/incomplete remains incomplete_coverage. |
| Unknown/late census knowledge |Unknown certification or certification afterK remains unavailable; price presence does not fill it. |
| First reopening before knowledge |First125@R is known onlyR+10; later126@R+1 already known byR+2 cannot replace it. |
| Same first reopening after knowledge |PreR120 versus125 gives-5 and-1/25, availableR+10. The1:1 mapping at the selected preR observation applies, despite a supplied2:1 mapping fromR. |

The complete literals retain all seven roles/reasons/proofs, selected identities,
signed topK, population, metrics, timing and own identities. Inputs bind unused
future mapping facts too. This synthetic example is not evidence of economic
equivalence, launch status, liquidity, price discovery, acquisition or data rights.

## Compatibility and bounds

All package sources and versions are unchanged by this guide. Old39 registry
IDs/config golden remain unchanged before/after opt-in install. There is no new
SessionSpec or old schema migration. Actual ConfigSpec.from_json(str) rejects own
envelopes; FeatureResult's constructor rejects own result metadata. FeatureResult
has no public JSON decoder. Own encoders reject old typed values. These domains
are deliberately separate; batch-only own discovery refuses update/merge/restore.

File reading belongs to the external consumer, which accepts one JSON fixture
path and uses a512KiB logical read cap. Its JSON receipt is limited to16KiB.
Calculations receive only the decoded supplied snapshots, no paths or callbacks.
The unchanged library caps are4096rows/leg,256facts,topK32,128UTF8-byte IDs and
64KiB/16MiB/1MiB config/input/result encodings. Existing oversized-result refusal
remains in installed tests. These are representation limits, not total RSS,
physical storage/kernel containment, hard deadlines or hostile-input isolation.
No performance claim is made. Workers/MCP/service/receipt APIs are unchanged.
