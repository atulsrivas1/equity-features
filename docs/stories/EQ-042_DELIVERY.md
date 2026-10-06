# EQ042 resource behavior delivery

[Issue48](https://github.com/atulsrivas1/equity-features/issues/48), E06/R3; [plan](EQ-042_PLAN.md), [resource behavior](../RESOURCE_BEHAVIOR.md), [21 measured cases](../benchmarks/EQ-042_WINDOWS.md), [raw observations](../benchmarks/EQ-042_WINDOWS.json), [source PR247](https://github.com/atulsrivas1/equity-features/pull/247).

Corepair0.0.4a4/consumer0.3.0 and all equations/schema/config/state/capability meanings unchanged. Final reviewed source f94407be47bf68c9faa7a6feea9f04470214dc3c, guarded source-main `df9c9438448aaae2e8c6604f7374f5c9786ddc71` has its exact tree; all13 actual changed published blobs/owner attribution verified. Source-main [Foundation37491810918](https://github.com/atulsrivas1/equity-features/actions/runs/37491810918) and [docs37491810884](https://github.com/atulsrivas1/equity-features/actions/runs/37491810884) bothOS pass.

## Independent measurements and review

Full21case Windows measurement source b6e84c3eb6c92b39177908edfa5d03ff8adad178 was clean; later results publication changes documentation only. Normalized LF diagnostic SHA47b19ccb282b7d99d84d342166ea0c3763b7afb0df94fb25c66c1877109674b0, native probe SHAa481f45163d3a0061de24920357a168a57d08690aa47394b0e7e288177b12579. Fixed K8/Nobs5/W2/chunks128 at128/2048/8192rows and separate8192/chunks16 K64/Nobs50/W20 cases all pass independent counts/sums/close-weighted price/topK ties/window shares/spread/time-duration goldens, batch/stream/exact restore/legal partition merge and original-state immutability. Retained dimensions stay fixed while input graphs grow; Python graph bytes vary with sharing/layout. No raw CanonicalBatch occurs in these explicitly no-prior/no-seed graphs, with independent injected-retention positive detector. Fixed supplied prior/seed context is separately owned input, not covered by that absence assertion.

Wrongordinal/contradictorycertificate reject inconsistent_identity; incompatible/rehashedcorrupt state reject invalid_schema atomically. External adapter cancellation before acquisition yields0/CANCELLED and betweenchunks1thenCANCELLED; row/chunk limits reject LIMIT beforeyield. Caller-stop preserves honest count1prefix. Unsupported kernel threads/cancelled config rejects invalid_config; no midkernel cancellation/core threadbudget/concurrent mutable-call guarantee. Owned reducer creation entrypoints denied without observed thread/process/subprocess creation; arbitrary callbacks/backends are not certified.

Reachable builtin/owned Python graph sizes exclude globals/code/unknown native buffers, deduplicate IDs and are version-specific diagnostics, not exclusiveownership/allocation/nativeRSS or private API. Public unsealed/sealed UTF8payload/retained K/Nobs/window dimensions, three coexisting merge states and independent input/result graphs are explicit. Native wholechild high-water includes input/diagnostics/restore/partitions/results/control checks before JSON output; Windowsbytes/LinuxKiBtimes1024, no isolated allocation delta. No universal constantmemory/performance threshold or source-truth claim.

[Completed separate final-head review](https://github.com/atulsrivas1/equity-features/pull/247#issuecomment-6020136442), reviewer /root/r3_reviewer:626units/strict48/boundary/sixinstalledquick cases independently passed; all21raw cases/hashes/typed failures/parity/control/nativecheckpoint/scoped limits inspected. Original224255d historical UTF8 punctuation corruption corrected at finalf94407b and exact unchanged history verified. No unresolved findings. No fullbaseline rerun/artifact rebuild/nativeLinux/hosted or human review. Author TWOactualfresh local wheel/sdist pairs each626tests/22examples/consumer0.3.0walkthrough/installedtyping/core-byte invariance plus installed benchmark/resource smokes pass. All emitted finalhead CI passed before guarded source merge;123mathrefs unchanged.

## Actual source artifacts

BOTH exactclean epoch1700000000 manifests/all8core archives digest/content/license/typing inspected. FOURactual CI benchmark JSON and FOURresource JSON separately verified exactclean source/harness/nativeprobe/math/parity/statistics/bounds/control/nativeunits. Variable observations are not deterministic archive bytes. FOURactual source pair fresh local Windows installs remain required before receipt acceptance; nativeLinux remains cited CI.

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

## Variable benchmark JSON

- Linux `benchmark-Linux-gz.json` SHA256 `6e84e3d5415b67b4dec00855474f005d9eb5ad3ddd3d8ce6fb1f171b918ff41e`
- Linux `benchmark-Linux-whl.json` SHA256 `630958fe6dff4d72b1165c48d1f638b4f5eb754c03fbdaf3482524dca0cbe123`
- Windows `benchmark-Windows-gz.json` SHA256 `bcf4ac9ca9f574a91c5a726f9ef3cf9edb91b49e952dc81a3b124c0c15da01e5`
- Windows `benchmark-Windows-whl.json` SHA256 `62672eb6502657f5a009becaf95a4af3c48390256abfa8c03601b396edd8dcc3`

## Variable resource JSON

- Linux `resource-Linux-gz.json` SHA256 `b29b496b58b9476a5ac05ce356ba8e4913076f283f525d4740c4b89b00ad6bc3`
- Linux `resource-Linux-whl.json` SHA256 `bc7126f23b3f8a4ae1f93be961b2ffc6534916daa83f001f46e3f7e613b950fc`
- Windows `resource-Windows-gz.json` SHA256 `dc0acd9ab146c9668549f8065c41c2dc0d88442dcd3e5b9dfedffa74eed811f9`
- Windows `resource-Windows-whl.json` SHA256 `0742d7d977771afd92b92d8c8e30fe1dfcef1720e37f74773272f6ef91b69c73`

## Final receipt gates

FOURactual source freshpair qualification, separate final-head receipt review and allCI remain required. Final published main/owner/changed blobs and BOTHactualfinal corearchive equality to FOURqualifiedsourcebytes must pass before Released/postreleaseverification/Done. Independently verify final variablebenchmark/resource JSON exactcleanmain/harness/math/statistics/nativeunits/thread/control/retainedshape facts; timing/memory observations need not equal earlier files. EF-L020 records graphscope and superseded UTF8 failure. Then pull dependency-ready EQ044; six other R3 stories remain after EQ042 acceptance. No stable/tag/registry/provider/R4 scope.
