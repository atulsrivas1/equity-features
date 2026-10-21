"""Check option planning allocation and optionally its private source ledger.

This verifies finite planning accounting, not numerical or legacy parity.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re


def dependency_graph(plan: dict, equity: dict) -> dict[str, set[str]]:
    graph = {s['id']: set(s['dependencies']) for s in plan['stories']}
    for rel in equity['releases']:
        for s in rel['existing_stories']:
            graph.setdefault(s['story'], set()).update(s['existing_dependencies'])
        for task in rel['proposed_tasks']:
            graph.setdefault(task['planning_key'], set()).update(task.get('dependencies', []))
        graph.setdefault(rel['acceptance_gate'], set()).update(rel['release_gate_additional_dependencies'])
        if rel.get('common_composition_dependency'):
            for s in rel['existing_stories']:
                graph[s['story']].add(rel['common_composition_dependency'])
    for amendment in equity['dependency_amendments']:
        edges = graph.setdefault(amendment['story'], set())
        edges.difference_update(amendment['remove'])
        edges.update(amendment['add'])
    return graph


def assert_acyclic(graph: dict[str, set[str]]) -> None:
    visiting, done = set(), set()
    def visit(node):
        assert node not in visiting, f'Dependency cycle at {node}'
        if node in done:
            return
        visiting.add(node)
        for dep in graph.get(node, []):
            visit(dep)
        visiting.remove(node)
        done.add(node)
    for sid in graph:
        visit(sid)


def check(root: Path, source: Path | None = None, ledger_path: Path | None = None) -> dict:
    plan = json.loads((root / 'docs/plans/option-delivery-replan.json').read_text(encoding='utf-8'))
    assert plan['planning_only'] and plan['preserve_equity_and_r18']
    assert plan['governance_issue'] == 572
    assert plan['option_implementation_requires'] == ['EQ-141', 'EQ-146', 'published_option_plan', 'reviewed_story_contracts']
    assert [r['id'] for r in plan['releases']] == [f'R{i}' for i in range(25, 30)]
    assert {(r['epic_issue'], r['milestone_number']) for r in plan['releases']} == {(526,29),(533,30),(540,31),(548,32),(555,33)}
    stories = {s['id']: s for s in plan['stories']}
    assert len(stories) == len(plan['stories']) == 36
    assert set(stories) == {f'EQ-{i}' for i in range(182,212)} | {f'EQ-{i}' for i in range(214,220)}
    assert not {'EQ-212','EQ-213'} & stories.keys(), 'EF1 ownership must be preserved'
    allocated = [s for r in plan['releases'] for s in r['stories']]
    assert Counter(allocated) == Counter(stories.keys())
    for r in plan['releases']:
        assert set(r['tracks']) == {'libraries','io','workers'}
        assert not any(r[k] for k in ['standalone_setup_release','api_required','product_ui_required'])
        assert r['contract_story'] in r['stories'] and r['acceptance_gate'] in r['stories']
        assert r['integration_story'] in r['stories'] and r['demo'] and r['parallel_after']
        assert set(s for t in r['tracks'].values() for s in t['stories']) <= set(r['stories'])
        for t in r['tracks'].values():
            assert t['stories'] and t['repository'] in {p['repository'] for p in plan['repositories']}
        for sid in r['stories']:
            s=stories[sid]
            assert s['release']==r['id'] and s['scope'] and s['validation'] and s['points']>0
            assert 'EQ-094' not in s['dependencies']
    assert 'EQ-084' not in stories['EQ-210']['dependencies'], 'Optional API must not gate local release'
    assert {'EQ-214'} <= set(stories['EQ-186']['dependencies'])
    assert {'EQ-216','EQ-217','EQ-218','EQ-219'} <= set(stories['EQ-211']['dependencies'])
    # Add equity allocation dependencies to catch backwards cross-plan cycles.
    equity=json.loads((root/'docs/plans/equity-delivery-replan.json').read_text(encoding='utf-8'))
    graph=dependency_graph(plan,equity)
    assert_acyclic(graph)
    # Independent adversarial control: an equity -> option back-edge must be
    # rejected because the option history story already consumes equity RV.
    assert 'EQ-154' in graph['EQ-197']
    adversarial_equity=deepcopy(equity)
    producer=next(s for r in adversarial_equity['releases'] for s in r['existing_stories'] if s['story']=='EQ-154')
    producer['existing_dependencies'].append('EQ-197')
    cyclic=dependency_graph(plan,adversarial_equity)
    try:
        assert_acyclic(cyclic)
    except AssertionError as error:
        assert 'Dependency cycle' in str(error)
    else:
        raise AssertionError('Cross-plan back-edge was not rejected')
    counts=plan['catalogue_accounting']
    assert sum(r['count'] for r in counts)==plan['catalogue_records']==2497
    assert plan['command_records']==296 and plan['named_option_feature_records']==26
    assert sum(r['count'] for r in counts if r['namespace']=='option_v1' and r['kind']=='feature')==26
    for namespace,kind,count in [('option_v1','scanner',111),('option_v1','watchlist',12),('option_v2','scanner',25),('flow','screen',11),('strategy_intraday','strategy',11),('strategy_eod','profile_direction_expiry',240),('strategy_meta','meta_score',5)]:
        assert sum(r['count'] for r in counts if (r['namespace'],r['kind'])==(namespace,kind))==count
    assert all(r['story'] in stories or r['story'] in graph or re.fullmatch(r'EQ-\d{3}',r['story']) for r in counts)
    docs=[root/'docs/OPTION_DELIVERY_REPLAN.md',root/'docs/OPTION_MATRIX_COVERAGE.md',*(root/'docs/options').glob('*_DELIVERY_PLAN.md')]
    assert len(docs)==7
    for path in docs:
        text=path.read_text(encoding='utf-8')
        assert not re.search(r'(?<![A-Za-z])[A-Za-z]:[\\/]',text), f'Private path in {path}'
        for link in re.findall(r'\]\(([^)]+)\)',text):
            if '://' not in link and not link.startswith('#'):
                assert (path.parent/link.split('#')[0]).is_file(), (path,link)
    if source is not None:
        assert ledger_path is not None
        for name, expected in plan['source_hashes'].items():
            assert hashlib.sha256((source/name).read_bytes()).hexdigest()==expected, name
        raw=json.loads((source/'CALCULATION_CATALOG.json').read_text(encoding='utf-8'))
        ledger=json.loads(ledger_path.read_text(encoding='utf-8'))
        key=lambda r:(r['namespace'],r['kind'],r['id'])
        assert Counter(map(key,raw['catalog']))==Counter(map(key,ledger['catalogue']))
        assert all(r['library'] and r['module'] and r['story'] and r['qualification'] for r in ledger['catalogue'])
        master=json.loads((source/'MASTER_MATRIX.json').read_text(encoding='utf-8'))
        assert {r['worker'] for r in ledger['commands']}=={r.get('worker',r.get('name')) for r in master['workers']}
        assert len(ledger['crosswalk'])==16
        assert {r['id'] for r in ledger['crosswalk']}=={r['id'] for r in json.loads((source/'PRODUCT_LIBRARY_CROSSWALK.json').read_text(encoding='utf-8'))}
    return dict(result='PASS',releases=5,stories=36,catalogue_records=2497,commands=296,private_source_checked=source is not None,qualification='Planning accounting only')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path)
    parser.add_argument('--ledger',type=Path)
    args=parser.parse_args()
    print(json.dumps(check(Path(__file__).resolve().parents[1],args.source,args.ledger),sort_keys=True))
