"""Independent documentation truth-table arithmetic; no diagnostic implementation."""
from pathlib import Path
import json

KINDS={'market_time','knowledge_time','declared_context','membership','revision','adjustment','freshness'}
FIELDS={
    'market_time':{'open','close','time','convention','include_closing','start'},
    'knowledge_time':{'known'},'declared_context':{'C','K','E','mode'},
    'membership':{'query','scope','selected_kind','history','reference','facts'},
    'revision':{'expected','observed','start','end','query','known'},
    'adjustment':{'expected','observed','expected_unit','observed_unit'},
    'freshness':{'basis','target','observed','tolerance'},
}


def reference(kind, values, context):
    """Independent scalar/interval reference against the frozen policy table."""
    failed=set();unknown=set();missing=0;age=None
    def absent(reason):
        nonlocal missing
        unknown.add(reason);missing+=1
    C,K,E=context['C'],context['K'],context['E']
    if kind=='market_time':
        session=values['open'] is not None and values['close'] is not None
        if not session:absent('missing_session')
        if values['time'] is None:absent('missing_market_fact')
        interval=values['convention']=='completed_interval'
        if interval and values['start'] is None:absent('missing_market_fact')
        if not missing:
            t=values['time'];limit=min(C,values['close'])
            if interval:valid=values['open']<=values['start']<t<=limit
            elif values['convention']=='closing_auction':valid=values['include_closing'] and t==values['close']==C
            else:valid=values['open']<=t<limit
            if not valid:failed.add('market_bound')
    elif kind=='knowledge_time':
        if values['known'] is None:absent('missing_knowledge')
        elif values['known']>K:failed.add('late_knowledge')
    elif kind=='declared_context':
        if values is None:absent('missing_context')
        else:
            for field,expected,reason in (('C',C,'market_cutoff_mismatch'),('K',K,'knowledge_cutoff_mismatch'),('E',E,'evaluation_mismatch')):
                if values[field]!=expected:failed.add(reason)
            if values['mode']!='known_at':failed.add('reconstruction_context')
    elif kind=='membership':
        ref=values['reference'];facts=values['facts'];full=False
        if values['query']>C:failed.add('future_effective_query')
        if ref is None:absent('missing_reference')
        else:
            if not ref['complete']:absent('incomplete_reference')
            full=len(facts)==ref['observed'] and {r[0] for r in facts}==set(range(ref['observed']))
            if not full:absent('incomplete_projection')
        if values['history']!='historical':absent('historical_proof_unknown')
        active=[f for f in facts if f[2]<=values['query'] and (f[3] is None or values['query']<f[3])]
        if len(active)>1:failed.add('ambiguous_membership')
        if not active and ref is not None and ref['complete'] and full and values['history']=='historical':failed.add('membership_absent')
        if any(f[5] is None for f in active):absent('missing_membership_text')
        if any(f[4] is None for f in active):absent('missing_knowledge')
        if any(f[5] is not None and f[5]!=values['scope'] for f in active):failed.add('membership_scope_mismatch')
        if any(f[4] is not None and f[4]>K for f in active):failed.add('late_knowledge')
    elif kind=='revision':
        for field in ('expected','observed'):
            if values[field] is None:absent('missing_revision_identity')
        if values['expected'] is not None and values['observed'] is not None and values['expected']!=values['observed']:failed.add('revision_mismatch')
        if values['start'] is None:absent('missing_effective_start')
        elif not (values['start']<=values['query'] and (values['end'] is None or values['query']<values['end'])):failed.add('outside_effective_interval')
        if values['query']>C:failed.add('future_effective_query')
        if values['known'] is None:absent('missing_knowledge')
        elif values['known']>K:failed.add('late_knowledge')
    elif kind=='adjustment':
        for field in ('expected','observed','expected_unit','observed_unit'):
            if values[field] is None:absent('missing_adjustment')
        for left,right in (('expected','observed'),('expected_unit','observed_unit')):
            if values[left] is not None and values[right] is not None and values[left]!=values[right]:failed.add('adjustment_mismatch')
    elif kind=='freshness':
        if values['observed'] is None:absent('missing_observation')
        elif values['observed']>values['target']:failed.add('future_observation')
        else:
            age=values['target']-values['observed']
            if age>values['tolerance']:failed.add('stale_observation')
    else:raise AssertionError('unknown reference kind')
    status='failed' if failed else 'unknown' if missing else 'passed'
    return {'status':status,'reasons':sorted(failed|unknown),'assessed':missing==0,'unknown_prerequisites':missing,'age_ns':age}


def verify(path):
    data=json.loads(path.read_bytes());assert data['fixture_schema']=='eq101-truth-table:1'
    assert set(data)=={'fixture_schema','context','scope','cases','admission_cases','required_structural_refusals'}
    assert len(data['cases'])==35 and len(data['admission_cases'])==6
    assert {c['kind'] for c in data['cases']}==KINDS
    cases={c['id']:c for c in data['cases']};assert len(cases)==35
    for case in cases.values():
        assert set(case) in ({'id','kind','input','expected'},{'id','kind','input','expected','context'})
        values=case['input']
        assert values is None and case['kind']=='declared_context' or type(values) is dict and set(values)==FIELDS[case['kind']]
        if case['kind']=='membership':
            assert values['selected_kind'] in ('universe_membership','sector_membership')
            assert values['history'] in ('historical','current_only','unknown')
            ref=values['reference'];facts=values['facts']
            assert ref is None or set(ref)=={'observed','complete'} and type(ref['observed']) is int and 0<=ref['observed']<=1024 and type(ref['complete']) is bool
            assert len(facts)<=1024 and all(type(f) is list and len(f)==6 for f in facts)
            assert len({f[0] for f in facts})==len(facts) and len({f[1] for f in facts})==len(facts)
        if case['kind']=='freshness':
            assert values['basis'] in ('market_observation','reference_publication','tool_read')
            assert type(values['tolerance']) is int and 0<=values['tolerance']<(1<<63)
        context=data['context']|case.get('context',{})
        assert all(type(context[k]) is int and -(1<<63)<=context[k]<(1<<63) for k in ('C','K','E'))
        assert context['C']<=context['E'] and context['K']<=context['E']
        expected=case['expected'];assert set(expected)=={'status','reasons','assessed','unknown_prerequisites','age_ns'}
        assert type(expected['assessed']) is bool and type(expected['unknown_prerequisites']) is int
        assert expected['reasons']==sorted(set(expected['reasons']))
        assert expected==reference(case['kind'],case['input'],context),case['id']
    for item in data['admission_cases']:
        assert set(item)=={'id','mode','unknown_action','case_ids','expected'}
        assert item['mode'] in ('advisory','strict') and item['unknown_action'] in ('allow','deny')
        assert len(item['case_ids'])==len(set(item['case_ids']))
        selected=[cases[k]['expected'] for k in item['case_ids']]
        passed=sum(c['status']=='passed' for c in selected);failed=sum(c['status']=='failed' for c in selected);unknown=sum(c['status']=='unknown' for c in selected)
        decision='not_applied' if item['mode']=='advisory' else 'denied' if failed or unknown and item['unknown_action']=='deny' else 'admitted'
        observed={'admission':decision,'requested':len(selected),'passed':passed,'failed':failed,'unknown':unknown,'assessed':sum(c['assessed'] for c in selected),'unknown_prerequisites':sum(c['unknown_prerequisites'] for c in selected)}
        assert observed==item['expected'],item['id']
    assert len(data['required_structural_refusals'])==18
    assert set(data['required_structural_refusals'].values())<={'invalid_schema','unsupported_version','inconsistent_binding','duplicate','limit_exceeded'}
    print('EQ101 independent documentation reference:35check vectors/6admission aggregates verified;18future structural requirements declared, not executed runtime tests.')


if __name__=='__main__':
    verify(Path(__file__).resolve().parents[1]/'docs/stories/EQ-101_TRUTH_TABLE.json')
