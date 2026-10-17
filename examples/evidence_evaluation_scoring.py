"""Independent DATA-only EQ117 scorer. Never imported by generic observer."""
from __future__ import annotations
import hashlib
import json
import math
import statistics
from typing import Any

PROPOSAL_SHA256 = '7405067b0360126a462bb7a66b5a89416cf93399843b0933b358760804e45073'
ORACLE_SHA256 = 'eb2824cc32a2573b51f825199b26c2dde2ae6f73eeda77ed068e8794c9e81fde'
ARMS = ('ordinary_log', 'evidence_ledger')
CASES = tuple('P%02d' % i for i in range(1, 9))
RAW_FIELDS = frozenset(('run_id', 'proposal_sha256', 'runner_source_map_sha256', 'input_map_sha256',
 'environment_id', 'os', 'python', 'installed_map_sha256', 'case_id', 'arm', 'repetition',
 'process_state', 'arm_position', 'status', 'error_code', 'diagnosis', 'anchor_status',
 'retention', 'model_identity', 'narrative_status', 'replay_status', 'calculator_calls',
 'operation_trace', 'record_ns', 'export_ns', 'read_verify_replay_ns', 'launch_import_ns',
 'common_fixture_compute_ns', 'closed_file_bytes', 'file_count', 'transient_peak_bytes',
 'stdout_sha256', 'stderr_sha256', 'declared_strict_admission', 'recomputed_strict_admission',
 'recomputed_strict_reason', 'return_code', 'record_start_ns', 'record_end_ns', 'export_start_ns',
 'export_end_ns', 'read_verify_replay_start_ns', 'read_verify_replay_end_ns', 'launch_import_start_ns',
 'launch_import_end_ns', 'common_fixture_compute_start_ns', 'common_fixture_compute_end_ns'))
STAGES = ('record', 'export', 'read_verify_replay', 'launch_import', 'common_fixture_compute')
OPERATIONS = ('file_read','file_write','file_close','json_decode','json_encode','hash_verify',
 'event_decode','chain_verify','ledger_open','ledger_append','ledger_verify','ledger_export',
 'ledger_close','bundle_read','payload_verify','assessment','replay_entry','calculator_call')
API_CATEGORIES = {'json.loads':'json_decode','json.dumps':'json_encode','observer.hash_verify':'hash_verify',
 'events.decode_event':'event_decode','ledger.verify_events':'chain_verify','ledger.verify_page':'chain_verify',
 'Ledger.create':'ledger_open','Ledger.open':'ledger_open','Ledger.append':'ledger_append',
 'Ledger.verify':'ledger_verify','Ledger.export_page':'ledger_export','Ledger.close':'ledger_close',
 'bundles.read_bundle':'bundle_read','events.verify_payload':'payload_verify',
 'diagnostics.evaluate_diagnostics':'assessment','observer.assessment':'assessment',
 'replay.replay_bundle':'replay_entry','session.compute_trades':'calculator_call',
 'io.read':'file_read','io.write':'file_write','io.close':'file_close'}


def exact(left: Any, right: Any) -> bool:
    def canonical(value: Any) -> str:
        return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)
    return canonical(left)==canonical(right)


def native(value: Any) -> Any:
    """Only translates already frozen independent literal tags, without codecs."""
    if type(value) is list:
        return [native(x) for x in value]
    if type(value) is not dict:
        return value
    if set(value) == {'int'}:
        return int(value['int'])
    if set(value) == {'enum', 'value'}:
        return value['value']
    if set(value) == {'record', 'fields'}:
        return dict(type=value['record'], fields={k: native(v) for k, v in value['fields'].items()})
    return {k: native(v) for k, v in value.items()}


def load_oracle(raw: bytes) -> dict[str, Any]:
    assert hashlib.sha256(raw).hexdigest() == ORACLE_SHA256
    return json.loads(raw)


def expected(case_id: str, oracle: dict[str, Any]) -> dict[str, Any]:
    case = next(x for x in oracle['cases'] if x['id'] == case_id)
    out = dict(load='verified', consistency=None, anchor=None, retention=None, model_identity=None,
        narrative_status=None, decision=None, declared_strict_admission=None, recomputed_strict_admission=None,
        recomputed_strict_reason=None, declared_strict=None, recomputed_strict=None, native_result=None,
        configuration=None, input_fingerprints=None, advisory_verification=None, explanation_verification=None,
        replay_status='refused_before_calculator', calculator_calls=0,
        source_authenticated=False, execution_verified=False)
    if case_id == 'P07':
        out['load'] = 'integrity_mismatch'
        return out
    future = case_id == 'P02'
    strict = oracle['strict_reports']['future' if future else 'clean']
    envelope = dict(oracle['configuration']['value'])
    envelope['domain'] = 'feature_result'
    envelope['value'] = oracle['future_native_result' if future else 'clean_native_result']
    out.update(consistency='verified', anchor=case['anchor'], retention=case['retention'],
        model_identity='not_supplied' if case_id == 'P08' else 'declared',
        narrative_status=case['narrative_status'], decision=case['decision'],
        declared_strict_admission=case['admission'],
        recomputed_strict_admission='UNKNOWN' if case_id == 'P05' else case['admission'],
        recomputed_strict_reason='retained_input_missing' if case_id == 'P05' else None,
        declared_strict=strict, recomputed_strict=None if case_id == 'P05' else strict,
        native_result=native(envelope), configuration=native(oracle['configuration']['value']),
        input_fingerprints=[dict(role='trades', input_id='trades', content=oracle['strict_input_fingerprints']['future' if future else 'clean'])],
        advisory_verification='declared_unverified', explanation_verification='recomputed_matched',
        replay_status=case['compute_replay'], calculator_calls=case['compute_calls'])
    return out


def schedule() -> list[dict[str, Any]]:
    odd = ('P01', 'P05', 'P03', 'P07', 'P02', 'P06', 'P04', 'P08')
    rows = []
    for repetition in range(1, 11):
        for case_id in odd if repetition % 2 else tuple(reversed(odd)):
            stable = CASES.index(case_id) + 1
            arms = ARMS if (repetition + stable) % 2 == 0 else tuple(reversed(ARMS))
            for position, arm in enumerate(arms, 1):
                rows.append(dict(case_id=case_id, arm=arm, repetition=repetition,
                    process_state='PROCESS_COLD' if repetition <= 5 else 'PROCESS_WARM', arm_position=position))
    assert len(rows) == 160 and len({(x['case_id'], x['arm'], x['repetition']) for x in rows}) == 160
    return rows


def validate_record(row: dict[str, Any]) -> None:
    assert type(row) is dict and set(row) == RAW_FIELDS
    assert row['proposal_sha256'] == PROPOSAL_SHA256 and row['case_id'] in CASES and row['arm'] in ARMS
    assert row['os'] in ('Windows', 'Linux') and type(row['repetition']) is int and 1 <= row['repetition'] <= 10
    assert row['process_state'] == ('PROCESS_COLD' if row['repetition'] <= 5 else 'PROCESS_WARM')
    assert type(row['arm_position']) is int and row['arm_position'] in (1, 2)
    assert row['status'] in ('valid', 'failed', 'not_run')
    assert row['error_code'] is None or type(row['error_code']) is str and len(row['error_code']) <= 48
    assert row['return_code'] is None or type(row['return_code']) is int
    for key in ('run_id', 'python'):
        assert type(row[key]) is str and row[key].isascii() and 0 < len(row[key]) <= 128
    for key in ('runner_source_map_sha256', 'input_map_sha256', 'environment_id', 'installed_map_sha256', 'stdout_sha256', 'stderr_sha256'):
        value = row[key]
        assert value is None and row['status'] != 'valid' or type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value)
    for key in ('calculator_calls', 'closed_file_bytes', 'file_count', 'transient_peak_bytes'):
        value = row[key]
        assert value is None or type(value) is int and 0 <= value < 2**63
    for stage in STAGES:
        start, end, duration = (row[stage + key] for key in ('_start_ns', '_end_ns', '_ns'))
        if start is None or end is None:
            assert start is end is duration is None
            assert row['status'] != 'valid'
        else:
            assert all(type(x) is int and 0 <= x < 2**63 for x in (start, end, duration))
            assert end >= start and duration == end - start
    if row['status'] == 'valid':
        assert row['error_code'] is None and row['return_code'] == 0 and type(row['diagnosis']) is dict
        assert type(row['calculator_calls']) is int and row['calculator_calls'] >= 0
        assert type(row['closed_file_bytes']) is int and type(row['file_count']) is int
        assert exact(row['calculator_calls'],row['diagnosis']['calculator_calls'])
        for target,source in (('anchor_status','anchor'),('retention','retention'),('model_identity','model_identity'),
            ('narrative_status','narrative_status'),('replay_status','replay_status'),
            ('declared_strict_admission','declared_strict_admission'),('recomputed_strict_admission','recomputed_strict_admission'),
            ('recomputed_strict_reason','recomputed_strict_reason')):
            assert exact(row[target],row['diagnosis'][source])
        trace=row['operation_trace']
        assert type(trace)is dict and set(trace)=={'counts','total','api_calls','cli_invocations','sequence_sha256','api_name_order','sequence_encoding','boundary_scope'}
        assert set(trace['counts'])==set(OPERATIONS) and set(trace['api_calls'])==set(API_CATEGORIES)
        assert all(type(x)is int and 0<=x<=1000000 for x in [trace['total'],*trace['counts'].values(),*trace['api_calls'].values()])
        assert trace['total']==sum(trace['counts'].values())==sum(trace['api_calls'].values())
        assert all(trace['counts'][category]==sum(value for api,value in trace['api_calls'].items()
                   if API_CATEGORIES[api]==category) for category in OPERATIONS)
        assert trace['counts']['calculator_call']==row['calculator_calls']
        assert type(trace['cli_invocations'])is int and trace['cli_invocations'] in (0,1)
        if row['process_state']=='PROCESS_COLD':assert trace['cli_invocations']==1
        assert trace['api_name_order']==sorted(API_CATEGORIES)
        assert type(trace['sequence_sha256'])is str and len(trace['sequence_sha256'])==64 and all(x in '0123456789abcdef' for x in trace['sequence_sha256'])
        assert trace['sequence_encoding']=='category-index,api-index,positive-repeat-count'
        assert trace['boundary_scope']=='selected nested Python APIs and io.IOBase stream calls; not C-internal SQL or OS I/O'
    assert len((json.dumps(row, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False) + '\n').encode()) <= 16384


def distribution(values: list[int]) -> dict[str, int | float]:
    assert values and all(type(x) is int and x >= 0 for x in values)
    ordered = sorted(values)
    return dict(n=len(values), median=statistics.median(ordered), minimum=ordered[0], maximum=ordered[-1],
        p25=ordered[math.ceil(.25 * len(ordered))-1], p75=ordered[math.ceil(.75 * len(ordered))-1])


def score(rows: list[dict[str, Any]], oracle: dict[str, Any], systems: tuple[str, ...]) -> dict[str, Any]:
    """Never drops a failure/NOT_RUN slot or treats a partial OS as full success."""
    assert systems in (('Windows',), ('Linux',), ('Windows', 'Linux'))
    assert len(rows) == 160 * len(systems)
    indexed = {}
    expected_keys = {(os, x['case_id'], x['arm'], x['repetition']) for os in systems for x in schedule()}
    for row in rows:
        validate_record(row)
        key = (row['os'], row['case_id'], row['arm'], row['repetition'])
        assert key not in indexed and key in expected_keys
        reference = next(x for x in schedule() if (x['case_id'], x['arm'], x['repetition']) == key[1:])
        assert all(row[k] == reference[k] for k in reference)
        indexed[key] = row
    assert set(indexed) == expected_keys
    assert len({row['run_id'] for row in rows}) == 1
    assert len({row['runner_source_map_sha256'] for row in rows}) == 1
    for system in systems:
        cohort = [row for row in rows if row['os'] == system]
        for field in ('environment_id', 'installed_map_sha256', 'python'):
            assert len({row[field] for row in cohort}) == 1
        for case in CASES:
            for rep in range(1, 11):
                left, right = (indexed[(system, case, arm, rep)] for arm in ARMS)
                assert left['input_map_sha256'] == right['input_map_sha256']
                assert all(left['common_fixture_compute'+suffix] == right['common_fixture_compute'+suffix]
                           for suffix in ('_start_ns', '_end_ns', '_ns'))
    correctness = {key: row['status'] == 'valid' and exact(row['diagnosis'],expected(row['case_id'], oracle)) for key, row in indexed.items()}
    comparisons = []
    stage_gates, storage_gates, operation_gates = [], [], []
    for system in systems:
        for state, reps in (('PROCESS_COLD', range(1, 6)), ('PROCESS_WARM', range(6, 11))):
            improved = 0
            for case in CASES:
                arms = {arm: [indexed[(system, case, arm, rep)] for rep in reps] for arm in ARMS}
                valid = all(correctness[(system, case, arm, rep)] for arm in ARMS for rep in reps)
                result: dict[str, Any] = dict(os=system, process_state=state, case_id=case, all_five_pairs_valid=valid,
                                               stages={}, storage=[], paired_differences=[])
                if valid:
                    for stage in ('record', 'export', 'read_verify_replay'):
                        baseline = distribution([x[stage+'_ns'] for x in arms[ARMS[0]]])
                        evidence = distribution([x[stage+'_ns'] for x in arms[ARMS[1]]])
                        gate = evidence['median'] <= 2 * baseline['median'] + 5000000
                        result['stages'][stage] = dict(ordinary_log=baseline, evidence_ledger=evidence, within_budget=gate)
                        stage_gates.append(gate)
                    result['separate_costs'] = {name:{arm:distribution([x[name+'_ns'] for x in arms[arm]])
                        for arm in ARMS} for name in ('launch_import','common_fixture_compute')}
                    result['combined_stage_plus_shared_fixture_ns'] = {arm:distribution([
                        sum(x[s+'_ns'] for s in ('record','export','read_verify_replay','common_fixture_compute'))
                        for x in arms[arm]]) for arm in ARMS}
                    result['combined_cost_scope']='Shared fixture cost is shown once for each arm comparison; it ran once per pair. Launch/import is separate and warm rows reference the same actor launch.'
                    for baseline, evidence in zip(arms[ARMS[0]], arms[ARMS[1]], strict=True):
                        gate = evidence['closed_file_bytes'] <= 2 * baseline['closed_file_bytes'] + 32768
                        storage_gates.append(gate)
                        result['storage'].append(dict(repetition=baseline['repetition'], ordinary_log=baseline['closed_file_bytes'],
                            evidence_ledger=evidence['closed_file_bytes'], within_budget=gate))
                        result['paired_differences'].append(dict(repetition=baseline['repetition'],
                            stages={stage: evidence[stage+'_ns']-baseline[stage+'_ns'] for stage in ('record', 'export', 'read_verify_replay')},
                            operations=evidence['operation_trace']['total']-baseline['operation_trace']['total'],
                            bytes=evidence['closed_file_bytes']-baseline['closed_file_bytes'],
                            relative_reductions=dict(
                                stages={stage:(baseline[stage+'_ns']-evidence[stage+'_ns'])/baseline[stage+'_ns']
                                    if baseline[stage+'_ns'] else None for stage in ('record','export','read_verify_replay')},
                                operations=(baseline['operation_trace']['total']-evidence['operation_trace']['total'])/baseline['operation_trace']['total']
                                    if baseline['operation_trace']['total'] else None,
                                bytes=(baseline['closed_file_bytes']-evidence['closed_file_bytes'])/baseline['closed_file_bytes']
                                    if baseline['closed_file_bytes'] else None)))
                    baseline_ops = distribution([x['operation_trace']['total'] for x in arms[ARMS[0]]])
                    evidence_ops = distribution([x['operation_trace']['total'] for x in arms[ARMS[1]]])
                    denominator = baseline_ops['median']
                    reduction = (denominator - evidence_ops['median'])/denominator if denominator else None
                    hit = denominator>0 and 5*(denominator-evidence_ops['median'])>=denominator
                    improved += int(hit)
                    result['operations'] = dict(ordinary_log=baseline_ops, evidence_ledger=evidence_ops,
                        reduction_by_ratio_of_medians=reduction, meets_optional_improvement=hit)
                else:
                    stage_gates.append(False);storage_gates.append(False)
                    result['operations'] = dict(reduction_by_ratio_of_medians=None, meets_optional_improvement=False)
                comparisons.append(result)
            operation_gates.append(dict(os=system, process_state=state, improved_cases=improved, required=6, meets_optional_signal=improved>=6))
    valid_rows = [row for row in rows if row['status'] == 'valid']
    matched = sum(correctness.values())
    replay_matches = sum(correctness[key] and row['replay_status'] == 'matched' and row['calculator_calls'] == 1 for key,row in indexed.items())
    zero_safe = sum(correctness[key] and row['case_id'] in ('P05','P07') and row['calculator_calls'] == 0 for key,row in indexed.items())
    complete = systems == ('Windows', 'Linux')
    return dict(schema='eq117.study.summary.v1', systems=list(systems), full_320_study=complete,
        planned=len(rows), attempted=sum(x['status']!='not_run' for x in rows), valid=len(valid_rows),
        failed=sum(x['status']=='failed' for x in rows), not_run=sum(x['status']=='not_run' for x in rows),
        exact_correct=matched, wrong_or_unavailable=len(rows)-matched, eligible_replay_matches=replay_matches,
        observed_calculator_calls=sum(row['calculator_calls'] for row in rows if row['calculator_calls'] is not None),
        calculator_call_observations_unavailable=sum(row['calculator_calls'] is None for row in rows),
        replay_status_counts={status:sum((row['replay_status'] or 'unavailable_observation')==status for row in rows)
            for status in sorted({row['replay_status'] or 'unavailable_observation' for row in rows})},
        required_eligible_replays=120*len(systems), missing_corrupt_zero_calls=zero_safe,
        required_missing_corrupt_zero_calls=40*len(systems), clean_false_positives=sum(
            row['status']=='valid' and row['case_id']=='P01' and any(
                row['diagnosis'][field] != wanted for field,wanted in (
                    ('load','verified'),('consistency','verified'),('anchor','matched_terminal'),
                    ('retention','complete'),('narrative_status','matched'),('decision','DEFER'),
                    ('recomputed_strict_admission','admitted'),('model_identity','declared')))
            for row in rows),
        correctness_pass=complete and matched==320 and replay_matches==240 and zero_safe==80,
        elapsed_budget_pass=complete and all(stage_gates), storage_budget_pass=complete and all(storage_gates),
        optional_operation_signal=complete and all(x['meets_optional_signal'] for x in operation_gates),
        comparisons=comparisons, operation_strata=operation_gates,
        human_debugging_steps=None, human_elapsed_ns=None, human_usefulness='UNKNOWN', demand='UNKNOWN',
        independent_trust_need='UNKNOWN', product_decision='DEFER', witness_selected=False,
        limits=['Automated fixed-fixture observations, not independent participants or human usability.',
                'Stage clocks and selected semantic/API counts, not physical I/O/resource containment.',
                'Same-owner terminals do not establish independent trust or execution/source authenticity.'])
