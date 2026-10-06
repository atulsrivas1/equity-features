# EQ050 retained equity schema mapping delivery

[Issue57](https://github.com/atulsrivas1/equity-features/issues/57), R4/E07, [plan](EQ-050_PLAN.md), [source PR262](https://github.com/atulsrivas1/equity-features/pull/262), [mapping API](../api/DUCKDB_MAPPING.md). Recorded October6,2026. Source qualified; final same-story receipt gates precede closure. R4 remains incomplete.

## Behavior and limits

Optional equity-feature-duckdb0.1.0a2 maps retained trades, trade-snapshot quotes, minute and UTCdaily OHLCV into unchanged schema1/corepair0.0.4a4. Callers explicitly declare price/currency/interpretation/rounding, source clock, instrument/session/occurrence identities and trade eligibility policy. UTCns parsing uses integer day/fraction arithmetic; shares and price coefficients check int64. Accepted quantize_float_prices supplies conversion reports; mapping digest binds columns/policy/metadata/occurrences and extends source input/mapping identity.

Missing columns/nulls/zero and unknown known-at remain distinct. TBBO never becomes continuous quotes; UTCdaily never becomes RTH daily. No inferred ticker permanence, source admission, provider truth, eligibility, availability, calendar, PIT or original scaled coefficients from DOUBLE. Semantic validation rejects bad order/duplicates/OHLC/quantities instead of hidden sorting/filling/clearing. A bounded explicit caller population is mapped once; later delivery chunking must preserve its mapping identity. No historical acquisition, numerical/private-source acceptance or scheduler/live support yet. Pure core packages, consumer0.4.0 and39batch/23update-restore/22conditionalmerge remain unchanged.

## Reviewed source and tests

Concrete pre-code8ae6d0d preceded implementation. Frozen final `bc370d2ce91aa54fead2dec24803dc4e2267e1ef` separately reviewed by local automated Codex `/root/eq049_review`: [completed review](https://github.com/atulsrivas1/equity-features/pull/262#issuecomment-6024069428). Independent46optional/633core/strict3/boundary38negative+10positive/import/registry pass;200 additional seeded exact timestamp cases and eligibility-scope mismatch rejection pass. Current UTF8/222 changed-document relative links/privacy and diff checks pass. No actionable findings; no human/hosted review or reviewer installed-build claim.

Development new-prose legacy encoding and subsequent newline-translation failures were corrected from pre-repair bytes; current full public UTF8/links/privacy/clean diff pass. Earlier failures are superseded, never acceptance evidence. Private four-family type-only inspection publishes no actual rows/source identifiers. No real golden frozen.

Author clean frozen repeat builds six archives; actual wheel/sdist installed46case suites, installedstrict3 and core absent/forbidden DuckDB before/after byte invariance pass. Core formulas/schema/modes are unchanged; relevant current Foundation/documentation checks preserve accepted numerical/unit baseline.

Guarded actual source main `6f3891f3e19fc5001340a07e36266ad902c8b935` matches reviewed tree; all15 actual changed public blobs and owner author verified. Source main [documentation37520940373](https://github.com/atulsrivas1/equity-features/actions/runs/37520940373), [Foundation37520940262](https://github.com/atulsrivas1/equity-features/actions/runs/37520940262) and [optional37520940219](https://github.com/atulsrivas1/equity-features/actions/runs/37520940219) all succeed. Native bothOS optional form reports bind46tests/installed typing/current source/exact input artifacts/core invariance and explicitly false real-data qualification.

Current source-main producers: Linux CPython3.12.15; Windows CPython3.12.10. Producer provenance is distinct from earlier PR/local evidence even when archive hashes match.

Both actual optional bundles downloaded: twelve archive hashes/four native installed reports independently verified. FOUR fresh actual delivered-form installations (both producer wheel/sdist pairs) run locally on Windows:46tests each, installedstrict3, pure core without/forbidden DuckDB and before/after core byte invariance pass. Native Linux execution comes from CI; no emulation claim. Actual Foundation twelve core/consumer archives equal accepted R3/EQ049 bytes; twelve current benchmark/resource/consumer reports bind source, parity,43-case consumer qualification and core invariance. No variable timing-byte equality or fresh numerical claim.

## Actual source-main optional channel archives

| Archive | Linux SHA256 | Windows SHA256 |
| --- | --- | --- |
| equity_feature_contracts-0.0.4a4-py3-none-any.whl | `acaa84fc0340c4640ced2b7cdbef04d5ba7cfaec20cd0525b866b415147635cc` | `3fb31963c1f51b64c4b82fc874c1c38cc9c73461b933fb06d52f84bb29b7c7b2` |
| equity_feature_contracts-0.0.4a4.tar.gz | `f32a66f31759b10c9ac251f4dffb2388a3e2ce50d2e5e15c69ac7038828f97a9` | `c0f35f1fd775b83ab9fdd48177c6332f38b1c83cc2f9986467e0852ca758ae57` |
| equity_feature_duckdb-0.1.0a2-py3-none-any.whl | `94b136bcad98d5c893a754aedb697fbb6d5826d985b915190c7e0fcc19988677` | `72ddfbe196173b50a7a5adc186c923c8a2f6e2786b4c67e20ee0fc830ab1dbf6` |
| equity_feature_duckdb-0.1.0a2.tar.gz | `3641352efcd427208f61d2c43a9c5978ab42c14e9c197ff9ddaea44bfe84ef44` | `1a23214d4c50c5fd88a1bf8aec96d262f27770ab19e77e2175ab9df7c05576fb` |
| equity_features-0.0.4a4-py3-none-any.whl | `cf8965e1600a3d8ef10dbefcfdea21f2d48ad8c8f80e0268abe12c365b1cd26e` | `0ff0745acf75f45ae7a2b38c7c106af200448f3026e4997fd0747101c79071f0` |
| equity_features-0.0.4a4.tar.gz | `14e7b8b0ec1b245747d53081a73c9ef060c0f637d205ae97b5e14304b4d95c8f` | `c25ab736eb267cd11a11d52cbeda6931d23796c94bb264164014f0dd542f1d06` |

Within-checkout/OS/toolchain repeatability only: source local versus Windows main optional archives differ only in resolver.py LF/CRLF and derived wheel RECORD bytes; member sets match and non-RECORD changed bytes normalize identically. Actual downloaded declared delivery bytes are qualified independently. No cross-checkout/platform identity guarantee. Unchanged core archives retain accepted hashes.

## Retention and final gate

- `duckdb-6f3891f3e19fc5001340a07e36266ad902c8b935-ubuntu-24.04`: server `sha256:e9ab6a11a518490c8074082f28dda9c83964394f24d919a4a4df87953ae60b0c`, 259538bytes, actual expiryUTC `2026-11-05T19:42:56Z`, observed not expired.
- `duckdb-6f3891f3e19fc5001340a07e36266ad902c8b935-windows-latest`: server `sha256:64a8a16c432e71f915e7b9ad23153cd9065658b36891c6a4d7a4d21c2ea86a9b`, 260716bytes, actual expiryUTC `2026-11-05T19:43:49Z`, observed not expired.

Server bundle digests differ from inner archive hashes. Requested30day retention is finite; rebuild recorded source/pins after expiry. Existing [DuckDB dependency inventory](../DUCKDB_DEPENDENCY_INVENTORY.json) retains actual pinned native archive/shipped-notice observations and limitations; no new third-party pin or universal license certificate.

Final receipt separate review/CI, guarded main/exact public blobs/owner, actual final-main archive equality/current report provenance/expiry and Released postrelease readback remain before Done. Receipt is doc-only: reuse these actual qualified forms with final equality/current reports, preserving runtime/tests/tools/packages. Then EQ051 bounded reads follows accepted050; EQ052-056 governed sessions/evidence/actual synthetic conformance/private numerical/final R4 acceptance remain open. No provider download/purchase, R5, source deletion, historical restart, registry/tag or remote publishing.
