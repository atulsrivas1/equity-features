"""Validate the future coverage extension separately from historical plan gates."""
from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
plan=json.loads((root/'docs/EQUITY_COVERAGE_ROADMAP.json').read_text(encoding='utf-8'))
rows=plan['stories']
assert len(rows)==18
assert {r['id'] for r in rows}=={f'EQ-{i}' for i in range(164,182)}
assert set(plan['releases'])=={'R22','R23','R24'}
assert plan['governance']['number']==502
graph={r['id']:r['dependencies'] for r in rows}
assert graph['EQ-174']==['EQ-164','EQ-091'], 'Endpoint labels are EQ091, not GitHub issue103'
assert 'EQ-090' in graph['EQ-176'] and 'EQ-102' not in graph['EQ-176'], 'Generic scanner is EQ090, not issue102'
for release,start,end in [('R22',164,170),('R23',170,176),('R24',176,182)]:
    assert {r['id'] for r in rows if r['release']==release}=={f'EQ-{i}' for i in range(start,end)}
    text=(root/f'docs/{release}_RELEASE_PLAN.md').read_text(encoding='utf-8')
    for row in [r for r in rows if r['release']==release]:
        assert row['url'] in text
        assert row['id'] in (root/'docs/BACKLOG.md').read_text(encoding='utf-8')
def visit(key,path):
    assert key not in path,path+[key]
    for dep in graph.get(key,[]):
        assert dep.startswith('EQ-') and dep!='EQ-094'
        if dep in graph: visit(dep,path+[key])
for r in rows:
    assert r['scope'] and r['validation'] and r['status']=='Backlog'
    assert r['url'].startswith('https://github.com/atulsrivas1/equity-features/issues/')
    visit(r['id'],[])
for document in [root/'docs/EQUITY_COVERAGE_RELEASE_PLAN.md',*(root/f'docs/{r}_RELEASE_PLAN.md' for r in plan['releases'])]:
    text=document.read_text(encoding='utf-8')
    assert 'Backlog' in text
print('18 future story IDs, three release allocations, links, scope/validation, retired-ID exclusion and acyclic dependencies verified.')
