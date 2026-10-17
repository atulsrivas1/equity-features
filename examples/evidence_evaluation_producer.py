"""Controlled EQ117 fixture preparation and two independent arm writers.

Only this producer and the separate scorer know injected case identities.
The observer never imports this module or receives the private producer seed.
"""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import time
from typing import Any

import equity_feature_agent_evidence as events
import equity_feature_agent_ledger as ledger
import equity_feature_contracts as contracts
from equity_feature_bundles import PublicationDeclaration, read_bundle, write_bundle
from equity_feature_diagnostics import DecisionContext, DiagnosticPolicy, KnowledgeCheck, evaluate_diagnostics
from equity_feature_evidence import canonical_content, fingerprint_batch
from equity_feature_explanations import encode_explanation, explain_result
from equity_features.session import compute_trades


def _module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Dataclasses resolve their defining module through sys.modules.
    import sys
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_PILOT: Any = None
_RESEARCH: Any = None


def pilot_module() -> Any:
    global _PILOT, _RESEARCH
    if _PILOT is None:
        _PILOT = _module('_eq117_controlled_pilot', Path(__file__).with_name('evidence_pilot.py'))
        _RESEARCH = _PILOT.research_module()
    return _PILOT


def prepare(seed: Path, case_id: str) -> dict[str, Any]:
    """One actual shared computation per pair, explicitly outside arm timers."""
    assert not seed.exists()
    pilot = pilot_module()
    oracle = pilot.oracles()
    case = next(x for x in oracle['cases'] if x['id'] == case_id)
    research = _RESEARCH
    start = time.perf_counter_ns()
    cfg, batch, golden = research.fixture(case_id == 'P02')
    result = compute_trades(batch, cfg, entity=contracts.EntityKey('A', 'S'))
    assert result == golden
    receipt = pilot._receipt(cfg, batch, result)
    explanation = encode_explanation(explain_result(result, receipt, cfg,
        entity=contracts.EntityKey('A', 'S'), feature_id='session.trade.count', evidence_limit=16))
    strict = pilot.strict_projection(evaluate_diagnostics(
        DecisionContext('demo', contracts.EntityKey('A', 'S'), cfg.availability),
        DiagnosticPolicy('eq116-known-rows', 'strict', 'deny'), tuple(KnowledgeCheck(
            'known-' + str(i + 1), 'trades:' + row_id, stamp, content=fingerprint_batch(batch))
            for i, (row_id, stamp) in enumerate(zip(
                next(x.values for x in batch.columns if x.name == 'event_id'),
                next(x.values for x in batch.columns if x.name == 'known_at_ns'), strict=True)))))
    assert strict == oracle['strict_reports']['future' if case_id == 'P02' else 'clean']
    declaration = PublicationDeclaration('synthetic', 'Fixed caller-created synthetic research example', 'caller_owned')
    full = write_bundle(receipt, cfg, result, (('trades', batch),), declaration)
    visible = write_bundle(receipt, cfg, result, () if case_id == 'P05' else (('trades', batch),), declaration)
    if case_id == 'P07':
        visible = pilot._corrupt(visible)
    seed.mkdir()
    with (seed / 'producer-bundle.zip').open('xb') as output:
        output.write(full)
    with (seed / 'visible-bundle.zip').open('xb') as output:
        output.write(visible)
    reports = dict(strict=strict, advisory=research.expected_reports(case_id == 'P02')[2].decode('ascii'),
                   explanation=explanation.decode('ascii'))
    facts = dict(schema='eq117.producer.v1', case_id=case_id, narrative=case['narrative'],
        retained_input=case_id != 'P05', prefix_count=7 if case_id == 'P06' else 8,
        reports=reports, initial_calculator_calls=1,
        original_native_result=json.loads(canonical_content(result)))
    with (seed / 'facts.json').open('xb') as output:
        output.write(pilot.encoded(facts, lf=True))
    end = time.perf_counter_ns()
    return dict(start_ns=start, end_ns=end, duration_ns=end-start, actual_calculator_calls=1,
                seed_map={p.name: dict(bytes=p.stat().st_size, sha256=pilot.digest(p.read_bytes())) for p in seed.iterdir()})


def record(seed: Path, destination: Path, arm: str, trial_id: str) -> None:
    """All arm-specific decode/serialization/storage work is inside record timing."""
    assert arm in ('ordinary_log', 'evidence_ledger') and not destination.exists()
    pilot = pilot_module()
    facts = pilot.parsed((seed / 'facts.json').read_bytes(), lf=True)
    bundle = read_bundle((seed / 'producer-bundle.zip').read_bytes())
    batch = bundle.inputs[0].batch
    assert batch is not None
    retained = (('trades', batch),) if facts['retained_input'] else ()
    research = _RESEARCH
    # Producer may use the original fixed workflow; generic observer may not.
    assessment = research.assess(bundle.configuration, retained, bundle.result,
        pilot.encode_receipt(bundle.receipt), facts['reports']['explanation'].encode('ascii'),
        facts['reports']['advisory'].encode('ascii'), facts['narrative'])
    case = dict(id=facts['case_id'], narrative=facts['narrative'])
    destination.mkdir()
    if arm == 'ordinary_log':
        rows = pilot._plain(case, bundle.configuration, batch, bundle.result,
            pilot.encode_receipt(bundle.receipt), facts['reports']['strict'], assessment)
        original = pilot.encoded(rows, lf=True)
        terminal = dict(record_count=len(rows), byte_length=len(original), digest=pilot.digest(original))
        with (destination / 'plain-log.json').open('xb') as output:
            output.write(pilot.encoded(rows[:facts['prefix_count']], lf=True))
    else:
        rows = pilot._events(case, bundle.configuration, batch, bundle.result,
            pilot.encode_receipt(bundle.receipt), pilot.encoded(facts['reports']['strict']), assessment)
        terminal = dict(chain_id=rows[-1].chain_id, sequence=len(rows), head_hash=events.event_digest(rows[-1]))
        store = ledger.Ledger.create(str((destination / 'ledger.sqlite').resolve()), rows[0].chain_id)
        try:
            checkpoint = ledger.Checkpoint(rows[0].chain_id, 0, '0' * 64)
            for event in rows[:facts['prefix_count']]:
                checkpoint = store.append(event, expected=checkpoint)
        finally:
            store.close()
        with (destination / 'events.json').open('xb') as output:
            output.write(pilot.encoded([json.loads(events.encode_event(e)) for e in rows[:facts['prefix_count']]], lf=True))
    common = {'bundle.zip': (seed / 'visible-bundle.zip').read_bytes(),
        'task.json': pilot.encoded(dict(schema='eq117.task.v1', trial_id=trial_id, narrative=facts['narrative']), lf=True),
        'declared-reports.json': pilot.encoded(facts['reports'], lf=True),
        'terminal.json': pilot.encoded(terminal, lf=True)}
    for name, raw in common.items():
        with (destination / name).open('xb') as output:
            output.write(raw)


def export(destination: Path, arm: str) -> None:
    from evidence_evaluation_observer import encoded, parsed, read_file
    if arm == 'ordinary_log':
        raw = encoded(parsed(read_file(destination / 'plain-log.json')))
    else:
        terminal = parsed(read_file(destination / 'terminal.json'))
        expected = ledger.Checkpoint(**terminal)
        store = ledger.Ledger.open(str((destination / 'ledger.sqlite').resolve()))
        try:
            actual = store.verify(expected=expected)
            page = store.export_page(after=0, through=actual.head, limit=8)
            ledger.verify_page(page, start=ledger.Checkpoint(expected.chain_id, 0, '0' * 64), through=actual.head)
            raw = encoded([json.loads(events.encode_event(e)) for e in page.events])
        finally:
            store.close()
    with (destination / 'export.json').open('xb') as output:
        output.write(raw)
