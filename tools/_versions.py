"""Single source of the experimental package versions for this repository's tools, tests and examples.

A pre-release bump edits this table, the matching ``pyproject.toml`` files, the ``__version__`` of contracts and
features, and the one expected-contracts constant inside each of evidence, labels and strategies (installed packages
cannot import this file). ``tools/verify_versions.py`` fails if any of those places disagree. Historical receipts,
release records and frozen archive baselines intentionally keep the versions they were produced with.
"""
from __future__ import annotations

VERSIONS: dict[str, str] = {
    "contracts": "0.0.4a5",
    "features": "0.0.4a6",
    "evidence": "0.1.0a3",
    "explanations": "0.1.0a3",
    "diagnostics": "0.1.0a2",
    "agent-evidence": "0.1.0a2",
    "agent-ledger": "0.1.0a2",
    "conformance": "0.1.0a2",
    "continuous": "0.1.0a2",
    "intraday": "0.1.0a4",
    "labels": "0.1.0a1",
    "strategies": "0.1.0a1",
}
CONTRACTS = VERSIONS["contracts"]
FEATURES = VERSIONS["features"]
# Producer versions the explanations package admits: the current features version and the earlier ones it still admits.
EXPLANATION_BACKEND_VERSIONS = ("0.0.4a4", "0.0.4a5", FEATURES)
