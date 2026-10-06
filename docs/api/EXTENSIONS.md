# Extending supplied-input calculations

Use supported parameters for an existing accepted equation; use explicit custom metadata and a trusted local calculator for changed meaning. Core pair0.0.4a4/custom schema1 supports canonical batch inputs, one declared output and no custom update/restore/merge. [Public API](PUBLIC_API.md), [custom contract](CUSTOM_FEATURES.md), [adapter mapping/SDK](../contracts/ADAPTER_KIT.md).

## Parameters and meaning

| Change | Identity and acceptance |
| --- | --- |
| Supported period, window, K/evidence limit, eligibility policy or supplied target/cutoffs under the documented algorithm | Preserve builtin feature ID/algorithm, supply a new ConfigSpec and digest; enforce its documented parameter bounds and timing/coverage rules |
| Range denominator changes from accepted close to opening price | Distinct custom ID such as demo:range_over_open/v2, new formula/units/timing/readiness metadata and independent golden |
| Initialization/smoothing, universe membership semantics, temporal admission or missing-data equation changes outside the documented policy | Version/distinguish the changed meaning explicitly and independently qualify it; a differently named parameter does not redefine builtin mathematics |
| Source implementation changes while mathematics/config stay the same | Preserve declared algorithm meaning and identify implementation/version; requalify affected behavior and provenance |

Builtin discovery contains39 reviewed IDs and actual capabilities. `Registry.with_definition` stores scoped metadata without an executable; it cannot override builtins. `CustomRegistry("demo").register(definition, calculator)` returns a new immutable registry, leaving old registries/builtin discovery unchanged. `list_features`/`get` discover only explicitly registered local entries. No global plugin import or automatic source discovery.

A CustomDefinition wraps FeatureDefinition schema1 with inner execution flags false, explicit implementation ID/version/config rule/named primitive parameter types, and actual batch-only capabilities. Declare canonical:1 roles/kinds/required fields, one output named by exact custom ID with dtype/unit/nullability, formula, initialization/warm-up, timing and missingness. CustomRequest carries owned canonical inputs, matching config ID/algorithm/parameter types and requested EntityKey. Semantic parameter ranges and actual equation remain calculator duties.

Return exactly one matching FeatureColumn/entity with independently aligned QualityRow and request.metadata(definition). Original source/snapshot/mapping/input bindings, C/K/E, config digest and actual implementation backend/version remain in ResultMetadata. Result admission reconstructs nested owned types and compares pre-callback copied identity; this enforces contracts, not a sandbox. Missing/incomplete/future/unknown data remains distinct; no manufactured zero or source row. Initially evidence retention is zero. Unknown IDs/malformed requests/unsupported modes reject before invoking a callback; callback exceptions propagate. Metadata to_json contains no executable and cannot restore a registration.

The public consumer0.3.0's synthetic session has O100/H104/L99/C103: custom range/open=(104-99)/100=0.05 versus unchanged builtin range/close=5/103. It uses explicitly admitted builtin v1 operands but its own v2 custom identity. Its separately packaged raw historical BAR adapter preserves exact facts, original known_at and full-source coverage separately from delivery chunks; supplied SDK cases check ordering/precision/availability/errors/bounds. Source acquisition is external to both core distributions. Trusted local code receives no purity/determinism/resource/mathematical/source-rights certification or sandbox. Remote executable upload/serialization is absent; provider/live/file/worker integration is later scope.

## Reproduce with actual installed public APIs

Use CPython3.12 x64 on a qualified Windows/Linux system. Download matching contracts/features artifacts from one accepted main [Foundation Actions run](../BUILD_DELIVERY.md) and verify its exact source/clean manifest/hashes before installation. Keep the matching public repository revision for tools/examples/consumer build; those resources are outside core archives. Do not use editable installs for qualification.

Create a fresh environment (`python -m venv installed-env`) and use its Python explicitly: `installed-env/Scripts/python.exe` on Windows or `installed-env/bin/python` on Linux. In the commands below `python` means that executable; replace the two artifact placeholders with actual matching wheel paths or both sdist paths from that run.

```text
python -m pip install --no-deps setuptools==80.9.0 build==1.2.2.post1 pyproject_hooks==1.3.3 packaging==26.3
python -m pip install --no-index --no-deps --no-build-isolation <contracts artifact> <features artifact>
python -m build --no-isolation --wheel --outdir consumer-dist examples/external_consumer
python -m pip install --no-index --no-deps consumer-dist/equity_feature_demo-0.3.0-py3-none-any.whl
python -m pip check
python -I -c "from equity_feature_demo import main; main()"
python -m pip install --no-deps mypy==1.15.0 mypy_extensions==1.1.0 typing_extensions==4.16.0
python -I tools/verify_public_typing.py
```

Commands require external pip/build tooling, not a network-capable core calculator. The consumer's pinned matching core dependencies prevent silently fetching unreleased packages. The isolated command resolves installed consumer/core public modules; the verifier checks actual site-packages/py.typed and rejects editable fallback. Expected output includes custom0.05, builtin5/103, public SDK adapter binding, positive caller/consumer typing and three rejected invalid calls. Run optional NumPy2.2.6/PyArrow20.0.0 and broader installed examples only under their documented compatibility requirements.

[tools/build_foundation.py](../../tools/build_foundation.py) repeats both core archive builds, inspects license/typing/privacy boundaries, and runs the consumer/typing verifier for each fresh wheel/sdist pair, alongside units/examples. It also fingerprints installed core files before/after external execution. No installed core edit, private import, credential or proprietary data is required. Actual bothOS CI/main artifact receipts remain acceptance evidence; a green editable run or example alone is insufficient. EQ095 independently qualifies the combined external experience before whole R3 acceptance.

EQ040 adds consumer0.3.0's [standalone installed workflows](../EXAMPLES.md): python -I -m equity_feature_demo.walkthrough covers batch/stream/history/composition/missingness plus existing custom/adapter integration. Consumer algorithmv2 and corepair0.0.4a4 are unchanged; independent implementation version and installed qualification advance.
