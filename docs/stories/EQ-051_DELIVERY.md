# EQ051 bounded historical reads delivery

[Issue58](https://github.com/atulsrivas1/equity-features/issues/58), R4/E07,
[source PR264](https://github.com/atulsrivas1/equity-features/pull/264),
[plan](EQ-051_PLAN.md), [API](../api/DUCKDB_READER.md),
[actual installed measurement](../benchmarks/EQ-051_READ.md).
Recorded October6,2026. Qualified source; final receipt/publication gates precede
closure. R4 conformance and private numerical acceptance remain EQ054/055.

## Behavior, compatibility and limits

Optional0.1.0a3 reads original local Parquet with exact UTCns and bound
instrument/time/supplied-session filters. Events are half-open; completed minute/
UTCdaily intervals must fit wholly. Physical original occurrences survive selection
and deterministic time/file/row ordering. Eager bounded population maps once, then
owned chunks retain stable mapping/schema/source coverage and unique input IDs.
ReadResult exposes full canonical population, envelopes, metrics and MappingReport.
Default source coverage remains unknown; exact matching caller assertions retain
selected-population coverage only. Missing partition differs from observed-empty.
Private read-only connections, safe errors and cooperative cancellation are tested.
No file-date calendar inference, provider truth, exchange sequencing, unknown PIT
certification, auction/live/continuous quotes, adjusted/reference acquisition,
zero-copy or hard synchronous-query/process-memory cap is promised. Same-sized
source mutation stability belongs to EQ053. Pure corepaira4/consumer0.4.0/math/
schema/modes/dependencies are unchanged; optional runtime additionally pins existing
governed NumPy2.2.6 because actual DuckDB1.5.6 UDF registration requires it.
Existing [upstream integrity](../RELEASE_INTEGRITY.md) records its notices/provenance.

## Reviewed source and corrected failures

Concrete pre-code dfde1b1 preceded implementation. Final PR264 head
`15f70080f62898bb8e152bc79c852e23b4cca0ef` independently reviewed by separate local
automated Codex `/root/eq049_review`: [review6024700509](https://github.com/atulsrivas1/equity-features/pull/264#issuecomment-6024700509).
Reviewer executed actual installed62tests/strict4/core633/64row measurement,
boundary38negative+10positive/import/registry, UTF8/190relative links/privacy/diff,
actual module/wheel identities and full measurement documentation/provenance.
No unresolved findings; no human/hosted review or reviewer fresh-sdist/nativeLinux
claim. Initial P2 null timestamp UDF bypass was independently reproduced, corrected
with special null handling and actual default/claimed-empty rejection regressions.

Initial synthetic setup hit catalog database/schema naming ambiguity; retain
catalog.duckdb regression and quote/qualify metadata identifiers. Literal DECIMAL
prices and an unquoted close alias were corrected in fixtures, preserving the
promised retained DOUBLE type. First actual installed wheel (2failures/10errors)
and prior optional CI failed because development NumPy masked a runtime dependency;
explicit optional pin restores clean installation. Benchmark parameterized range+
COPY output triggered a backend restriction; separate bound fixture creation and
bound output copy corrected it. Failed/superseded runs are excluded. A private
verification helper initially included a schema-less manifest among report checks;
corrected by skipping manifests and current identities reran successfully.

Author actual wheel/sdist installed62suite/strict4/quick read/core invariance pass.
Local repeat-build began9f80670; docs-only head advanced during qualification. Each
form's provenance was respected and wheel qualification reran at frozen15f7008,
leaving all four local install/read reports current, with unchanged runtime/archive
bytes. The full512/4096 three-sample measurement is accurately dated to clean
9f80670 actual installed wheels, not relabeled as final-head execution. All10
final-head CI checks passed before guarded squash merge.

Source main `34a06153114e22a2b8a14088608a1d0379f183ea` matches reviewed tree; all18
actual changed public blobs and owner author verified. Current main
[docs37525927446](https://github.com/atulsrivas1/equity-features/actions/runs/37525927446),
[Foundation37525927636](https://github.com/atulsrivas1/equity-features/actions/runs/37525927636)
and [optional37525927655](https://github.com/atulsrivas1/equity-features/actions/runs/37525927655)
succeed. BothOS actual bundles downloaded and inspected:24 archive hashes and20
current native report facts/harness/test-suite/native-probe identities verify.
Foundation12archives equal accepted EQ050/R3 bytes. Six optional/core wheel RECORDs
validate. Optional four native installed reports bind62cases, strict4, current
source/actual form hashes/runtime and before-after pure-core invariance; four
native64row measurement reports retain independent parity and correct peak units.
Foundation12reports retain current source/parity/43consumer outcomes/core invariance.
Variable timing values are not required to be byte equal.

FOUR fresh actual downloaded producer/form pairs independently installed locally
on Windows: each62tests/strict4/64row measured parity/core without and forbidden
DuckDB plus before-after core module/metadata bytes pass. NativeLinux execution is
CI; Linux-built forms running Windows are not nativeLinux evidence. No provider or
private numerical acceptance is inferred.

## Actual source-main optional archive identities

| Archive | Linux SHA256 | Windows SHA256 |
| --- | --- | --- |
| equity_feature_contracts-0.0.4a4-py3-none-any.whl | `acaa84fc0340c4640ced2b7cdbef04d5ba7cfaec20cd0525b866b415147635cc` | `3fb31963c1f51b64c4b82fc874c1c38cc9c73461b933fb06d52f84bb29b7c7b2` |
| equity_feature_contracts-0.0.4a4.tar.gz | `f32a66f31759b10c9ac251f4dffb2388a3e2ce50d2e5e15c69ac7038828f97a9` | `c0f35f1fd775b83ab9fdd48177c6332f38b1c83cc2f9986467e0852ca758ae57` |
| equity_feature_duckdb-0.1.0a3-py3-none-any.whl | `4f6e67c20990dbe6acf7d5b1fcf54f27a0efd9ee1b8937075ef3c85ae2fdf274` | `9587be27ce37c0b846dac2a9a7879562538b07b7fbb15725dd13442423c27325` |
| equity_feature_duckdb-0.1.0a3.tar.gz | `c3019d3abc90a64cf622601a1e42e63cbefdd515b17401814925f42c6fa231f3` | `fc0b00ecc13aa21b46873e63420d15d9d574d2588caa9a64d5f64177b672b312` |
| equity_features-0.0.4a4-py3-none-any.whl | `cf8965e1600a3d8ef10dbefcfdea21f2d48ad8c8f80e0268abe12c365b1cd26e` | `0ff0745acf75f45ae7a2b38c7c106af200448f3026e4997fd0747101c79071f0` |
| equity_features-0.0.4a4.tar.gz | `14e7b8b0ec1b245747d53081a73c9ef060c0f637d205ae97b5e14304b4d95c8f` | `c25ab736eb267cd11a11d52cbeda6931d23796c94bb264164014f0dd542f1d06` |

Current producer CPython: Linux3.12.14; Windows3.12.10.
Within-checkout/OS/toolchain repeatability only; cross-platform or newline-different
checkout byte identity is not promised. Actual declared downloaded bytes were
qualified directly; pure core archives retain accepted hashes.

## Experimental channels and remaining final gates

- `duckdb-34a06153114e22a2b8a14088608a1d0379f183ea-ubuntu-24.04`: server `sha256:4fac96005ba2a4369259105d0c1f1ed4d9d6cc627dab7b9adef0222bf9c914a1`, 272429bytes, actual expiryUTC `2026-11-05T20:23:18Z`, observed not expired.
- `duckdb-34a06153114e22a2b8a14088608a1d0379f183ea-windows-latest`: server `sha256:d3f28da8df1870e06b60cea2f31532c788db9df55d243de931ee4821e94c8d66`, 273725bytes, actual expiryUTC `2026-11-05T20:24:41Z`, observed not expired.
- `foundation-34a06153114e22a2b8a14088608a1d0379f183ea-ubuntu-24.04`: server `sha256:43c7a555daf6965fafd0406ebbb3cb9ac42ca51ec9aa7fdaa1d05a65ec6702e9`, 273824bytes, actual expiryUTC `2026-11-05T20:24:17Z`, observed not expired.
- `foundation-34a06153114e22a2b8a14088608a1d0379f183ea-windows-latest`: server `sha256:4b8cedc9495941cbcb88b936c276b7ac9ae1459104ec9d4424ed5b828a32faff`, 275118bytes, actual expiryUTC `2026-11-05T20:25:36Z`, observed not expired.

Server bundle digests differ from inner archive hashes. Requested30day retention
is finite; recorded source/pins support later rebuild. No stable registry/tag or
new publication channel. Separate receipt final-head review/allCI, guarded exact
main/public blobs/owner, actual final-main archive equality/current20report facts/
expiry and Released postrelease readback remain before Done. Doc-only receipt
reuses these four qualified forms only with final byte equality/current reports.
Next EQ052 resolves explicit governed calendar/history/reference requests, then
EQ053-056 remain planned. Stop after bounded R4; no worker, provider purchase/
download, source deletion, historical restart, R5 or account administration.
