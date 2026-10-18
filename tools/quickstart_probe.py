"""Trusted EQ132 qualification, outside all installed calculation packages."""
from pathlib import Path
import hashlib
import importlib.metadata as metadata
import importlib.util
import json
import platform
import re
import struct
import sys
from dataclasses import asdict, replace
from enum import Enum
import csv
import io
import base64
import os
import stat
from urllib.parse import urlparse, unquote


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      default=lambda x: x.value if isinstance(x, Enum) else unsupported(x))


def unsupported(value):
    raise TypeError(type(value).__name__)


def checked_origin(origin, prefix):
    path = Path(origin).resolve()
    require(path.is_file() and path.is_relative_to(prefix), "source fallback or missing installed module")
    return path.relative_to(prefix).as_posix()


def unique_distributions(distributions):
    normalize = lambda s: re.sub(r"[-_.]+", "-", s).lower()
    pairs = [(normalize(x.metadata["Name"]), x.version) for x in distributions]
    require(len({name for name, _ in pairs}) == len(pairs), "duplicate normalized distribution")
    return dict(pairs)


def complete_site_inventory(distributions, prefix):
    """Close the on-disk site tree against every owner, including pip bootstrap."""
    prefix = Path(prefix).resolve()
    roots = {Path(dist.locate_file("")).resolve() for dist in distributions}
    require(len(roots) == 1, "multiple distribution roots refused")
    site = next(iter(roots))
    require(site.is_relative_to(prefix), "site root outside prefix")
    owners = {}
    bootstrap = {}
    for dist in distributions:
        require(dist.files is not None, "distribution has no RECORD inventory")
        for relative in dist.files:
            candidate = Path(dist.locate_file(relative))
            require(not candidate.is_symlink() and not (hasattr(candidate, "is_junction") and candidate.is_junction()),
                    "linked installed file refused")
            path = candidate.resolve()
            require(path.is_relative_to(prefix) and path.is_file() and stat.S_ISREG(path.stat().st_mode),
                    "non-regular or escaped installed file")
            require(path not in owners, "overlapping distribution file ownership")
            owners[path] = dist.metadata["Name"]
            if re.sub(r"[-_.]+", "-", dist.metadata["Name"]).lower() == "pip":
                raw = path.read_bytes()
                bootstrap[path.relative_to(prefix).as_posix()] = {"sha256": sha(raw), "bytes": len(raw)}
    actual = {}
    def walk_error(error):
        raise error
    for directory, directories, filenames in os.walk(site, followlinks=False, onerror=walk_error):
        for name in directories + filenames:
            path = Path(directory) / name
            require(not path.is_symlink() and not (hasattr(path, "is_junction") and path.is_junction()),
                    "linked site-tree entry refused")
            require(stat.S_ISDIR(path.stat().st_mode) if name in directories else stat.S_ISREG(path.stat().st_mode),
                    "non-regular site-tree entry refused")
        for name in filenames:
            path = (Path(directory) / name).resolve()
            raw = path.read_bytes()
            actual[path] = {"sha256": sha(raw), "bytes": len(raw)}
    require(set(actual) == {path for path in owners if path.is_relative_to(site)},
            "unrecorded or missing on-disk site file")
    return {"site_root": site.relative_to(prefix).as_posix(),
            "site_files": {p.relative_to(site).as_posix(): value for p, value in sorted(actual.items())},
            "bootstrap_files": bootstrap, "complete_record_ownership": True}


def validate_direct_url(direct, wheel_hash, wheel_path):
    require(type(direct) is dict and set(direct) == {"archive_info", "url"},
            "unexpected installer-origin fields")
    archive = direct["archive_info"]
    require(type(archive) is dict and set(archive) in ({"hashes"}, {"hashes", "hash"})
            and archive["hashes"] == {"sha256": wheel_hash}
            and ("hash" not in archive or archive["hash"] == "sha256=" + wheel_hash),
            "installer archive digest fields drift")
    require(type(direct["url"]) is str, "installer URL must be text")
    url = urlparse(direct["url"])
    require(url.scheme == "file" and not any((url.netloc, url.query, url.fragment, url.params)),
            "unexpected installer URL components")
    origin = unquote(url.path)
    if platform.system() == "Windows" and origin.startswith("/"):
        origin = origin[1:]
    require(Path(origin).resolve() == wheel_path, "installed origin is not selected local wheel")


def installed_inventory(inputs, phase):
    require(sys.implementation.name == "cpython" and sys.version_info[:2] == (3, 12)
            and struct.calcsize("P") == 8 and platform.machine().casefold() in ("amd64", "x86_64")
            and sys.prefix != sys.base_prefix,
            "fresh CPython 3.12 x64 venv required")
    prefix = Path(sys.prefix).resolve()
    config = (prefix / "pyvenv.cfg").read_text(encoding="utf-8").lower()
    require("include-system-site-packages = false" in config, "system site packages refused")
    normalize = lambda s: re.sub(r"[-_.]+", "-", s).lower()
    distributions = list(metadata.distributions())
    names = unique_distributions(distributions)
    expected = {"equity-feature-contracts": "0.0.4a4", "equity-features": "0.0.4a4"}
    if phase == "full":
        expected["equity-feature-demo"] = "0.4.0"
    require(set(names) == set(expected) | {"pip"}, "unexpected installed distribution")
    require(all(names[k] == v for k, v in expected.items()), "installed version drift")
    for forbidden in ("numpy", "pyarrow", "equity_feature_io", "equity_feature_workers"):
        require(importlib.util.find_spec(forbidden) is None, "unexpected runtime: " + forbidden)
    site_closure = complete_site_inventory(distributions, prefix)
    artifact = next(a for a in inputs["artifacts"] if a["manifest"]["system"] == platform.system())
    inventory = {}
    for wheel_name, wheel in artifact["selected_wheels"].items():
        name = normalize(wheel["metadata"]["name"])
        if name not in expected:
            continue
        dist = metadata.distribution(name)
        root = Path(dist.locate_file("")).resolve()
        require(root.is_relative_to(prefix), "distribution outside owned prefix")
        files = {}
        for relative in dist.files:
            path = Path(dist.locate_file(relative)).resolve()
            require(path.is_relative_to(prefix) and path.is_file(), "installed path escaped prefix")
            raw = path.read_bytes()
            files[str(relative).replace("\\", "/")] = {"sha256": sha(raw), "bytes": len(raw)}
        entry_map = wheel["entries"]
        record = next(p for p in entry_map if p.endswith(".dist-info/RECORD"))
        for path, expected_file in entry_map.items():
            if path != record:
                require(files.get(path) == expected_file, "installed wheel payload drift: " + path)
        extra = set(files) - set(entry_map)
        info = record.rsplit("/", 1)[0]
        require(extra == {info + "/INSTALLER", info + "/REQUESTED", info + "/direct_url.json"},
                "unexpected generated installed file")
        rows = list(csv.reader(io.StringIO(Path(dist.locate_file(record)).read_text(encoding="utf-8"))))
        require(len(rows) == len(files) and {row[0] for row in rows} == set(files),
                "installed RECORD names drift")
        for path, digest, size in rows:
            if path == record:
                require(digest == size == "", "installed RECORD self entry drift")
            else:
                actual = Path(dist.locate_file(path)).read_bytes()
                encoded = base64.urlsafe_b64encode(hashlib.sha256(actual).digest()).decode().rstrip("=")
                require(digest == "sha256=" + encoded and size == str(len(actual)),
                        "installed RECORD digest drift")
        require(Path(dist.locate_file(info + "/INSTALLER")).read_bytes() == b"pip\n"
                and Path(dist.locate_file(info + "/REQUESTED")).read_bytes() == b"",
                "installer metadata drift")
        direct = json.loads(Path(dist.locate_file(info + "/direct_url.json")).read_bytes())
        validate_direct_url(direct, wheel["sha256"], prefix.parent / "wheelhouse" / wheel_name)
        module = wheel_name.split("-")[0]
        spec = importlib.util.find_spec(module)
        require(spec is not None, "installed module missing: " + module)
        origin = checked_origin(spec.origin, prefix)
        inventory[name] = {"version": dist.version, "module_origin":
                           origin, "files": files}
    core = {k: v for k, v in inventory.items() if k != "equity-feature-demo"}
    return {"system": platform.system(), "python": platform.python_version(),
            "bits": struct.calcsize("P") * 8, "machine": platform.machine(), "installed_versions": names,
            "prefix_isolated": True, "forbidden_dependencies_absent": True,
            "distributions": inventory, "site_closure": site_closure, "core": core,
            "core_sha256": sha(canonical(core).encode())}


def independent_results(inputs):
    from equity_feature_contracts import (
        AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, CompositionSpec,
        ConfigSpec, Coverage, DataKind, EntityKey, FamilyResult, FeatureColumn,
        FeatureResult, HistoryContext, InputBinding, InputScope, Parameter,
        PrefixCoverage, PriceUnit, QualityRow, Reason, ResultMetadata,
        ReturnReference, SessionSpec, SourceBinding, Status, StreamPopulation,
        ValueType, WindowSpec, builtin_registry,
    )
    from equity_features.session import compute_bars
    from equity_features.incremental import SessionAccumulator
    from equity_features.history import compute_history
    from equity_features.composition import compose_features
    from equity_features.custom import CustomInput, CustomRegistry, CustomRequest
    from equity_feature_demo import FEATURE_ID, fixture, definition, calculate
    from equity_feature_demo.adapter import adapter_fixture, NeverCancelled
    from equity_feature_contracts.adapter_kit import ConformanceCase, run_conformance

    expected = inputs["independent_expected"]
    request = fixture()
    before = canonical(asdict(request))
    batch = request.inputs[0].batch
    columns = {x.name: x.values for x in batch.columns}
    require(columns == {"instrument_id": ("A", "A"), "session_id": ("S", "S"),
        "start_ns": (100, 150), "end_ns": (150, 200), "known_at_ns": (150, 210),
        "open": (100, 102), "high": (103, 104), "low": (99, 101), "close": (102, 103),
        "volume": (200, 300), "actual_notional": (20300, 30900)}, "fixture literal drift")
    require(batch.metadata == BatchMetadata("demo", SourceBinding("synthetic", "snapshot1", "map1", "bars1"),
        Coverage(2, 2, True), PriceUnit(0, "USD"), scope=InputScope(100, 200, "example-v1")),
        "whole supplied metadata drift")
    require(request.config == ConfigSpec(FEATURE_ID, "v2", (Parameter("eligibility_policy", "example-v1"),),
        SessionSpec("demo", "S", 100, 200, "caller-supplied"), WindowSpec(1, "S", ("P", "S")),
        AvailabilitySpec(200, 210, 210), price_unit=PriceUnit(0, "USD")), "whole configuration drift")
    require(request.entity == EntityKey("A", "S"), "entity drift")
    config = replace(request.config, identity="walkthrough-bars", algorithm_version="v1")
    result = compute_bars(batch, config, entity=request.entity)
    registry = builtin_registry()
    def expected_columns(values):
        return tuple(FeatureColumn(k, "v1", ValueType(registry.get(k).outputs[0].dtype),
            registry.get(k).outputs[0].unit, (request.entity,), (v,)) for k, v in values.items())
    qualities = tuple(QualityRow(request.entity, k,
        Status.MISSING_INPUT if v is None else Status.AVAILABLE, 2, 2,
        (Reason.ABSENT_INPUT,) if v is None else ()) for k, v in expected["batch_values"].items())
    whole_metadata = ResultMetadata("demo", "S", AvailabilitySpec(200, 210, 210), config.digest,
        (InputBinding("bars", DataKind.BAR, batch.metadata),), "python-exact", "0.0.4a4")
    golden = FeatureResult(expected_columns(expected["batch_values"]), qualities, whole_metadata)
    require(result == golden, "full independent twelve-value/quality/metadata golden mismatch")
    absent = compute_bars(None, config, entity=request.entity)
    absent_golden = FeatureResult(expected_columns(dict.fromkeys(expected["batch_values"])),
        tuple(QualityRow(request.entity, k, Status.MISSING_INPUT, None, 0, (Reason.ABSENT_INPUT,))
              for k in expected["batch_values"]), replace(whole_metadata, inputs=()))
    require(absent == absent_golden, "full absent-bars golden mismatch")
    def chunk(i):
        return replace(batch, columns=tuple(Column(x.name, (x.values[i],)) for x in batch.columns),
                       metadata=replace(batch.metadata, coverage=Coverage(1, 1, True)))
    stream = SessionAccumulator("bars", config, entity=request.entity,
                                population=StreamPopulation.from_batch(batch))
    stream.update(chunk(0), start_ordinal=0)
    prefix = stream.snapshot(PrefixCoverage(150, Coverage(1, 1, True)))
    prefix_snapshot = canonical(asdict(prefix))
    require(next(x.values[0] for x in prefix.values if x.feature_id == "session.bar.close") == 102.0
            and prefix.metadata.availability.market_cutoff_ns == 150, "prefix literal mismatch")
    stream.update(chunk(1), start_ordinal=1)
    final = stream.finalize(PrefixCoverage(200, Coverage(2, 2, True)))
    require(final.values == golden.values and final.quality == golden.quality
            and final.metadata.availability.market_cutoff_ns == 200
            and canonical(asdict(prefix)) == prefix_snapshot, "stream final/prefix preservation mismatch")

    sessions = tuple(SessionSpec("demo", "S" + str(i), 10*i+1, 10*i+10, "supplied") for i in range(3))
    context = HistoryContext(EntityKey("A", "S2"), "walkthrough-grid-v1", sessions, (Coverage(1, 1, True),)*3)
    timing = AvailabilitySpec(30, 35, 35)
    daily = CanonicalBatch(DataKind.DAILY, tuple(Column(k, v) for k, v in (
        ("instrument_id", ("A",)*3), ("session_id", ("S0", "S1", "S2")),
        ("start_ns", (1, 11, 21)), ("end_ns", (10, 20, 30)),
        ("close", (100, 110, 121)), ("known_at_ns", (10, 20, 30)))),
        BatchMetadata("demo", SourceBinding("synthetic", "history1", "map1", "daily-A"),
                      Coverage(3, 3, True), PriceUnit(0, "USD")))
    history = []
    families = []
    for period, literal in ((1, 0.1), (2, 0.21)):
        cfg = ConfigSpec("walkthrough-h" + str(period), "v1", (Parameter("period", period),),
            sessions[-1], WindowSpec(period+1, "S2", ("S0", "S1", "S2"), "completed_eod"),
            timing, price_unit=PriceUnit(0, "USD"))
        answer = compute_history(daily, cfg, context=context, feature_ids=("history.return",))
        missing = compute_history(None, cfg, context=context, feature_ids=("history.return",))
        require(len(answer.values) == len(answer.quality) == 1 and answer.values[0].values == (literal,)
                and answer.quality[0].status == Status.AVAILABLE, "history hand golden mismatch")
        require(missing.values[0].values == (None,) and missing.quality[0].status == Status.MISSING_INPUT,
                "history absence must remain explicit")
        families.append(FamilyResult("h" + str(period), answer, cfg, companion=ReturnReference(answer, cfg, context)))
        history.append({"config": asdict(cfg), "result": asdict(answer), "absent": asdict(missing)})
    composed = compose_features(tuple(families), spec=CompositionSpec("demo", sessions[-1], timing,
                                ("h2", "missing", "h1")))
    require(composed.components == (families[1], families[0]) and composed.missing_instances == ("missing",)
            and composed.components[0].result is families[1].result, "whole composition preservation mismatch")
    custom = CustomRegistry("demo").register(definition(), calculate).compute(FEATURE_ID, request)
    require(custom.values[0].values == (0.05,), "independent custom5/100 mismatch")
    adapter, acquisition = adapter_fixture()
    deliveries = tuple(adapter.iter_batches(acquisition, NeverCancelled()))
    conformance = run_conformance((ConformanceCase("quickstart-installed-adapter", acquisition,
                                                 adapter.capabilities(), deliveries),))
    require(conformance.passed and len(deliveries) == 1, "public adapter conformance mismatch")
    adapted = CustomRegistry("demo").register(definition(), calculate).compute(FEATURE_ID,
        CustomRequest((CustomInput("bars", deliveries[0].batch),), request.config, request.entity))
    require(adapted.values[0].values == (0.05,)
            and adapted.metadata.inputs[0].metadata.source == deliveries[0].source,
            "adapted source/custom binding mismatch")
    require(canonical(asdict(request)) == before, "input/config mutation")
    return {"schema": "eq132.independent-results.v1", "supplied_request": asdict(request),
        "batch_config": asdict(config), "batch": asdict(result), "absent_bars": asdict(absent),
        "prefix": asdict(prefix), "stream_final": asdict(final), "daily_input": asdict(daily),
        "history_context": asdict(context), "history": history, "composition": asdict(composed),
        "custom": asdict(custom), "acquisition": asdict(acquisition),
        "adapter_deliveries": [asdict(x) for x in deliveries], "adapter_conformance": asdict(conformance),
        "adapted_result": asdict(adapted),
        "input_config_unchanged": True, "full_batch_absence_golden": True}


def main():
    require(len(sys.argv) == 3 and sys.argv[1] in ("core", "full", "results"), "fixed probe arguments required")
    require(sys.flags.isolated == 1 and sys.flags.optimize == 0, "isolated assertions-enabled execution required")
    inputs = json.loads(Path(sys.argv[2]).read_bytes())
    value = independent_results(inputs) if sys.argv[1] == "results" else installed_inventory(inputs, sys.argv[1])
    print(canonical(value))


if __name__ == "__main__":
    main()
