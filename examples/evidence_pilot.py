"""Eight fixed synthetic comparisons; trusted local orchestration, never a sandbox.

Package calculations remain pure. This outer example owns files and SQLite;
same-owner terminals and model declarations do not authenticate execution.
"""
from __future__ import annotations

import hashlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import stat
import sys
from typing import Any, cast
import zipfile

import equity_feature_contracts as c
import equity_feature_agent_evidence as a
import equity_feature_agent_ledger as ledger
from equity_feature_evidence import (canonical_content, fingerprint_config,
    fingerprint_batch, fingerprint_result, InputFingerprint, make_content_receipt,
    EnvironmentDeclaration, PackageVersion, ExecutionClaim, EvidenceDisclosure,
    encode_receipt)
from equity_feature_explanations import explain_result, encode_explanation
from equity_feature_diagnostics import (DecisionContext, DiagnosticPolicy,
    KnowledgeCheck, evaluate_diagnostics)
from equity_feature_bundles import (PublicationDeclaration, write_bundle,
    read_bundle, BundleError)

CASE_IDS = tuple('P%02d' % i for i in range(1, 9))
ARMS = ('ordinary_log', 'evidence_ledger')
FORMS = ('wheel-light', 'wheel-compute', 'sdist-light', 'sdist-compute')
FILES = ('bundle.zip', 'plain-log.json', 'events.json', 'ledger.sqlite',
         'terminals.json', 'reports.json', 'observations.json', 'completion.json')
CAPS = dict(zip(FILES, (1048576, 32768, 131072, None, 16384, 65536, 16384, 16384), strict=True))
ORACLE_SHA256 = '30aec747d0483ae3e95faabf704fbd37d2fa8cd40882eb3ba1c2518e6932a98a'


class PilotError(ValueError):
    """Fixed diagnostic; never echo a caller path or exception payload."""
    def __init__(self, code: str = 'invalid_input') -> None:
        self.code = code if code in ('invalid_input', 'integrity_mismatch',
            'limit_exceeded', 'incomplete', 'existing_output') else 'invalid_input'
        super().__init__('Evidence pilot rejected: ' + self.code)


def require(ok: bool, code: str = 'invalid_input') -> None:
    if not ok:
        raise PilotError(code) from None


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def encoded(value: Any, *, lf: bool = False) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode('ascii') + (b'\n' if lf else b'')


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in out)
        out[key] = value
    return out


def parsed(raw: bytes, *, lf: bool = False) -> Any:
    require(type(raw) is bytes and raw.isascii())
    require(len(raw) <= 131072, 'limit_exceeded')
    try:
        value = json.loads(raw, object_pairs_hook=_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(PilotError()))
        require(encoded(value, lf=lf) == raw)
        return value
    except (ValueError, RecursionError, OverflowError, UnicodeError):
        raise PilotError() from None


def shape(value: Any, keys: tuple[str, ...]) -> dict[str, Any]:
    require(type(value) is dict and set(value) == set(keys))
    return cast(dict[str, Any], value)


def research_module() -> Any:
    """Load only the fixed sibling outer example, never an uploaded module."""
    name = '_eq116_fixed_research'
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name('agent_research.py'))
        require(spec is not None and spec.loader is not None)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def oracles() -> dict[str, Any]:
    fixed = Path(__file__).with_name('EQ116_ORACLES.json')
    if not fixed.is_file():
        fixed = Path(__file__).resolve().parents[1] / 'docs/stories/EQ116_ORACLES.json'
    raw = fixed.read_bytes()
    require(digest(raw) == ORACLE_SHA256, 'integrity_mismatch')
    return cast(dict[str, Any], json.loads(raw, object_pairs_hook=_pairs))


def fp(value: Any) -> dict[str, Any]:
    return {key: getattr(value, key) for key in ('domain', 'digest', 'byte_length',
        'schema_version', 'canonicalization', 'algorithm')}


def native_data(value: Any) -> Any:
    """Translate independent literal tags to the accepted content JSON shape."""
    if type(value) is list:return [native_data(x) for x in value]
    if type(value) is not dict:return value
    if set(value) == {'int'}:return int(value['int'])
    if set(value) == {'enum', 'value'}:return value['value']
    if set(value) == {'fields', 'record'}:
        return dict(type=value['record'], fields={k: native_data(x) for k, x in value['fields'].items()})
    return {k: native_data(x) for k, x in value.items()}


def strict_projection(report: Any) -> dict[str, Any]:
    context = report.context
    availability = context.availability
    findings = []
    for finding in report.findings:
        row = {key: getattr(finding, key) for key in ('check_id', 'subject_id', 'kind',
            'status', 'severity', 'assessed', 'unknown_prerequisites', 'age_ns')}
        row.update(content=None if finding.content is None else fp(finding.content),
                   reasons=list(finding.reasons))
        findings.append(row)
    out = {key: getattr(report, key) for key in ('schema_version', 'requested_count',
        'passed_count', 'failed_count', 'unknown_count', 'assessed_count',
        'unknown_prerequisite_count', 'admission', 'source_authenticated',
        'historical_acquisition_verified')}
    out.update(context=dict(namespace=context.namespace,
        entity=dict(instrument_id=context.entity.instrument_id, session_id=context.entity.session_id),
        availability={key: getattr(availability, key) for key in ('market_cutoff_ns',
            'knowledge_cutoff_ns', 'evaluation_ns', 'mode', 'reconstruction_reason')}),
        policy={key: getattr(report.policy, key) for key in ('policy_id', 'mode', 'unknown_action')},
        findings=findings, not_requested=list(report.not_requested))
    return out


def _receipt(cfg: Any, batch: Any, result: Any) -> Any:
    return make_content_receipt(result, cfg, (('trades', batch),),
        EnvironmentDeclaration('CPython', '3.12', 'synthetic-qualification', (
            PackageVersion('equity-feature-contracts', '0.0.4a5'),
            PackageVersion('equity-features', '0.0.4a6'))),
        ExecutionClaim(), EvidenceDisclosure('not_supplied', 0))


def _payload(kind: a.PayloadKind, raw: bytes) -> a.PayloadReference:
    return a.PayloadReference(kind, digest(raw), len(raw), len(raw), a.DisclosureState.RETAINED_COMPLETE)


def _events(case: dict[str, Any], cfg: Any, batch: Any, result: Any,
            receipt: bytes, strict_raw: bytes, assessment: Any) -> tuple[a.EventRecord, ...]:
    events: list[a.EventRecord] = []
    absent = a.TimeDeclaration(None, None, None)
    context = a.DecisionContext('demo', 'S', cfg.availability)
    actor = a.ActorDeclaration('eq116-pilot', a.ActorKind.SOFTWARE)
    def add(subject: Any) -> a.EventReference:
        sequence = len(events) + 1
        value = a.EventRecord('pilot:' + case['id'], sequence, case['id'] + ':e' + str(sequence),
            actor, absent, absent, '0' * 64 if not events else a.event_digest(events[-1]), subject)
        events.append(value)
        return a.event_reference(value)
    request = add(a.RequestSubject(case['id'], 'inspect supplied trade count', context))
    missing = case['id'] == 'P08'
    add(a.ModelSubject(None if missing else 'synthetic', None if missing else 'fixture-model',
        None if missing else 'v1', a.ModelIdentityState.NOT_SUPPLIED if missing else a.ModelIdentityState.DECLARED))
    call = add(a.ToolCallSubject(request, 'compute_trades', '0.0.4a4',
        a.ArgumentSet(a.DisclosureState.RETAINED_COMPLETE, 2, (
            a.Argument('configuration', fingerprint_config(cfg).digest),
            a.Argument('input', fingerprint_batch(batch).digest)))))
    result_ref = add(a.ToolResultSubject(call, a.ToolOutcome.SUCCEEDED,
        _payload(a.PayloadKind.TOOL_RESULT, canonical_content(result))))
    check = add(a.ToolCallSubject(request, 'evaluate_diagnostics', '0.1.0a1',
        a.ArgumentSet(a.DisclosureState.RETAINED_COMPLETE, 2, (
            a.Argument('input', fingerprint_batch(batch).digest),
            a.Argument('policy_id', 'eq116-known-rows')))))
    add(a.ToolResultSubject(check, a.ToolOutcome.SUCCEEDED,
        _payload(a.PayloadKind.DIAGNOSTIC_REPORT, strict_raw)))
    read = add(a.FeatureReadSubject(result_ref, _payload(a.PayloadKind.EXECUTION_RECEIPT, receipt),
        fingerprint_config(cfg), (InputFingerprint('trades', 'trades', fingerprint_batch(batch)),),
        fingerprint_result(result), ('session.trade.count',), context))
    add(a.DecisionSubject(request, (read,), a.DecisionAction(assessment.decision.lower()), assessment.reason_code))
    require(len(events) == 8)
    return tuple(events)


def _plain(case: dict[str, Any], cfg: Any, batch: Any, result: Any,
           receipt: bytes, strict: dict[str, Any], assessment: Any) -> list[dict[str, Any]]:
    """Independent writer from shared facts; never consumes event or ledger data."""
    missing = case['id'] == 'P08'
    config_fp, input_fp, output_fp = fp(fingerprint_config(cfg)), fp(fingerprint_batch(batch)), fp(fingerprint_result(result))
    facts = [dict(request_key=case['id'], objective='inspect supplied trade count',
        narrative=case['narrative'], context=strict['context']),
        dict(provider=None if missing else 'synthetic', model=None if missing else 'fixture-model',
             version=None if missing else 'v1', identity_state='not_supplied' if missing else 'declared'),
        dict(request_sequence=1, tool='compute_trades', version='0.0.4a4', configuration=config_fp, input=input_fp),
        dict(call_sequence=3, outcome='succeeded', output=output_fp, payload=canonical_content(result).decode('ascii')),
        dict(request_sequence=1, tool='evaluate_diagnostics', version='0.1.0a1', input=input_fp, policy=strict['policy']),
        dict(call_sequence=5, outcome='succeeded', report=strict),
        dict(result_sequence=4, configuration=config_fp, input=input_fp, output=output_fp,
             receipt=receipt.decode('ascii'), feature_ids=['session.trade.count'], context=strict['context']),
        dict(request_sequence=1, feature_read_sequences=[7], action=assessment.decision, reason_code=assessment.reason_code)]
    kinds = ('request', 'model', 'calculation_call', 'calculation_result', 'diagnostic_call',
             'diagnostic_result', 'feature_read', 'decision')
    return [dict(schema='eq116.plain.v1', case_id=case['id'], sequence=i + 1, kind=kinds[i], facts=value)
            for i, value in enumerate(facts)]


def _archive(raw: bytes) -> dict[str, bytes]:
    require(len(raw) <= 1048576, 'limit_exceeded')
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            infos = archive.infolist()
            require(len(infos) <= 16 and len({x.filename for x in infos}) == len(infos))
            require(sum(x.file_size for x in infos) <= 262144, 'limit_exceeded')
            allowed = {'manifest.json', 'receipt.json', 'configuration.json', 'result.json', 'inputs/000.json'}
            for info in infos:
                require(info.orig_filename == info.filename and info.filename in allowed)
                require(info.compress_type == zipfile.ZIP_STORED and not info.is_dir())
                require(stat.S_IFMT(info.external_attr >> 16) in (0, stat.S_IFREG))
                require(not info.flag_bits & 1)
            return {x.filename: archive.read(x) for x in infos}
    except (zipfile.BadZipFile, RuntimeError, OSError):
        raise PilotError() from None


def _corrupt(raw: bytes) -> bytes:
    entries = _archive(raw)
    value = json.loads(entries['result.json'])
    # Change the first literal count value only; manifest and receipt stay stale.
    require(value['value']['fields']['values'][0]['fields']['values'] == [3])
    value['value']['fields']['values'][0]['fields']['values'] = [4]
    entries['result.json'] = encoded(value)
    out = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(raw)) as original:
        with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_STORED) as archive:
            for info in original.infolist():
                # Preserve every accepted language field (1980 DOS epoch,
                # creator/extractor versions, mode100600, flags, no extras).
                archive.writestr(copy.copy(info), entries[info.filename])
    return out.getvalue()


def record(root: Path) -> None:
    """Actual local producer. Any failure leaves an explicitly incomplete root."""
    require(type(root) is Path or isinstance(root, Path))
    require(not root.exists(), 'existing_output')
    oracle = oracles()
    research = research_module()
    from equity_features.session import compute_trades
    root.mkdir()
    for case in oracle['cases']:
        directory = root / case['id'];directory.mkdir()
        future = case['id'] == 'P02'
        cfg, batch, golden = research.fixture(future)
        actual = compute_trades(batch, cfg, entity=c.EntityKey('A', 'S'))
        require(actual == golden, 'integrity_mismatch')
        require(json.loads(canonical_content(actual))['value'] == native_data(oracle['future_native_result' if future else 'clean_native_result']), 'integrity_mismatch')
        receipt = _receipt(cfg, batch, actual);receipt_raw = encode_receipt(receipt)
        explanation = encode_explanation(explain_result(actual, receipt, cfg,
            entity=c.EntityKey('A', 'S'), feature_id='session.trade.count', evidence_limit=16))
        advisory = research.expected_reports(future)[2]
        strict = strict_projection(evaluate_diagnostics(DecisionContext('demo', c.EntityKey('A', 'S'), cfg.availability),
            DiagnosticPolicy('eq116-known-rows', 'strict', 'deny'), tuple(KnowledgeCheck(
                'known-' + str(i + 1), 'trades:t' + str(i + 1), known,
                content=fingerprint_batch(batch)) for i, known in enumerate((110, 130, 211 if future else 210)))))
        require(strict == oracle['strict_reports']['future' if future else 'clean'], 'integrity_mismatch')
        retained = () if case['id'] == 'P05' else (('trades', batch),)
        assessment = research.assess(cfg, retained, actual, receipt_raw, explanation, advisory, case['narrative'])
        events = _events(case, cfg, batch, actual, receipt_raw, encoded(strict), assessment)
        plain = _plain(case, cfg, batch, actual, receipt_raw, strict, assessment)
        all_plain = encoded(plain, lf=True)
        terminal = dict(schema='eq116.terminals.v1', case_id=case['id'], expected_count=8,
            ledger=dict(chain_id='pilot:' + case['id'], sequence=8, head_hash=a.event_digest(events[-1])),
            ordinary_log=dict(record_count=8, byte_length=len(all_plain), digest=digest(all_plain)))
        prefix = 7 if case['id'] == 'P06' else 8
        store = ledger.Ledger.create(str((directory / 'ledger.sqlite').resolve()), 'pilot:' + case['id'])
        try:
            checkpoint = ledger.Checkpoint('pilot:' + case['id'], 0, '0' * 64)
            for event in events[:prefix]:
                checkpoint = store.append(event, expected=checkpoint)
        finally:
            store.close()
        bundle = write_bundle(receipt, cfg, actual, retained,
            PublicationDeclaration('synthetic', 'Fixed caller-created synthetic research example', 'caller_owned'))
        if case['id'] == 'P07':bundle = _corrupt(bundle)
        payloads = {'bundle.zip': bundle, 'plain-log.json': encoded(plain[:prefix], lf=True),
            'events.json': encoded([json.loads(a.encode_event(e)) for e in events[:prefix]], lf=True),
            'terminals.json': encoded(terminal, lf=True),
            'reports.json': encoded(dict(schema='eq116.reports.v1', case_id=case['id'], strict=strict,
                advisory=advisory.decode('ascii'), explanation=explanation.decode('ascii')), lf=True),
            'observations.json': encoded(dict(schema='eq116.producer.v1', case_id=case['id'], narrative=case['narrative'],
                model_state='not_supplied' if case['id'] == 'P08' else 'declared', narrative_status=assessment.narrative_status,
                decision=assessment.decision, reason_code=assessment.reason_code, input_retained=bool(retained),
                initial_calculator_calls=1, initial_diagnostic_calls=1, strict_admission=strict['admission'],
                source_authenticated=False, execution_verified=False), lf=True)}
        require(sum(map(len, payloads.values())) + 16384 <= 1048576, 'limit_exceeded')
        for name, raw in payloads.items():
            cap = CAPS[name];assert cap is not None
            require(len(raw) <= cap, 'limit_exceeded')
            with (directory / name).open('xb') as output:output.write(raw)
        files = {name: dict(bytes=(directory / name).stat().st_size,
            digest=digest((directory / name).read_bytes())) for name in FILES[:-1]}
        completion = encoded(dict(schema='eq116.complete.v1', case_id=case['id'], files=files), lf=True)
        require(len(completion) <= 16384, 'limit_exceeded')
        with (directory / 'completion.json').open('xb') as output:output.write(completion)


def _read(path: Path, cap: int) -> bytes:
    require(stat.S_ISREG(path.lstat().st_mode))
    with path.open('rb') as source:raw = source.read(cap + 1)
    require(len(raw) <= cap, 'limit_exceeded')
    return raw


def _load(directory: Path, case_id: str) -> dict[str, bytes]:
    require({x.name for x in directory.iterdir()} == set(FILES), 'incomplete')
    complete = parsed(_read(directory / 'completion.json', 16384), lf=True)
    shape(complete, ('schema', 'case_id', 'files'))
    require(complete['schema'] == 'eq116.complete.v1' and complete['case_id'] == case_id)
    shape(complete['files'], FILES[:-1])
    loaded = {}
    for name in FILES[:-1]:
        desc = shape(complete['files'][name], ('bytes', 'digest'))
        require(type(desc['bytes']) is int and desc['bytes'] >= 0)
        require(type(desc['digest']) is str and len(desc['digest']) == 64)
        cap = CAPS[name]
        if name == 'ledger.sqlite':
            # A physical SQLite bound is deliberately not claimed. Stream its
            # completion identity without retaining an unbounded copy in memory.
            require(stat.S_ISREG((directory / name).lstat().st_mode))
            count = 0;hasher = hashlib.sha256()
            with (directory / name).open('rb') as source:
                while chunk := source.read(65536):
                    count += len(chunk);hasher.update(chunk)
            require(count == desc['bytes'] and hasher.hexdigest() == desc['digest'], 'integrity_mismatch')
        else:
            assert cap is not None
            raw = _read(directory / name, cap)
            require(desc == dict(bytes=len(raw), digest=digest(raw)), 'integrity_mismatch')
            loaded[name] = raw
    require(sum(map(len, loaded.values())) + len(encoded(complete, lf=True)) <= 1048576, 'limit_exceeded')
    return loaded


def _replay(bundle: Any) -> tuple[str, int]:
    """Count actual fixed public calculator entries, rather than trusting a report."""
    from equity_feature_bundles.replay import replay_bundle
    try:
        import equity_features.session as session
    except ImportError:
        report = replay_bundle(bundle)
        require(report.calculation_count == 0)
        return report.status, 0
    original = session.compute_trades
    calls = 0
    def counted(*args: Any, **kwargs: Any) -> Any:
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)
    session.compute_trades = counted
    try:
        report = replay_bundle(bundle)
    finally:
        session.compute_trades = original
    require(report.calculation_count == calls, 'integrity_mismatch')
    return report.status, calls


def read_case(directory: Path, case_id: str, arm: str, form: str) -> dict[str, Any]:
    require(case_id in CASE_IDS and arm in ARMS and form in FORMS)
    oracle = oracles();case = next(x for x in oracle['cases'] if x['id'] == case_id)
    raw = _load(directory, case_id)
    _archive(raw['bundle.zip'])
    observed = dict(schema='eq116.reader.v1', case_id=case_id, arm=arm, form=form,
        load='verified', consistency=None, anchor=None, retention=None, narrative_status=None,
        decision=None, model_state=None, strict_admission=None, replay_status='refused_before_calculator',
        calculator_calls=0, source_authenticated=False, execution_verified=False)
    try:
        bundle = read_bundle(raw['bundle.zip'])
    except BundleError as exc:
        require(case_id == 'P07' and exc.code == 'integrity_mismatch', 'integrity_mismatch')
        observed['load'] = 'integrity_mismatch'
        return observed
    require(case_id != 'P07', 'integrity_mismatch')
    future = case_id == 'P02'
    research = research_module()
    cfg, expected_batch, golden = research.fixture(future)
    require(bundle.configuration == cfg and bundle.result == golden, 'integrity_mismatch')
    require(json.loads(canonical_content(bundle.result))['value'] == native_data(oracle['future_native_result' if future else 'clean_native_result']), 'integrity_mismatch')
    require(len(bundle.inputs) == 1 and bundle.inputs[0].role == 'trades' and bundle.inputs[0].input_id == 'trades')
    require(bundle.inputs[0].content == fingerprint_batch(expected_batch), 'integrity_mismatch')
    missing = bundle.inputs[0].batch is None
    require(missing == (case_id == 'P05'))
    if not missing:
        # CanonicalBatch logical identity sorts columns; tuple construction order
        # is not part of the accepted typed-content identity.
        retained_batch = bundle.inputs[0].batch
        assert retained_batch is not None
        require(canonical_content(retained_batch) == canonical_content(expected_batch), 'integrity_mismatch')
    retained = () if missing else (('trades', bundle.inputs[0].batch),)
    receipt_raw = encode_receipt(bundle.receipt)
    reports = parsed(raw['reports.json'], lf=True)
    shape(reports, ('schema', 'case_id', 'strict', 'advisory', 'explanation'))
    require(reports['schema'] == 'eq116.reports.v1' and reports['case_id'] == case_id)
    require(encoded(reports['strict']) == encoded(oracle['strict_reports']['future' if future else 'clean']), 'integrity_mismatch')
    require(type(reports['advisory']) is str and type(reports['explanation']) is str)
    advisory = reports['advisory'].encode('ascii');explanation = reports['explanation'].encode('ascii')
    require(len(encoded(reports['strict'])) <= 16384 and len(advisory) <= 16384 and len(explanation) <= 32768, 'limit_exceeded')
    assessment = research.assess(cfg, retained, bundle.result, receipt_raw, explanation, advisory, case['narrative'])
    producer = parsed(raw['observations.json'], lf=True)
    wanted_producer = dict(schema='eq116.producer.v1', case_id=case_id, narrative=case['narrative'],
        model_state='not_supplied' if case_id == 'P08' else 'declared', narrative_status=assessment.narrative_status,
        decision=assessment.decision, reason_code=assessment.reason_code, input_retained=not missing,
        initial_calculator_calls=1, initial_diagnostic_calls=1, strict_admission=reports['strict']['admission'],
        source_authenticated=False, execution_verified=False)
    require(encoded(producer) == encoded(wanted_producer), 'integrity_mismatch')
    # The literal batch used to check declared identities is NOT supplied to
    # replay when missing. Original-content consistency and retained bytes differ.
    terminal = parsed(raw['terminals.json'], lf=True)
    shape(terminal, ('schema', 'case_id', 'expected_count', 'ledger', 'ordinary_log'))
    require(terminal['schema'] == 'eq116.terminals.v1' and terminal['case_id'] == case_id and type(terminal['expected_count']) is int and terminal['expected_count'] == 8)
    shape(terminal['ledger'], ('chain_id', 'sequence', 'head_hash'))
    shape(terminal['ordinary_log'], ('record_count', 'byte_length', 'digest'))
    full_events = _events(case, cfg, expected_batch, bundle.result, receipt_raw, encoded(reports['strict']), assessment)
    full_plain = _plain(case, cfg, expected_batch, bundle.result, receipt_raw, reports['strict'], assessment)
    complete_plain = encoded(full_plain, lf=True)
    require(encoded(terminal['ledger']) == encoded(dict(chain_id='pilot:' + case_id, sequence=8, head_hash=a.event_digest(full_events[-1]))), 'integrity_mismatch')
    require(encoded(terminal['ordinary_log']) == encoded(dict(record_count=8, byte_length=len(complete_plain), digest=digest(complete_plain))), 'integrity_mismatch')
    count = 7 if case_id == 'P06' else 8
    if arm == 'ordinary_log':
        plain = parsed(raw['plain-log.json'], lf=True)
        require(encoded(plain) == encoded(full_plain[:count]), 'integrity_mismatch')
        anchor = 'matched_terminal' if raw['plain-log.json'] == complete_plain else 'not_covered'
    else:
        values = parsed(raw['events.json'], lf=True)
        require(type(values) is list and len(values) == count)
        events = tuple(a.decode_event(encoded(x)) for x in values)
        require(all(len(a.encode_event(e)) <= 16384 for e in events), 'limit_exceeded')
        require(tuple(a.encode_event(e) for e in events) == tuple(a.encode_event(e) for e in full_events[:count]), 'integrity_mismatch')
        expected_terminal = ledger.Checkpoint(**terminal['ledger'])
        checked = ledger.verify_events(events, chain_id='pilot:' + case_id, expected=expected_terminal)
        store = ledger.Ledger.open(str((directory / 'ledger.sqlite').resolve()))
        try:
            actual = store.verify(expected=expected_terminal)
            require(actual == checked, 'integrity_mismatch')
            page = store.export_page(after=0, through=actual.head, limit=8)
            ledger.verify_page(page, start=ledger.Checkpoint('pilot:' + case_id, 0, '0' * 64), through=actual.head)
            require(tuple(a.encode_event(e) for e in page.events) == tuple(a.encode_event(e) for e in events), 'integrity_mismatch')
        finally:
            store.close()
        for e in events:
            if type(e.subject) is a.ToolResultSubject:
                payload = canonical_content(bundle.result) if e.sequence == 4 else encoded(reports['strict'])
                require(a.verify_payload(e.subject.payload, payload).retained_matched, 'integrity_mismatch')
            elif type(e.subject) is a.FeatureReadSubject:
                require(a.verify_payload(e.subject.receipt, receipt_raw).retained_matched, 'integrity_mismatch')
        anchor = actual.anchor_status.value
    replay_status, calls = _replay(bundle)
    observed.update(consistency='verified', anchor=anchor, retention='missing' if missing else 'complete',
        narrative_status=assessment.narrative_status, decision=assessment.decision,
        model_state=producer['model_state'], strict_admission=reports['strict']['admission'],
        replay_status=replay_status, calculator_calls=calls)
    return observed


def replay(root: Path, form: str) -> list[dict[str, Any]]:
    require(form in FORMS)
    require({x.name for x in root.iterdir()} == set(CASE_IDS), 'incomplete')
    observations = [read_case(root / case_id, case_id, arm, form) for case_id in CASE_IDS for arm in ARMS]
    expected = [x for x in oracles()['reader_expectations'] if x['form'] == form]
    require(encoded(observations) == encoded(expected), 'integrity_mismatch')
    return observations


def main() -> None:
    require(len(sys.argv) in (3, 4))
    if sys.argv[1] == 'record' and len(sys.argv) == 3:
        record(Path(sys.argv[2]).resolve())
        print(encoded(dict(schema='eq116.recorded.v1', cases=list(CASE_IDS))).decode())
    elif sys.argv[1] == 'replay' and len(sys.argv) == 4:
        print(encoded(replay(Path(sys.argv[2]).resolve(), sys.argv[3])).decode())
    else:raise PilotError()


if __name__ == '__main__':
    main()
