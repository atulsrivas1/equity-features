"""Static checks for the future option/library release plan; no numerical claims."""
from pathlib import Path
import json,re

root=Path(__file__).resolve().parents[1]
plan=json.loads((root/'docs/OPTION_LIBRARY_ROADMAP.json').read_text(encoding='utf-8'))
rows=plan['stories']
assert len(rows)==30
assert {r['id'] for r in rows}=={f'EQ-{i}' for i in range(182,212)}
assert set(plan['releases'])=={'R25','R26','R27','R28','R29'}
earlier=json.loads((root/'docs/EQUITY_EXPANSION_ROADMAP.json').read_text(encoding='utf-8'))['stories']
earlier+=json.loads((root/'docs/EQUITY_COVERAGE_ROADMAP.json').read_text(encoding='utf-8'))['stories']
known={f'EQ-{i:03}' for i in range(1,136)}-{'EQ-094'}
graph={r['id']:r['dependencies'] for r in earlier+rows}
assert 'EQ-084' in graph['EQ-210'] and 'EQ-094' not in graph['EQ-210'], 'Scoped service is EQ084; EQ094 remains retired'
known|=set(graph)
for release,start,end in [('R25',182,188),('R26',188,194),('R27',194,201),('R28',201,207),('R29',207,212)]:
    selected=[r for r in rows if r['release']==release]
    assert {r['id'] for r in selected}=={f'EQ-{i}' for i in range(start,end)}
    text=(root/f'docs/{release}_RELEASE_PLAN.md').read_text(encoding='utf-8')
    assert 'Backlog' in text
    for r in selected:assert r['url'] in text and r['id'] in (root/'docs/BACKLOG.md').read_text(encoding='utf-8')
    if release!='R29':
        assert any(r['layer']=='I/O' for r in selected)
        assert any(r['layer']=='workers' for r in selected)
    assert any(r['layer']=='release acceptance' for r in selected)
def visit(key,path):
    assert key not in path,path+[key]
    for dep in graph.get(key,[]):
        assert dep in known and dep!='EQ-094',dep
        if dep in graph:visit(dep,path+[key])
for r in rows:
    assert r['scope'] and r['validation'] and r['status']=='Backlog'
    assert re.fullmatch(r'https://github.com/atulsrivas1/equity-features/issues/\d+',r['url'])
    visit(r['id'],[])
# Exposure/volatility admission does not impose a blanket dependency on the other release.
assert not any(dep in {f'EQ-{i}' for i in range(194,201)} for r in rows if r['release']=='R28' for dep in r['dependencies'])
assert not any(dep in {f'EQ-{i}' for i in range(201,207)} for r in rows if r['release']=='R27' for dep in r['dependencies'])
print('30 option/library stories, five releases, I/O-worker-acceptance coverage and complete cross-roadmap dependency DAG verified; no numerical acceptance.')
