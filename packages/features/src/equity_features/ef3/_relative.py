"""Pure EF3 relative statistics (ef3-rel1): correlation, beta and residual return of one instrument against one benchmark.

Exact rational mathematics over the daily simple returns of two close-only BAR roles aligned by identical governed
session id; one correctly rounded float64 per published value (the correlation square root is evaluated in Decimal120
unless the exact rational is a perfect square). No clock, I/O, storage, default window or benchmark.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Context, Decimal, DecimalException, localcontext, MAX_EMAX, MIN_EMIN, ROUND_HALF_EVEN
from fractions import Fraction
from math import isqrt

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, CanonicalBatch, ConfigSpec, EntityKey, ErrorCode, EvidenceRow,
    FeatureColumn, FeatureResult, Parameter, PriceUnit, QualityRow, Reason, ResultMetadata, Status, ValueType,
    require_compatible_inputs,
)
from equity_features import __version__
from ._common import (
    PRECEDENCE, CloseFact, DailyGrid, admit_role, envelope, fail, first_status, integer, label, parameter_map,
    slot_reasons,
)

RELATIVE_IDENTITY = "ef3.relative_stats"
RELATIVE_ALGORITHM = "ef3-relative-stats-v1"
# The label names the whole convention set (simple session returns, complete-case joint pairs, centered OLS with
# the declared n-1 denominator that cancels, exact zero tests, same-window no-intercept residual).
RELATIVE_POLICY = "ef3-rel1"
BETA = "relative.beta"
CORRELATION = "relative.correlation"
RESIDUAL = "relative.residual_return"
RELATIVE_FEATURES = (BETA, CORRELATION, RESIDUAL)
ROLES = ("instrument", "benchmark")
_KEYS = frozenset({"policy_version", "benchmark_id", "window", "min_pairs", "evidence_limit"})


@dataclass(frozen=True)
class RelativeStatsSettings:
    policy_version: str
    benchmark_id: str
    window: int
    min_pairs: int
    evidence_limit: int


def _check(policy: object, benchmark: object, window: object, min_pairs: object, limit: object) -> RelativeStatsSettings:
    if type(policy) is not str:
        fail(ErrorCode.INVALID_CONFIG, "exact relative-statistics policy label required")
    if policy != RELATIVE_POLICY:
        fail(ErrorCode.INCOMPATIBLE_VERSION, "unsupported relative-statistics policy label")
    benchmark_id = label(benchmark)
    width = integer(window, 2, 4096)
    minimum = integer(min_pairs, 2, width)
    return RelativeStatsSettings(policy, benchmark_id, width, minimum, integer(limit, 0, 10000))


def build_relative_stats_config(grid: DailyGrid, *, policy_version: str | None = None, benchmark_id: str | None = None,
                                window: int | None = None, min_pairs: int | None = None,
                                availability: AvailabilitySpec, adjustment: AdjustmentSpec, price_unit: PriceUnit,
                                evidence_limit: int = 0) -> ConfigSpec:
    """Final ConfigSpec for one instrument and exactly one benchmark; every parameter is explicit with no default."""
    if type(grid) is not DailyGrid:
        fail(ErrorCode.INVALID_CONFIG, "concrete daily grid required")
    settings = _check(policy_version, benchmark_id, window, min_pairs, evidence_limit)
    if settings.benchmark_id == grid.instrument_id:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "the benchmark must differ from the instrument (no self-pair)")
    params = (Parameter("policy_version", settings.policy_version), Parameter("benchmark_id", settings.benchmark_id),
              Parameter("window", settings.window), Parameter("min_pairs", settings.min_pairs),
              Parameter("evidence_limit", settings.evidence_limit))
    return envelope(RELATIVE_IDENTITY, RELATIVE_ALGORITHM, params, grid, availability, adjustment, price_unit)


def decode_relative_stats_config(grid: DailyGrid, config: ConfigSpec) -> RelativeStatsSettings:
    """Validate the closed relative-statistics envelope against the supplied grid and return its settings."""
    values = parameter_map(config, RELATIVE_IDENTITY, RELATIVE_ALGORITHM, _KEYS, grid)
    settings = _check(values["policy_version"], values["benchmark_id"], values["window"], values["min_pairs"],
                      values["evidence_limit"])
    assert config.price_unit is not None
    expected = build_relative_stats_config(
        grid, policy_version=settings.policy_version, benchmark_id=settings.benchmark_id, window=settings.window,
        min_pairs=settings.min_pairs, availability=config.availability, adjustment=config.adjustment,
        price_unit=config.price_unit, evidence_limit=settings.evidence_limit)
    if config != expected:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "configuration is not the final canonical relative-statistics envelope")
    return settings


def _tree(terms: list[tuple[int, int]]) -> tuple[int, int]:
    """Exact sum of n/d terms as an unreduced (numerator, denominator) pair; pairwise, gcd-free."""
    work = list(terms)
    if not work:
        return 0, 1
    while len(work) > 1:
        merged = [(work[i][0]*work[i+1][1] + work[i+1][0]*work[i][1], work[i][1]*work[i+1][1])
                  for i in range(0, len(work)-1, 2)]
        if len(work) % 2:
            merged.append(work[-1])
        work = merged
    return work[0]


def _float(value: Fraction) -> float:
    """One correctly rounded binary64 of an exact rational; zero is the positive zero."""
    try:
        return float(value)
    except OverflowError:
        fail(ErrorCode.OVERFLOW, "relative statistic outside binary64")


def _correlation(cov: Fraction, var_b: Fraction, var_i: Fraction) -> float:
    """sign(cov) * sqrt(cov^2 / (var_b var_i)): exact when both reduced parts are squares, else Decimal120."""
    if cov == 0:
        return 0.0
    square = cov * cov / (var_b * var_i)
    num, den = square.numerator, square.denominator
    root_n, root_d = isqrt(num), isqrt(den)
    if root_n * root_n == num and root_d * root_d == den:
        magnitude = _float(Fraction(root_n, root_d))
    else:
        context = Context(prec=120, rounding=ROUND_HALF_EVEN, Emin=MIN_EMIN, Emax=MAX_EMAX)
        try:
            with localcontext(context):
                magnitude = float((Decimal(num) / Decimal(den)).sqrt())
        except (DecimalException, OverflowError, ValueError):
            fail(ErrorCode.OVERFLOW, "correlation arithmetic outside declared numeric policy")
    return -magnitude if cov < 0 else magnitude


def compute_relative_stats(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None],
                           grid: DailyGrid, config: ConfigSpec, *, features: tuple[str, ...]) -> FeatureResult:
    """Selected ef3-rel1 outputs; `batches` is the fixed pair (instrument, benchmark), each nullable."""
    settings = decode_relative_stats_config(grid, config)
    if (type(features) is not tuple or not 1 <= len(features) <= len(RELATIVE_FEATURES)
            or any(type(feature) is not str for feature in features) or len(set(features)) != len(features)):
        fail(ErrorCode.INVALID_SCHEMA, "nonempty unique selected feature IDs required")
    if any(feature not in RELATIVE_FEATURES for feature in features):
        fail(ErrorCode.UNKNOWN_FEATURE, "unknown selected relative-statistics feature")
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
    inst = admit_role("instrument", inst_batch, grid.instrument_id, grid, config)
    bench = admit_role("benchmark", bench_batch, settings.benchmark_id, grid, config)
    t = grid.target_index
    window, minimum = settings.window, settings.min_pairs
    entity = EntityKey(grid.instrument_id, config.session.session_id)
    cutoff = config.availability.knowledge_cutoff_ns
    lo = max(t - window, 0)
    in_grid = t - window >= 0
    reasons_base: set[Reason] = set()
    n = 0
    valid: list[int] = []
    if len(present) < 2:
        reasons_base.add(Reason.ABSENT_INPUT)
    else:
        causes: dict[int, frozenset[Reason]] = {}
        for s in range(lo, t + 1):
            causes[s] = slot_reasons(inst.facts[s], cutoff) | slot_reasons(bench.facts[s], cutoff)
            reasons_base.update(causes[s])
        valid = [j for j in range(lo + 1, t + 1) if not causes[j - 1] and not causes[j]]
        n = len(valid)
        if not in_grid:
            reasons_base.add(Reason.INSUFFICIENT_HISTORY)
    computable = len(present) == 2 and in_grid and n >= minimum
    values: dict[str, float | None] = {feature: None for feature in selected}
    reasons: dict[str, set[Reason]] = {feature: set(reasons_base) for feature in selected}
    if computable:
        for feature in selected:
            reasons[feature] = set()
        # Returns r_j = (C_j - C_{j-1}) / C_{j-1} as exact numerator/denominator pairs.
        xs, ys = [], []
        for j in valid:
            ci, pi = inst.facts[j].close, inst.facts[j - 1].close
            cb, pb = bench.facts[j].close, bench.facts[j - 1].close
            assert ci is not None and pi is not None and cb is not None and pb is not None
            xs.append((ci - pi, pi))
            ys.append((cb - pb, pb))
        sx, sy = Fraction(*_tree(xs)), Fraction(*_tree(ys))
        sxx = Fraction(*_tree([(a*a, b*b) for a, b in xs]))
        syy = Fraction(*_tree([(a*a, b*b) for a, b in ys]))
        sxy = Fraction(*_tree([(a[0]*b[0], a[1]*b[1]) for a, b in zip(xs, ys)]))
        # n times the centered sums (the n-1 versus n denominator cancels in every published ratio).
        cov = n*sxy - sx*sy
        var_b = n*syy - sy*sy
        var_i = n*sxx - sx*sx
        if var_b == 0:
            for feature in selected:
                reasons[feature].add(Reason.ZERO_DENOMINATOR)
        else:
            beta = cov / var_b
            if BETA in selected:
                values[BETA] = _float(beta)
            if CORRELATION in selected:
                if var_i == 0:
                    reasons[CORRELATION].add(Reason.ZERO_DENOMINATOR)
                else:
                    values[CORRELATION] = _correlation(cov, var_b, var_i)
            if RESIDUAL in selected:
                if t in valid:
                    target_x = Fraction(*xs[-1])
                    target_y = Fraction(*ys[-1])
                    values[RESIDUAL] = _float(target_x - beta * target_y)
                else:
                    # A lost target pair gives the residual the causes of the target slots only.
                    reasons[RESIDUAL] = (set(slot_reasons(inst.facts[t - 1], cutoff) | slot_reasons(bench.facts[t - 1], cutoff)
                                             | slot_reasons(inst.facts[t], cutoff) | slot_reasons(bench.facts[t], cutoff)))
    columns: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    for feature in selected:
        status = Status.AVAILABLE if values[feature] is not None else first_status(reasons[feature])
        count = window
        if values[feature] is not None:
            # Amendment 1: an available row publishes expected = observed = n used pairs; the lost-pair causes stay
            # as reasons and as excluded evidence rows.
            count = n
            reasons[feature] = set(reasons_base)
            used = (valid[0] - 1, valid[-1])
            for facts in (inst.facts, bench.facts):
                for s_ in used:
                    fact: CloseFact = facts[s_]
                    if fact.row_index is None or fact.input_id is None or len(evidence) >= settings.evidence_limit:
                        continue
                    evidence.append(EvidenceRow(entity, feature, fact.input_id, f"slot:{s_}", fact.slot.end_ns,
                        fact.known_at_ns, fact.slot.start_ns, fact.slot.end_ns, "consumed", None, "completed_interval"))
            for facts in (inst.facts, bench.facts):
                for s_ in range(lo, t + 1):
                    fact = facts[s_]
                    causes_here = slot_reasons(fact, cutoff)
                    if not causes_here or fact.row_index is None or fact.input_id is None:
                        continue
                    first = next(r for r in PRECEDENCE if r in causes_here)
                    if (first in (Reason.UNKNOWN_AVAILABILITY, Reason.FUTURE_KNOWLEDGE)
                            and config.availability.knowledge_reason(fact.known_at_ns) != first.value):
                        continue
                    if len(evidence) >= settings.evidence_limit:
                        continue
                    evidence.append(EvidenceRow(entity, feature, fact.input_id, f"slot:{s_}", fact.slot.end_ns,
                        fact.known_at_ns, fact.slot.start_ns, fact.slot.end_ns, "excluded", first,
                        "completed_interval"))
        ordered = tuple(sorted(reasons[feature], key=lambda reason: reason.value))
        columns.append(FeatureColumn(feature, RELATIVE_ALGORITHM, ValueType.FLOAT64, "fraction", (entity,),
                                     (values[feature],)))
        quality.append(QualityRow(entity, feature, status, count, n, ordered))
    bindings = tuple(b for b in (inst.binding, bench.binding) if b is not None)
    metadata = ResultMetadata(config.session.namespace, config.session.session_id, config.availability,
                              config.digest, bindings, "python-exact", __version__, settings.evidence_limit)
    return FeatureResult(tuple(columns), tuple(quality), metadata, tuple(evidence))

