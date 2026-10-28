"""Check that every live place that carries a package version agrees with tools/_versions.py (static, source based).

Covers: each package's pyproject version and its exact dependency pins, the in-source version constants of contracts,
features, intraday and explanations, the expected-contracts constant of evidence/labels/strategies, the admitted producer
versions of explanations, and the external consumer example pins. Historical receipts are deliberately not checked.
"""
from __future__ import annotations

import ast
import re
import tomllib
from pathlib import Path

from _versions import CONTRACTS, EXPLANATION_BACKEND_VERSIONS, FEATURES, VERSIONS

ROOT = Path(__file__).resolve().parents[1]
DIST = {f"equity-feature-{k}": k for k in VERSIONS if k not in ("features", "intraday")}
DIST.update({"equity-features": "features", "equity-features-intraday": "intraday"})
errors: list[str] = []


def expect(label: str, actual: object, wanted: object) -> None:
    if actual != wanted:
        errors.append(f"{label}: {actual!r} != {wanted!r}")


def pins(requirement: str) -> tuple[str, str] | None:
    m = re.fullmatch(r"([A-Za-z0-9_.-]+)(?:\[[a-z]+\])?==([0-9][^;\s]*)", requirement)
    return (m.group(1), m.group(2)) if m else None


def check_requirements(label: str, requirements: list[str]) -> None:
    for requirement in requirements:
        parsed = pins(requirement)
        if parsed and parsed[0] in DIST:
            expect(f"{label} pin {parsed[0]}", parsed[1], VERSIONS[DIST[parsed[0]]])


def constant(path: Path, name: str) -> str:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            value = ast.literal_eval(node.value) if isinstance(node.value, (ast.Constant, ast.Tuple)) else None
            if value is not None:
                return value  # type: ignore[no-any-return]
    errors.append(f"{path.relative_to(ROOT)}: {name} not found")
    return ""


for pyproject in sorted((ROOT / "packages").glob("*/pyproject.toml")):
    project = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]
    key = DIST[project["name"]]
    expect(f"{project['name']} version", project["version"], VERSIONS[key])
    check_requirements(project["name"], project.get("dependencies", []))
    for group in project.get("optional-dependencies", {}).values():
        check_requirements(project["name"], group)

pkg = ROOT / "packages"
# Every package that declares a literal __version__ must match its table entry.
for init in sorted(pkg.glob("*/src/*/__init__.py")):
    m = re.search(r"^__version__ = ['\"]([^'\"]+)['\"]", init.read_text(encoding="utf-8"), re.M)
    if m:
        expect(f"{init.relative_to(ROOT)} __version__", m.group(1), VERSIONS[init.parts[init.parts.index("packages") + 1]])
expect("contracts __version__", constant(pkg / "contracts/src/equity_feature_contracts/__init__.py", "__version__"), CONTRACTS)
expect("features __version__", constant(pkg / "features/src/equity_features/__init__.py", "__version__"), FEATURES)
expect("intraday PACKAGE_VERSION", constant(pkg / "intraday/src/equity_features_intraday/_registry.py", "PACKAGE_VERSION"), VERSIONS["intraday"])
expect("explanations __version__", constant(pkg / "explanations/src/equity_feature_explanations/__init__.py", "__version__"), VERSIONS["explanations"])
expect("explanations admitted backends", constant(pkg / "explanations/src/equity_feature_explanations/_explain.py", "_LEGACY_BACKEND_VERSIONS"),
       EXPLANATION_BACKEND_VERSIONS)
for path in ("evidence/src/equity_feature_evidence/_content.py", "labels/src/equity_feature_labels/_codec.py",
             "strategies/src/equity_feature_strategies/_codec.py"):
    expect(f"{path} _CONTRACTS_VERSION", constant(pkg / path, "_CONTRACTS_VERSION"), CONTRACTS)
consumer = tomllib.loads((ROOT / "examples/external_consumer/pyproject.toml").read_text(encoding="utf-8"))["project"]
check_requirements("examples/external_consumer", consumer["dependencies"])

if errors:
    raise SystemExit("version drift:\n" + "\n".join(errors))
print(f"Versions consistent across {len(list((pkg).glob('*/pyproject.toml')))} packages, in-source constants and example pins.")
