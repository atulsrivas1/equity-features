"""Pure finite supplied-snapshot arithmetic and causal readiness."""
from __future__ import annotations
from dataclasses import dataclass, field
from fractions import Fraction
from typing import cast
from equity_feature_contracts import ContractError, ErrorCode
from . import _model as m
from ._rational import Rational


@dataclass
class _Role:
    name: str
    reasons: list[str] = field(default_factory=list)
    proofs: list[str] = field(default_factory=list)
    blocked: bool = False
    empty: bool = False

    def reason(self, reason: str) -> None:
        if reason not in self.reasons:
            self.reasons.append(reason)

    def proof(self, pointer: str) -> None:
        if pointer not in self.proofs:
            self.proofs.append(pointer)

    def finish(self) -> m.RoleReadiness:
        proofs = self.proofs
        if self.name in ('continuous_feed', 'reference_feed', 'conversion'):
            proofs = sorted(proofs, key=lambda pointer: int(pointer.rsplit('/', 1)[1]))
        status = 'blocked' if self.blocked else 'unavailable' if self.reasons else 'ready'
        if self.empty:
            status = 'not_applicable'
        return m.RoleReadiness(self.name, status, tuple(r for r in m.REASONS if r in self.reasons), proofs)


def _time(time: int | None, cutoff: int, role: _Role, consumed: list[int]) -> None:
    if time is None:
        role.reason('unknown_availability')
    else:
        consumed.append(time)
        if time > cutoff:
            role.reason('future_knowledge')


def _coverage(leg: m.Leg, name: str, cutoff: int, role: _Role, consumed: list[int]) -> None:
    for pointer in ('scope', 'coverage', 'coverage_known_at_ns'):
        role.proof('/'+name+'/'+pointer)
    if not leg.coverage.complete:
        role.reason('incomplete_coverage')
    _time(leg.coverage_known_at_ns, cutoff, role, consumed)


def _latest_known(leg: m.Leg, name: str, limit: int, cutoff: int,
                  role: _Role, consumed: list[int]) -> list[int]:
    market = [i for i, row in enumerate(leg.observations) if row.event_ns <= limit]
    known = [i for i in market if leg.observations[i].known_at_ns is not None
             and cast(int, leg.observations[i].known_at_ns) <= cutoff]
    if known:
        return [known[-1]]
    if not market:
        role.reason('absent_observation')
    for i in market:
        role.proof('/'+name+'/observations/'+str(i))
        _time(leg.observations[i].known_at_ns, cutoff, role, consumed)
    return []


def _prices(leg: m.Leg, name: str, indices: list[int], cutoff: int,
            role: _Role, consumed: list[int]) -> None:
    if role.blocked:
        return
    if not indices and not role.reasons:
        role.reason('absent_observation')
    for i in indices:
        row = leg.observations[i]
        role.proof('/'+name+'/observations/'+str(i))
        _time(row.known_at_ns, cutoff, role, consumed)
        if row.price is None:
            role.reason('null_price')


def _cover(value: m.ContinuousInput, leg: m.Leg, start: int, end: int,
           wanted: str, role: _Role, consumed: list[int]) -> None:
    """Cover a half-open finite range; a one-nanosecond range is a point."""
    intervals: list[tuple[int, int]] = []
    for i, fact in enumerate(value.feed_facts):
        if (fact.feed_id, fact.product_id) != (leg.feed_id, leg.product_id):
            continue
        left, right = max(start, fact.interval.start_ns), min(end, fact.interval.end_ns)
        if left >= right:
            continue
        intervals.append((left, right))
        role.proof('/feed_facts/'+str(i))
        _time(fact.known_at_ns, value.config.availability.knowledge_cutoff_ns, role, consumed)
        if fact.state != wanted:
            role.reason(fact.state if fact.state in ('unknown', 'stale', 'outage')
                        else 'not_live' if wanted == 'live' else 'not_scheduled_freeze')
    reached = start
    for left, right in sorted(intervals):
        if left > reached:
            role.reason('absent_fact')
        reached = max(reached, right)
    if reached < end:
        role.reason('absent_fact')


def _mappings(value: m.ContinuousInput, indices: list[int], role: _Role,
              consumed: list[int]) -> dict[int, m.ConversionFact]:
    mappings: dict[int, m.ConversionFact] = {}
    c, r = value.continuous, value.reference
    if not indices:
        role.blocked = value.config.operation != 'freeze'
    for i in indices:
        event = c.observations[i].event_ns
        matching = [(j, fact) for j, fact in enumerate(value.conversion_facts)
                    if (fact.continuous_instrument_id, fact.reference_instrument_id) == (c.instrument_id, r.instrument_id)
                    and fact.interval.start_ns <= event < fact.interval.end_ns]
        if not matching:
            role.reason('absent_fact')
            continue
        j, fact = matching[0]
        mappings[i] = fact
        role.proof('/conversion_facts/'+str(j))
        _time(fact.known_at_ns, value.config.availability.knowledge_cutoff_ns, role, consumed)
    return mappings


def _checked(value: Fraction) -> Fraction:
    # Rational reduces before checking. Comparator/unreduced temporaries are not stages.
    Rational(value.numerator, value.denominator)
    return value


def _normalized(row: m.PriceObservation, leg: m.Leg, fact: m.ConversionFact) -> Fraction:
    scaled = _checked(Fraction(cast(int, row.price), 10**leg.price_unit.scale))
    return _checked(scaled * Fraction(fact.continuous_units_denominator, fact.reference_units_numerator))


def _rational(value: Fraction) -> Rational:
    return Rational(value.numerator, value.denominator)


def _compute(value: m.ContinuousInput, expected: str) -> m.ContinuousResult:
    m._input(value)
    cfg = value.config
    if cfg.operation != expected:
        raise ContractError(ErrorCode.INVALID_CONFIG, 'entry point requires its matching operation')
    config_digest, input_digest = cfg.identity_digest, value.identity_digest
    c, r = value.continuous, value.reference
    cutoff = cfg.availability.knowledge_cutoff_ns
    consumed: list[int] = [cfg.window.end_ns]
    roles = [_Role(name) for name in m.ROLES]
    cc, rc, cp, rp, cf, rf, conversion = roles
    _coverage(c, 'continuous', cutoff, cc, consumed)
    _coverage(r, 'reference', cutoff, rc, consumed)
    ci: list[int]
    ri: list[int]
    if expected == 'basis':
        ci = _latest_known(c, 'continuous', cast(int, cfg.anchor_ns), cutoff, cp, consumed)
        if ci:
            ri = _latest_known(r, 'reference', c.observations[ci[0]].event_ns, cutoff, rp, consumed)
        else:
            ri = []
            rp.blocked = True
    elif expected == 'freeze':
        ci = list(range(len(c.observations)))
        ri = [len(r.observations)-1] if r.observations else []
        if not ci:
            cp.blocked = True
    else:
        ci = [len(c.observations)-1] if c.observations else []
        after = [i for i, row in enumerate(r.observations) if row.event_ns >= cast(int, cfg.reopen_ns)]
        ri = after[:1]
    _prices(c, 'continuous', ci, cutoff, cp, consumed)
    _prices(r, 'reference', ri, cutoff, rp, consumed)
    if expected == 'basis':
        anchor = cast(int, cfg.anchor_ns)
        if ci and anchor-c.observations[ci[0]].event_ns > cfg.max_continuous_age_ns:
            cp.reason('stale_observation')
        if ri and anchor-r.observations[ri[0]].event_ns > cfg.max_reference_age_ns:
            rp.reason('stale_observation')
        mismatch = bool(ci and ri and c.observations[ci[0]].event_ns-r.observations[ri[0]].event_ns > cfg.max_mismatch_ns)
    elif expected == 'freeze':
        if ri and cfg.window.start_ns-r.observations[ri[0]].event_ns > cfg.max_reference_age_ns:
            rp.reason('stale_observation')
        mismatch = bool(ri and cfg.window.start_ns-r.observations[ri[0]].event_ns > cfg.max_mismatch_ns)
    else:
        boundary = cast(int, cfg.reopen_ns)
        if ci and boundary-c.observations[ci[0]].event_ns > cfg.max_continuous_age_ns:
            cp.reason('stale_observation')
        if ri and r.observations[ri[0]].event_ns-boundary > cfg.max_reference_age_ns:
            rp.reason('stale_observation')
        mismatch = bool(ci and ri and r.observations[ri[0]].event_ns-c.observations[ci[0]].event_ns > cfg.max_mismatch_ns)
    if mismatch:
        if ci:
            cp.reason('mismatch')
        rp.reason('mismatch')
    if expected == 'freeze':
        _cover(value, c, cfg.window.start_ns, cfg.window.end_ns, 'live', cf, consumed)
        if ri:
            point = r.observations[ri[0]].event_ns
            _cover(value, r, point, point+1, 'live', rf, consumed)
            _cover(value, r, cfg.window.start_ns, cfg.window.end_ns, 'scheduled_freeze', rf, consumed)
        else:
            rf.blocked = True
    else:
        if ci:
            point = c.observations[ci[0]].event_ns
            _cover(value, c, point, point+1, 'live', cf, consumed)
            if expected == 'basis':
                anchor = cast(int, cfg.anchor_ns)
                _cover(value, c, anchor, anchor+1, 'live', cf, consumed)
        else:
            cf.blocked = True
        if ri:
            point = r.observations[ri[0]].event_ns
            _cover(value, r, point, point+1, 'live', rf, consumed)
            if expected == 'basis':
                anchor = cast(int, cfg.anchor_ns)
                _cover(value, r, anchor, anchor+1, 'live', rf, consumed)
            else:
                boundary = cast(int, cfg.reopen_ns)
                _cover(value, r, boundary-1, boundary, 'scheduled_freeze', rf, consumed)
                _cover(value, r, boundary, boundary+1, 'live', rf, consumed)
        else:
            rf.blocked = True
    mappings = _mappings(value, ci, conversion, consumed)
    other_ready = all(not role.reasons and not role.blocked for role in (cc, rc, rp, cf, rf, conversion))
    if expected == 'freeze' and not ci and other_ready:
        cp.blocked = False; cp.empty = True; cp.reason('observed_empty')
    status = ('incomplete_coverage' if any('incomplete_coverage' in role.reasons for role in roles)
              else 'not_applicable' if cp.empty
              else 'missing_input' if any(role.reasons or role.blocked for role in roles)
              else 'available')
    selected = [m.SelectedObservation('continuous', c.observations[i].observation_id) for i in ci]
    selected += [m.SelectedObservation('reference', r.observations[i].observation_id) for i in ri]
    values: tuple[Rational | None, Rational | None] = (None, None)
    witnesses: list[m.DeviationWitness] = []
    if status == 'available':
        reference = r.observations[ri[0]]
        y = _checked(Fraction(cast(int, reference.price), 10**r.price_unit.scale))
        deviations = [(i, _checked(_normalized(c.observations[i], c, mappings[i])-y)) for i in ci]
        if expected == 'freeze':
            total = Fraction(0)
            for _, deviation in deviations:
                total = _checked(total+abs(deviation))
            mean = _checked(total/len(ci))
            ordered = sorted(deviations, key=lambda item: (-abs(item[1]), c.observations[item[0]].event_ns,
                             c.observations[item[0]].order_key, c.observations[item[0]].observation_id.encode('utf-8')))
            values = (_rational(abs(ordered[0][1])), _rational(mean))
            witnesses = [m.DeviationWitness('continuous', c.observations[i].observation_id,
                           reference.observation_id, mappings[i].fact_id, _rational(deviation))
                         for i, deviation in ordered[:cfg.top_k]]
        else:
            difference = deviations[0][1]
            values = (_rational(difference), _rational(_checked(difference/y)))
    available = max(consumed) if status in ('available', 'not_applicable') else None
    result = m.ContinuousResult('1', expected, config_digest, input_digest, status,
                [role.finish() for role in roles],
                [m.MetricValue(name, number) for name, number in zip(m.METRICS[expected], values)],
                selected, witnesses, len(ci) if expected == 'freeze' else None, available)
    # Enforce the complete own envelope bound BEFORE returning a numerical value.
    m.encode_payload('continuous_result', m.result_payload(result))
    return result


def compute_basis(value: m.ContinuousInput) -> m.ContinuousResult:
    """Latest-known backward-aligned supplied basis and ratio."""
    return _compute(value, 'basis')


def compute_freeze(value: m.ContinuousInput) -> m.ContinuousResult:
    """Complete freeze population maximum/mean absolute deviation and topK."""
    return _compute(value, 'freeze')


def compute_reopen(value: m.ContinuousInput) -> m.ContinuousResult:
    """Immutable pre-boundary continuous versus first reopening reference outcome."""
    return _compute(value, 'reopen')
