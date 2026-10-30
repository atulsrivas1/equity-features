"""Pure DV1 log-return beta and correlation (dv1-rlog1): one instrument against one benchmark.

x_j = ln(Ci_j / Ci_(j-1)) and y_j = ln(Cb_j / Cb_(j-1)) of two close-only BAR roles aligned by governed session id;
every logarithm is a Decimal120 evaluation of the exact close ratio (same primitive as `ef3-dlv1`), the sums are
two-pass in Decimal120 and each published value is one correctly rounded float64. Zero variances are decided by exact
integer comparison of the close ratios (the logarithm is injective), never by a Decimal variance. No clock, I/O,
storage, default window or benchmark. The simple-return variants `relative.beta` and `relative.correlation` (ef3-rel1)
are a different convention and are untouched. Internal, synthetic, pre-release.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Context, Decimal, DecimalException, localcontext, MAX_EMAX, MIN_EMIN, ROUND_HALF_EVEN
from math import isfinite

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, CanonicalBatch, ConfigSpec, EntityKey, ErrorCode, EvidenceRow, FeatureColumn,
    FeatureResult, Parameter, PriceUnit, QualityRow, Reason, ResultMetadata, Status, ValueType, WindowSpec,
    require_compatible_inputs,
)
from equity_features import __version__
from ._config_check import check_coverage_declared, check_tail, check_units
from ._status import status_of
from equity_features.ef3._common import (
    CloseFact, DailyGrid, admit_role, fail, grid_parameters, integer, label, parameter_map, slot_reasons,
)

RLOG_IDENTITY = "dv1.relative_log_stats"
RLOG_ALGORITHM = "dv1-relative-log-stats-v1"
# The label names the whole convention set (natural-log close-ratio returns, complete-case joint pairs, centred sums,
# exact ratio zero tests, Decimal120 arithmetic, one float64 rounding, no log residual).
RLOG_POLICY = "dv1-rlog1"
LOG_BETA = "relative.log_return_beta"
LOG_CORRELATION = "relative.log_return_correlation"
RLOG_FEATURES = (LOG_BETA, LOG_CORRELATION)
_KEYS = frozenset({"policy_version", "benchmark_id", "window", "min_pairs", "evidence_limit"})


@dataclass(frozen=True)
class RelativeLogSettings:
    policy_version: str
    benchmark_id: str
    window: int
    min_pairs: int
    evidence_limit: int


def _check(policy: object, benchmark: object, window: object, min_pairs: object, limit: object) -> RelativeLogSettings:
    """Config-stage checks of the parameters (types, bounds, no default); the policy label is the version stage."""
    if type(policy) is not str:
        fail(ErrorCode.INVALID_CONFIG, "exact relative-log policy label required")
    benchmark_id = label(benchmark)
    width = integer(window, 2, 4096)
    minimum = integer(min_pairs, 2, width)
    return RelativeLogSettings(policy, benchmark_id, width, minimum, integer(limit, 0, 10000))


def build_relative_log_config(grid: DailyGrid, *, policy_version: str | None = None, benchmark_id: str | None = None,
                              window: int | None = None, min_pairs: int | None = None,
                              availability: AvailabilitySpec, adjustment: AdjustmentSpec, price_unit: PriceUnit,
                              evidence_limit: int | None = None) -> ConfigSpec:
    """Final ConfigSpec for one instrument and exactly one benchmark; every parameter is explicit with no default
    (an omitted evidence_limit is INVALID_CONFIG). Refusal stages in the contract's order: config, version, identity."""
    if type(grid) is not DailyGrid:
        fail(ErrorCode.INVALID_CONFIG, "concrete daily grid required")
    settings = _check(policy_version, benchmark_id, window, min_pairs, evidence_limit)
    availability, adjustment, price_unit = check_units(availability, adjustment, price_unit)
    check_tail(grid, availability, adjustment, price_unit, settings.policy_version, RLOG_POLICY,
               "unsupported relative-log policy label")
    if settings.benchmark_id == grid.instrument_id:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "the benchmark must differ from the instrument (no self-pair)")
    target = grid.target
    params = (Parameter("policy_version", settings.policy_version), Parameter("benchmark_id", settings.benchmark_id),
              Parameter("window", settings.window), Parameter("min_pairs", settings.min_pairs),
              Parameter("evidence_limit", settings.evidence_limit))
    return ConfigSpec(RLOG_IDENTITY, RLOG_ALGORITHM, params + grid_parameters(grid), target,
                      WindowSpec(len(grid.sessions), target.session_id, tuple(s.session_id for s in grid.sessions),
                                 "completed_eod"),
                      availability, adjustment, price_unit)


def decode_relative_log_config(grid: DailyGrid, config: ConfigSpec) -> RelativeLogSettings:
    """Validate the closed relative-log envelope against the supplied grid and return its settings."""
    values = parameter_map(config, RLOG_IDENTITY, RLOG_ALGORITHM, _KEYS, grid)
    settings = _check(values["policy_version"], values["benchmark_id"], values["window"], values["min_pairs"],
                      values["evidence_limit"])
    assert config.price_unit is not None
    expected = build_relative_log_config(
        grid, policy_version=settings.policy_version, benchmark_id=settings.benchmark_id, window=settings.window,
        min_pairs=settings.min_pairs, availability=config.availability, adjustment=config.adjustment,
        price_unit=config.price_unit, evidence_limit=settings.evidence_limit)
    if config != expected:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "configuration is not the final canonical relative-log envelope")
    return settings


def _to_float(value: Decimal) -> float:
    """One correctly rounded binary64 of a Decimal120 value; an exact zero is the positive zero."""
    converted = float(value)
    if not isfinite(converted):
        fail(ErrorCode.OVERFLOW, "relative log statistic outside binary64")
    return 0.0 if converted == 0.0 else converted


def log_statistics(inst: list[tuple[int, int]], bench: list[tuple[int, int]],
                   selected: tuple[str, ...]) -> dict[str, float | None]:
    """Selected log statistics of n joint pairs of (close, prior close); None marks zero_denominator.

    Zero variance is decided by exact cross-multiplied ratio equality: the benchmark ratios all equal gives None for
    both outputs; the instrument ratios all equal gives beta exactly +0.0 and no correlation.
    """
    n = len(inst)
    y_flat = all(bench[i][0] * bench[0][1] == bench[0][0] * bench[i][1] for i in range(1, n))
    x_flat = all(inst[i][0] * inst[0][1] == inst[0][0] * inst[i][1] for i in range(1, n))
    out: dict[str, float | None] = {feature: None for feature in selected}
    if y_flat:
        return out
    if x_flat:
        if LOG_BETA in out:
            out[LOG_BETA] = 0.0
        return out
    context = Context(prec=120, rounding=ROUND_HALF_EVEN, Emin=MIN_EMIN, Emax=MAX_EMAX)
    try:
        with localcontext(context):
            xs = [(Decimal(c) / Decimal(p)).ln() for c, p in inst]
            ys = [(Decimal(c) / Decimal(p)).ln() for c, p in bench]
            mean_x = sum(xs, Decimal(0)) / n
            mean_y = sum(ys, Decimal(0)) / n
            dx = [value - mean_x for value in xs]
            dy = [value - mean_y for value in ys]
            sxy = sum((a * b for a, b in zip(dx, dy)), Decimal(0))
            syy = sum((b * b for b in dy), Decimal(0))
            if LOG_BETA in out:
                out[LOG_BETA] = _to_float(sxy / syy)
            if LOG_CORRELATION in out:
                sxx = sum((a * a for a in dx), Decimal(0))
                out[LOG_CORRELATION] = _to_float(sxy / (sxx * syy).sqrt())
    except (DecimalException, OverflowError, ValueError):
        fail(ErrorCode.OVERFLOW, "relative log statistic arithmetic outside declared numeric policy")
    return out


def _causes(fact: CloseFact, market_cutoff_ns: int, knowledge_cutoff_ns: int) -> frozenset[Reason]:
    """A slot that ends after the market cutoff is still forming (future_market); otherwise the shared slot causes."""
    if fact.slot.end_ns > market_cutoff_ns:
        return frozenset({Reason.FUTURE_MARKET})
    return slot_reasons(fact, knowledge_cutoff_ns)


def compute_relative_log(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None],
                         grid: DailyGrid, config: ConfigSpec, *, features: tuple[str, ...]) -> FeatureResult:
    """Selected dv1-rlog1 outputs; `batches` is the fixed pair (instrument, benchmark), each nullable."""
    settings = decode_relative_log_config(grid, config)
    if (type(features) is not tuple or not 1 <= len(features) <= len(RLOG_FEATURES)
            or any(type(feature) is not str for feature in features) or len(set(features)) != len(features)):
        fail(ErrorCode.INVALID_SCHEMA, "nonempty unique selected feature IDs required")
    if any(feature not in RLOG_FEATURES for feature in features):
        fail(ErrorCode.UNKNOWN_FEATURE, "unknown selected relative-log feature")
    selected = tuple(sorted(features))
    if type(batches) not in (tuple, list):
        fail(ErrorCode.INVALID_SCHEMA, "the fixed roles (instrument, benchmark) are required")
    if len(batches) > 2:
        fail(ErrorCode.INVALID_CONFIG, "exactly one benchmark: the producer joins only the requested pair")
    if len(batches) != 2:
        fail(ErrorCode.INVALID_SCHEMA, "the fixed roles (instrument, benchmark) are required")
    inst_batch, bench_batch = batches
    present = [batch for batch in batches if batch is not None]
    if inst_batch is not None and bench_batch is not None:
        if type(inst_batch) is not CanonicalBatch or type(bench_batch) is not CanonicalBatch:
            fail(ErrorCode.INVALID_SCHEMA, "concrete canonical batches required")
        require_compatible_inputs(inst_batch, bench_batch)
        if inst_batch.metadata.source.input_id == bench_batch.metadata.source.input_id:
            fail(ErrorCode.DUPLICATE, "distinct actual role input IDs required")
    check_coverage_declared(inst_batch)
    check_coverage_declared(bench_batch)
    inst = admit_role("instrument", inst_batch, grid.instrument_id, grid, config)
    bench = admit_role("benchmark", bench_batch, settings.benchmark_id, grid, config)
    t = grid.target_index
    window, minimum = settings.window, settings.min_pairs
    entity = EntityKey(grid.instrument_id, config.session.session_id)
    cutoff = config.availability.knowledge_cutoff_ns
    market = config.availability.market_cutoff_ns
    lo = max(t - window, 0)
    in_grid = t - window >= 0
    reasons_base: set[Reason] = set()
    valid: list[int] = []
    if len(present) < 2:
        reasons_base.add(Reason.ABSENT_INPUT)
    else:
        causes: dict[int, frozenset[Reason]] = {}
        for s in range(lo, t + 1):
            causes[s] = _causes(inst.facts[s], market, cutoff) | _causes(bench.facts[s], market, cutoff)
            reasons_base.update(causes[s])
        valid = [j for j in range(lo + 1, t + 1) if not causes[j - 1] and not causes[j]]
        if not in_grid:
            reasons_base.add(Reason.INSUFFICIENT_HISTORY)
    n = len(valid)
    values: dict[str, float | None] = {feature: None for feature in selected}
    reasons: dict[str, set[Reason]] = {feature: set(reasons_base) for feature in selected}
    if len(present) == 2 and in_grid and n >= minimum:
        pairs_i: list[tuple[int, int]] = []
        pairs_b: list[tuple[int, int]] = []
        for j in valid:
            ci, pi = inst.facts[j].close, inst.facts[j - 1].close
            cb, pb = bench.facts[j].close, bench.facts[j - 1].close
            assert ci is not None and pi is not None and cb is not None and pb is not None
            pairs_i.append((ci, pi))
            pairs_b.append((cb, pb))
        values = log_statistics(pairs_i, pairs_b, selected)
        for feature in selected:
            if values[feature] is None:
                reasons[feature].add(Reason.ZERO_DENOMINATOR)
    columns: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    used = sorted({k for j in valid for k in (j - 1, j)})
    order = ([t] if t in used else []) + [k for k in used if k != t]
    for feature in selected:
        status = Status.AVAILABLE if values[feature] is not None else status_of(reasons[feature])
        count = window
        if values[feature] is not None:
            # An available row publishes expected = observed = n used pairs; lost-pair causes stay as reasons.
            count = n
            for s_ in order:
                for facts in (inst.facts, bench.facts):
                    fact = facts[s_]
                    if fact.row_index is None or fact.input_id is None or len(evidence) >= settings.evidence_limit:
                        continue
                    evidence.append(EvidenceRow(entity, feature, fact.input_id, f"slot:{s_}", fact.slot.end_ns,
                        fact.known_at_ns, fact.slot.start_ns, fact.slot.end_ns, "consumed", None,
                        "completed_interval"))
        ordered = tuple(sorted(reasons[feature], key=lambda reason: reason.value))
        columns.append(FeatureColumn(feature, RLOG_ALGORITHM, ValueType.FLOAT64, "fraction", (entity,),
                                     (values[feature],)))
        quality.append(QualityRow(entity, feature, status, count, n, ordered))
    bindings = tuple(b for b in (inst.binding, bench.binding) if b is not None)
    metadata = ResultMetadata(config.session.namespace, config.session.session_id, config.availability,
                              config.digest, bindings, "python-exact", __version__, settings.evidence_limit)
    return FeatureResult(tuple(columns), tuple(quality), metadata, tuple(evidence))
