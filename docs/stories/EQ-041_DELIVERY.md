# EQ041 measured benchmark delivery

[Issue47](https://github.com/atulsrivas1/equity-features/issues/47), E06/R3; [pre-code plan](EQ-041_PLAN.md), [methodology](../BENCHMARKS.md), [full local observations](../benchmarks/EQ-041_WINDOWS.md), [raw samples](../benchmarks/EQ-041_WINDOWS.json), [source PR245](https://github.com/atulsrivas1/equity-features/pull/245).

Corepair0.0.4a4 and consumer0.3.0 remain unchanged. Math/schema/config/state/capability meanings unchanged. Final reviewed source `5c178e3f957bb08c77ff72f2e8a8b6b2b1881232`; guarded source-main `ef99dd29d7291dab3e2230470d14f8628a687698` has its exact tree. All12changed actual published blobs and agreed owner author/GitHub server merge committer attribution verified.

## Measurements and independent checks

Harness lives outside both core packages, runs public installed kernels in isolated serial children, and rejects failed arithmetic/parity before timing. Seed41001/128uniform,16384uniform and16384skew trades; K8/chunks128,1024; independently exact integer/Fraction totals, fullsortedtopK, streamedfinal versus batch values/quality, governedhistorySMA/EMA/return goldens. Fixture/hash/runtime/hardware/clock/requestedthread versus effectiveArrow facts, min/median/max/rawdurations, creation/chunk/conversion timings and exposed buffer/ownership facts are explicit. Native process peak units Windowsbytes/LinuxKiBtimes1024 are wholelifetime, not retainedstate or calculator-only allocations.

Full measuredWindows source `efa8af7101e571a66a22aa9892ba9aa96b590075` was clean with normalizedLFharnessSHA `a481f45163d3a0061de24920357a168a57d08690aa47394b0e7e288177b12579`; subsequent source/results publication changes docs only. Actual checked aggregates112006/138273/127748rows/sec, topK79751/89603/87344rows/sec, wholechild49.79/71.14/70.97MiB are observations, not thresholds/speedups/production capacity/platform comparisons. All three rawcases retain actual hardware/backend/three repetitions/limits. Selected historyrows128/512/period20/anchorS0/return19 are distinct from tradeN. No benchmark claim covers every39ID, source truth or arbitrary custom callbacks; EQ042 separately measures retained state.

## Separate review and local/source CI qualification

[Completed final-head separate local review](https://github.com/atulsrivas1/equity-features/pull/245#issuecomment-6019494076) by /root/r3_reviewer found no actionable findings. Independently executed installedquickbenchmark,622units/strict48/boundary/threebenchmarktests; verified independentoracles/streamparity/conversionownership, rawstatistics/throughput/MiB/harnesshash, unchanged runtime/build/test from measuredsource and correctnativeunits/limits. No fullbaseline rerun, artifact rebuild or localnativeLinux; local automated review is not hosted activation or human approval.

Author622units/strict48/policies pass. Repeated four core archives reproduce; TWO fresh local wheel/sdist pairs each622tests/22examples/consumer0.3.0walkthrough/publictyping/core-byte invariance and isolated installed smallbenchmark pass. Clean final5c178e3 manifests and allSIXexactheadCI pass before guarded merge. Source-main [docs37487086358](https://github.com/atulsrivas1/equity-features/actions/runs/37487086358) and [Foundation37487086274](https://github.com/atulsrivas1/equity-features/actions/runs/37487086274) bothOS pass; unchanged123independent math references remain separateCI gates.

BOTH actualsource downloaded exactclean/epoch1700000000 manifests and all8archive content/hashes/license/typing inspected. FOUR actual bothOS wheel/sdist installedquickbenchmark JSON verified against exactsource/harness/core/backend/seed/goldens/parity/samples/statistics/nativeunits/threadfacts. Variabletimingfiles are separately hashed below, not deterministic corearchives. FOURfreshlocalWindowsactualsource pair installations remain required before receipt acceptance; nativeLinux is citedCI, not localWindows execution.

## Actual source core archive hashes

### Linux

- `equity_feature_contracts-0.0.4a4-py3-none-any.whl` SHA256 `acaa84fc0340c4640ced2b7cdbef04d5ba7cfaec20cd0525b866b415147635cc`
- `equity_feature_contracts-0.0.4a4.tar.gz` SHA256 `f32a66f31759b10c9ac251f4dffb2388a3e2ce50d2e5e15c69ac7038828f97a9`
- `equity_features-0.0.4a4-py3-none-any.whl` SHA256 `cf8965e1600a3d8ef10dbefcfdea21f2d48ad8c8f80e0268abe12c365b1cd26e`
- `equity_features-0.0.4a4.tar.gz` SHA256 `14e7b8b0ec1b245747d53081a73c9ef060c0f637d205ae97b5e14304b4d95c8f`

### Windows

- `equity_feature_contracts-0.0.4a4-py3-none-any.whl` SHA256 `3fb31963c1f51b64c4b82fc874c1c38cc9c73461b933fb06d52f84bb29b7c7b2`
- `equity_feature_contracts-0.0.4a4.tar.gz` SHA256 `c0f35f1fd775b83ab9fdd48177c6332f38b1c83cc2f9986467e0852ca758ae57`
- `equity_features-0.0.4a4-py3-none-any.whl` SHA256 `0ff0745acf75f45ae7a2b38c7c106af200448f3026e4997fd0747101c79071f0`
- `equity_features-0.0.4a4.tar.gz` SHA256 `c25ab736eb267cd11a11d52cbeda6931d23796c94bb264164014f0dd542f1d06`

## Actual source variable benchmark JSON hashes

- Linux `benchmark-Linux-gz.json` SHA256 `bfcb59a32fef3fedc5d7df4fa29303c6c4d1dc25d58c739ce0772789bc0a0ada`
- Linux `benchmark-Linux-whl.json` SHA256 `427009176b8afbfd3c88ae8e04de49b69d2b09f67039640d4a8cabde870d6676`
- Windows `benchmark-Windows-gz.json` SHA256 `8c9d36014afb4cee8a2bbe115d1535935cc73f399a5615d186957e3a6e75b661`
- Windows `benchmark-Windows-whl.json` SHA256 `f9dc09c6dedaa5e82db23b26e72232a9423f09b61ddcc7a4e4287c2d1f5b2986`

## Final receipt gate

Issue47 requires actual FOURfresh sourcepair qualification, separate final-head receipt review, allCI, exact published finalreceipt-main source/owner and BOTHactualfinalarchive bytes equal FOUR-qualified source bytes beforeReleased/postrelease verification/Done. Finalmain variablebenchmarkJSON must independently match finalclean source identity/harness/math/statistics/nativeunits/threadfacts; its elapsed/peak values need not equal earlier observations. No fictional deterministic timing equality. Receipt also replaces obsolete no-measurement wording in current API docs with actual bounded observations/no universal guarantee. Then pull dependency-ready EQ042resources; seven later R3 stories remain after accepted EQ041. R3 remainsopen, no stable/tag/registry/R4 or provider scope.
