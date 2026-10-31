"""Single source of the experimental package versions for this repository's tools, tests and examples.

A pre-release bump edits this table, the matching ``pyproject.toml`` files, the ``__version__`` of contracts and
features, and the one expected-contracts constant inside each of evidence, labels and strategies (installed packages
cannot import this file). ``tools/verify_versions.py`` fails if any of those places disagree. Historical receipts,
release records and frozen archive baselines intentionally keep the versions they were produced with.
"""
from __future__ import annotations

VERSIONS: dict[str, str] = {
    "contracts": "0.0.4a6",
    "features": "0.0.4a7",
    "evidence": "0.1.0a4",
    "explanations": "0.1.0a4",
    "diagnostics": "0.1.0a3",
    "agent-evidence": "0.1.0a3",
    "agent-ledger": "0.1.0a3",
    "conformance": "0.1.0a3",
    "continuous": "0.1.0a2",
    "intraday": "0.1.0a5",
    "labels": "0.1.0a1",
    "strategies": "0.1.0a1",
}
CONTRACTS = VERSIONS["contracts"]
FEATURES = VERSIONS["features"]
# Producer versions the explanations package admits: the current features version and the earlier ones it still admits.
EXPLANATION_BACKEND_VERSIONS = ("0.0.4a4", "0.0.4a5", "0.0.4a6", FEATURES)

# Sibling-repository distributions the multi-repository builders (build_conformance, build_r10, build_r9, build_evidence_pilot) build.
SIBLINGS: dict[str, str] = {
    "io-contracts": "0.1.0a3",
    "io-sdk": "0.1.0a3",
    "duckdb": "0.1.0a11",
    "duckdb-sink": "0.1.0a1",
    "bundles": "0.1.0a2",
    "workers": "0.1.0a17",
}
# Exact sibling commits those builders read: the io post-bump main commit 94217cf and the workers main commit 474f79d (workers #112 re-pin).
SIBLING_COMMITS: dict[str, str] = {
    "io": "94217cfafe5e54461c8dc9efdf4848809e04082a",
    "workers": "474f79d380d45d907a172a7ffc93319eae0e5139",
}
