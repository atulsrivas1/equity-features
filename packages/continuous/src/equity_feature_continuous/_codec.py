"""Closed in-memory own envelopes; no old-core coercion or executable decoding."""
from __future__ import annotations
import json
from typing import NoReturn, cast
from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, ContractError, Coverage, ErrorCode,
    IntervalSpec, PriceUnit, SourceBinding,
)
from . import _model as m
from ._model import (ContinuousConfig, ContinuousInput, ContinuousResult, ConversionFact,
                     DeviationWitness, FeedFact, Leg, MetricValue, PriceObservation,
                     RoleReadiness, SelectedObservation)
from ._rational import Rational

ContinuousObject = ContinuousConfig | ContinuousInput | ContinuousResult


def _obj(value: object, fields: tuple[str, ...]) -> dict[str, object]:
    if type(value) is not dict:
        m._fail(ErrorCode.INVALID_SCHEMA, 'closed JSON object required')
    result = cast('dict[str, object]', value)
    if set(result) != set(fields):
        m._fail(ErrorCode.INVALID_SCHEMA, 'exact continuous JSON fields required')
    return result


def _str(value: object) -> str:
    if type(value) is not str:
        m._fail(ErrorCode.INVALID_SCHEMA, 'exact JSON string required')
    return value


def _int(value: object) -> int:
    if type(value) is not int:
        m._fail(ErrorCode.INVALID_SCHEMA, 'exact JSON integer required')
    return value


def _nullable_int(value: object) -> int | None:
    return None if value is None else _int(value)


def _bool(value: object) -> bool:
    if type(value) is not bool:
        m._fail(ErrorCode.INVALID_SCHEMA, 'exact JSON boolean required')
    return value


def _array(value: object, cap: int) -> list[object]:
    if type(value) is not list:
        m._fail(ErrorCode.INVALID_SCHEMA, 'JSON array required')
    result = cast('list[object]', value)
    if len(result) > cap:
        m._fail(ErrorCode.BOUNDS, 'JSON collection exceeds declared count')
    return result


def _interval(value: object) -> IntervalSpec:
    p = _obj(value, ('name', 'start_ns', 'end_ns'))
    name = _str(p['name']); m._label(name)
    start, end = _int(p['start_ns']), _int(p['end_ns'])
    m._ns(start); m._ns(end)
    if start >= end:
        m._fail(ErrorCode.BOUNDS, 'positive finite JSON interval required')
    return IntervalSpec(name, start, end)


def _availability(value: object) -> AvailabilitySpec:
    p = _obj(value, ('market_cutoff_ns', 'knowledge_cutoff_ns', 'evaluation_ns', 'mode', 'reconstruction_reason'))
    times = (_int(p['market_cutoff_ns']), _int(p['knowledge_cutoff_ns']), _int(p['evaluation_ns']))
    for time in times:
        m._ns(time)
    mode = _str(p['mode']); reason = p['reconstruction_reason']
    if reason is not None:
        m._label(_str(reason))
    if mode != 'known_at':
        m._fail(ErrorCode.UNSUPPORTED_CAPABILITY, 'continuous reconstruction is unsupported')
    return AvailabilitySpec(*times, mode=mode, reconstruction_reason=cast('str | None', reason))


def _config(value: object) -> ContinuousConfig:
    p = _obj(value, ('identity', 'schema_version', 'algorithm_version', 'operation', 'window',
                     'availability', 'anchor_ns', 'reopen_ns', 'max_continuous_age_ns',
                     'max_reference_age_ns', 'max_mismatch_ns', 'top_k', 'weighting', 'reference_mode'))
    return ContinuousConfig(identity=_str(p['identity']), schema_version=_str(p['schema_version']),
        algorithm_version=_str(p['algorithm_version']), operation=_str(p['operation']),
        window=_interval(p['window']), availability=_availability(p['availability']),
        anchor_ns=_nullable_int(p['anchor_ns']), reopen_ns=_nullable_int(p['reopen_ns']),
        max_continuous_age_ns=_int(p['max_continuous_age_ns']),
        max_reference_age_ns=_int(p['max_reference_age_ns']), max_mismatch_ns=_int(p['max_mismatch_ns']),
        top_k=_int(p['top_k']), weighting=_str(p['weighting']), reference_mode=_str(p['reference_mode']))


def _observation(value: object) -> PriceObservation:
    p = _obj(value, ('observation_id', 'event_ns', 'order_key', 'price', 'known_at_ns'))
    return PriceObservation(_str(p['observation_id']), _int(p['event_ns']), _int(p['order_key']),
                            _nullable_int(p['price']), _nullable_int(p['known_at_ns']))


def _leg(value: object) -> Leg:
    p = _obj(value, ('instrument_id', 'feed_id', 'product_id', 'underlying_id', 'quantity_unit',
                     'price_kind', 'source', 'price_unit', 'adjustment', 'scope', 'coverage',
                     'coverage_known_at_ns', 'observations'))
    s = _obj(p['source'], ('source_id', 'snapshot_id', 'mapping_version', 'input_id'))
    u = _obj(p['price_unit'], ('scale', 'currency'))
    a = _obj(p['adjustment'], ('basis', 'policy_version', 'action_snapshot', 'anchor'))
    c = _obj(p['coverage'], ('expected', 'observed', 'complete'))
    return Leg(instrument_id=_str(p['instrument_id']), feed_id=_str(p['feed_id']),
        product_id=_str(p['product_id']), underlying_id=_str(p['underlying_id']),
        quantity_unit=_str(p['quantity_unit']), price_kind=_str(p['price_kind']),
        source=SourceBinding(_str(s['source_id']), _str(s['snapshot_id']), _str(s['mapping_version']), _str(s['input_id'])),
        price_unit=PriceUnit(_int(u['scale']), _str(u['currency'])),
        adjustment=AdjustmentSpec(_str(a['basis']), _str(a['policy_version']), _str(a['action_snapshot']), _str(a['anchor'])),
        scope=_interval(p['scope']), coverage=Coverage(_nullable_int(c['expected']), _int(c['observed']), _bool(c['complete'])),
        coverage_known_at_ns=_nullable_int(p['coverage_known_at_ns']),
        observations=tuple(_observation(row) for row in _array(p['observations'], 4096)))


def _feed(value: object) -> FeedFact:
    p = _obj(value, ('fact_id', 'revision', 'feed_id', 'product_id', 'interval', 'state', 'known_at_ns'))
    return FeedFact(_str(p['fact_id']), _str(p['revision']), _str(p['feed_id']), _str(p['product_id']),
                    _interval(p['interval']), _str(p['state']), _nullable_int(p['known_at_ns']))


def _conversion(value: object) -> ConversionFact:
    p = _obj(value, ('fact_id', 'revision', 'continuous_instrument_id', 'reference_instrument_id',
                     'underlying_id', 'continuous_quantity_unit', 'reference_quantity_unit', 'currency',
                     'interval', 'reference_units_numerator', 'continuous_units_denominator', 'known_at_ns'))
    return ConversionFact(fact_id=_str(p['fact_id']), revision=_str(p['revision']),
        continuous_instrument_id=_str(p['continuous_instrument_id']), reference_instrument_id=_str(p['reference_instrument_id']),
        underlying_id=_str(p['underlying_id']), continuous_quantity_unit=_str(p['continuous_quantity_unit']),
        reference_quantity_unit=_str(p['reference_quantity_unit']), currency=_str(p['currency']),
        interval=_interval(p['interval']), reference_units_numerator=_int(p['reference_units_numerator']),
        continuous_units_denominator=_int(p['continuous_units_denominator']), known_at_ns=_nullable_int(p['known_at_ns']))


def _input(value: object) -> ContinuousInput:
    p = _obj(value, ('config', 'continuous', 'reference', 'feed_facts', 'conversion_facts'))
    cfg = _config(p['config']); continuous = _leg(p['continuous']); reference = _leg(p['reference'])
    m._pair(cfg, continuous, reference)
    feeds = tuple(_feed(f) for f in _array(p['feed_facts'], 256))
    m._feeds(feeds)
    conversions = tuple(_conversion(f) for f in _array(p['conversion_facts'], 256))
    return ContinuousInput(cfg, continuous, reference, feeds, conversions)


def _rational(value: object) -> Rational | None:
    if value is None:
        return None
    p = _obj(value, ('numerator', 'denominator'))
    n, d = _int(p['numerator']), _int(p['denominator'])
    if d <= 0:
        m._fail(ErrorCode.INVALID_SCHEMA, 'positive canonical wire denominator required')
    result = Rational(n, d)
    if (result.numerator, result.denominator) != (n, d):
        m._fail(ErrorCode.INVALID_SCHEMA, 'wire fractions must already be reduced')
    return result


def _role(value: object) -> RoleReadiness:
    p = _obj(value, ('role', 'status', 'reasons', 'proofs'))
    return RoleReadiness(_str(p['role']), _str(p['status']),
        tuple(_str(r) for r in _array(p['reasons'], 14)), tuple(_str(r) for r in _array(p['proofs'], 4096)))


def _metric(value: object) -> MetricValue:
    p = _obj(value, ('id', 'value'))
    return MetricValue(_str(p['id']), _rational(p['value']))


def _selected(value: object) -> SelectedObservation:
    p = _obj(value, ('role', 'observation_id'))
    return SelectedObservation(_str(p['role']), _str(p['observation_id']))


def _witness(value: object) -> DeviationWitness:
    p = _obj(value, ('role', 'observation_id', 'reference_id', 'conversion_fact_id', 'deviation'))
    deviation = _rational(p['deviation'])
    if deviation is None:
        m._fail(ErrorCode.INVALID_SCHEMA, 'deviation witness requires exact value')
    return DeviationWitness(_str(p['role']), _str(p['observation_id']), _str(p['reference_id']),
                             _str(p['conversion_fact_id']), deviation)


def _result(value: object) -> ContinuousResult:
    p = _obj(value, ('algorithm_version', 'operation', 'config_digest', 'input_digest', 'status',
                     'roles', 'metrics', 'selected', 'top_k', 'population_count', 'available_at_ns'))
    return ContinuousResult(algorithm_version=_str(p['algorithm_version']), operation=_str(p['operation']),
        config_digest=_str(p['config_digest']), input_digest=_str(p['input_digest']), status=_str(p['status']),
        roles=tuple(_role(r) for r in _array(p['roles'], 7)), metrics=tuple(_metric(r) for r in _array(p['metrics'], 2)),
        selected=tuple(_selected(r) for r in _array(p['selected'], 4097)), top_k=tuple(_witness(r) for r in _array(p['top_k'], 32)),
        population_count=_nullable_int(p['population_count']), available_at_ns=_nullable_int(p['available_at_ns']))


def _pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            m._fail(ErrorCode.INVALID_SCHEMA, 'duplicate continuous JSON key')
        result[key] = value
    return result


def _constant(value: str) -> NoReturn:
    m._fail(ErrorCode.INVALID_SCHEMA, 'nonfinite JSON numbers are unsupported')


def _read(raw: bytes, expected_kind: str | None = None) -> ContinuousObject:
    if type(raw) is not bytes:
        m._fail(ErrorCode.INVALID_SCHEMA, 'bounded concrete UTF8 bytes required')
    cap = m.BYTE_LIMITS[expected_kind] if expected_kind is not None else m.BYTE_LIMITS['continuous_input']
    if len(raw) > cap:
        m._fail(ErrorCode.BOUNDS, 'encoded continuous representation exceeds declared bytes')
    try:
        decoded = json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs, parse_constant=_constant)
    except ContractError:
        raise
    except (ValueError, UnicodeDecodeError, RecursionError):
        m._fail(ErrorCode.INVALID_SCHEMA, 'invalid continuous UTF8 JSON')
    root = _obj(decoded, ('kind', 'schema_version', 'payload'))
    version = _str(root['schema_version'])
    if version != '1':
        m._fail(ErrorCode.INCOMPATIBLE_VERSION, 'unsupported continuous envelope version')
    kind = _str(root['kind'])
    if kind not in m.BYTE_LIMITS or expected_kind is not None and kind != expected_kind:
        m._fail(ErrorCode.INVALID_SCHEMA, 'unexpected continuous envelope kind')
    if len(raw) > m.BYTE_LIMITS[kind]:
        m._fail(ErrorCode.BOUNDS, 'encoded continuous representation exceeds declared bytes')
    if kind == 'continuous_config':
        return _config(root['payload'])
    if kind == 'continuous_input':
        return _input(root['payload'])
    return _result(root['payload'])


def from_json(raw: bytes) -> ContinuousObject:
    """Dispatch the three own kinds under the overall input byte cap.

    Typed decoders additionally enforce their narrower kind cap before parsing.
    This dispatcher checks that narrower cap as soon as its kind is parsed.
    """
    return _read(raw)


def config_from_json(raw: bytes) -> ContinuousConfig:
    return cast(ContinuousConfig, _read(raw, 'continuous_config'))


def input_from_json(raw: bytes) -> ContinuousInput:
    return cast(ContinuousInput, _read(raw, 'continuous_input'))


def result_from_json(raw: bytes) -> ContinuousResult:
    return cast(ContinuousResult, _read(raw, 'continuous_result'))


def to_json(value: ContinuousObject) -> bytes:
    if type(value) is ContinuousConfig:
        return m.encode_payload('continuous_config', m.config_payload(value))
    if type(value) is ContinuousInput:
        return m.encode_payload('continuous_input', m.input_payload(value))
    if type(value) is ContinuousResult:
        return m.encode_payload('continuous_result', m.result_payload(value))
    m._fail(ErrorCode.INVALID_SCHEMA, 'exact own continuous object required')


def config_digest(value: ContinuousConfig) -> str:
    m._config(value)
    return value.identity_digest


def input_digest(value: ContinuousInput) -> str:
    m._input(value)
    return value.identity_digest


def result_digest(value: ContinuousResult) -> str:
    m._result(value)
    return value.identity_digest
