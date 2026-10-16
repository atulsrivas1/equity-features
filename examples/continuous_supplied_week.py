"""External synthetic consumer; all file I/O stays outside calculations."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

from equity_feature_contracts import ContractError
import equity_feature_continuous as c

MAX_FIXTURE_BYTES = 524288
MAX_RECEIPT_BYTES = 16384
CASE_IDS = (
    'supplied_friday_basis', 'basis_during_supplied_pause_not_live',
    'supplied_weekend_freeze', 'weekend_continuous_outage',
    'weekend_continuous_stale', 'weekend_continuous_unknown',
    'weekend_one_ns_reference_fact_gap', 'weekend_incomplete_census',
    'weekend_unknown_census_knowledge', 'weekend_late_census_knowledge',
    'reopen_before_first_knowledge_no_later_substitution',
    'reopen_after_original_first_knowledge',
)
FEATURE_IDS = (
    'cross_venue.basis', 'cross_venue.premium', 'cross_venue.freeze_max_abs',
    'cross_venue.freeze_mean_abs', 'cross_venue.reopen_gap',
    'cross_venue.reopen_premium',
)


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('utf-8')


def envelope(kind: str, payload: Any) -> bytes:
    return canonical({'kind': kind, 'schema_version': '1', 'payload': payload})


def evaluate(packet: dict[str, Any], fixture_sha256: str) -> dict[str, Any]:
    """Compare complete supplied literals; this is an example, not an oracle generator."""
    if (packet.get('kind') != 'EQ115_CONDITIONAL_SYNTHETIC_ORACLES'
            or packet.get('schema_version') != '1'
            or re.fullmatch('[0-9a-f]{64}', fixture_sha256) is None):
        raise ValueError('unsupported synthetic packet identity')
    cases = packet['cases']
    if type(cases) is not list or tuple(x['case_id'] for x in cases) != CASE_IDS:
        raise ValueError('the complete ordered twelve-case packet is required')
    features = c.list_features()
    if tuple(feature.id for feature in features) != FEATURE_IDS:
        raise ValueError('unexpected own discovery surface')
    for feature in features:
        c.require_capability(feature.id, 'batch')
        for mode in ('update', 'merge', 'restore'):
            try:
                c.require_capability(feature.id, mode)
            except ContractError as error:
                if error.code.value != 'unsupported_capability':
                    raise
            else:
                raise ValueError('unexpected nonbatch capability')
    functions = {'basis': c.compute_basis, 'freeze': c.compute_freeze,
                 'reopen': c.compute_reopen}
    records = []
    for case in cases:
        raw = envelope('continuous_input', case['input'])
        value = c.input_from_json(raw)
        before = c.to_json(value.config)
        if (c.config_digest(value.config) != case['config_digest']
                or c.input_digest(value) != case['input_digest']):
            raise ValueError('supplied input identity mismatch: ' + case['case_id'])
        expected = envelope('continuous_result', case['expected_result'])
        if hashlib.sha256(expected).hexdigest() != case['expected_result_digest']:
            raise ValueError('independent result literal identity mismatch: ' + case['case_id'])
        result = functions[value.config.operation](value)
        actual = c.to_json(result)
        if actual != expected or c.result_digest(result) != case['expected_result_digest']:
            raise ValueError('complete result mismatch: ' + case['case_id'])
        if (c.to_json(value) != raw or c.to_json(value.config) != before
                or c.from_json(actual) != result):
            raise ValueError('input preservation or own round trip failed')
        records.append({'case_id': case['case_id'], 'result_digest': c.result_digest(result)})
    return {'schema': 'continuous-supplied-week:1', 'fixture_sha256': fixture_sha256,
            'case_count': 12, 'cases': records, 'batch_feature_ids': list(FEATURE_IDS)}


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate synthetic JSON key')
        result[key] = value
    return result


def reject_constant(value: str) -> Any:
    raise ValueError('nonfinite synthetic JSON value')


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit('usage: continuous_supplied_week.py SYNTHETIC_FIXTURE.json')
    with Path(sys.argv[1]).open('rb') as stream:
        raw = stream.read(MAX_FIXTURE_BYTES + 1)
    if len(raw) > MAX_FIXTURE_BYTES:
        raise ValueError('synthetic fixture exceeds declared logical bound')
    packet = json.loads(raw, object_pairs_hook=unique_object, parse_constant=reject_constant)
    if type(packet) is not dict:
        raise ValueError('synthetic packet must be an object')
    receipt = canonical(evaluate(packet, hashlib.sha256(raw).hexdigest())) + b'\n'
    if len(receipt) > MAX_RECEIPT_BYTES:
        raise ValueError('synthetic receipt exceeds declared logical bound')
    sys.stdout.buffer.write(receipt)


if __name__ == '__main__':
    main()
