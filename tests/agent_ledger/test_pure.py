"""Independent pre-code golden histories and result-construction boundaries."""
from dataclasses import replace, FrozenInstanceError
import hashlib
import json
from pathlib import Path
import unittest
import equity_feature_agent_evidence as a
import equity_feature_agent_ledger as l

ROOT = Path(__file__).resolve().parents[2]
def load(name): return json.loads((ROOT/'docs/stories'/('EQ-107_'+name+'.json')).read_bytes())
def events(): return [a.decode_event(x['canonical_bytes_ascii'].encode('ascii')) for x in load('ORACLE')['records']]
def cp(n):
    return l.Checkpoint('demo:chain', n, '0'*64 if n == 0 else load('ORACLE')['records'][n-1]['sha256'])
def checkpoint(d): return l.Checkpoint(d['chain_id'],d['sequence'],d['head_hash'])
def page_case(case):
    p=case['page'];return l.Page(checkpoint(p['before']),checkpoint(p['after']),checkpoint(p['through']),[a.decode_event(x.encode('ascii')) for x in p['events_ascii']])

class PureTests(unittest.TestCase):
    def rejected(self, call, code='invalid_schema'):
        with self.assertRaises(l.LedgerError) as caught: call()
        self.assertEqual(caught.exception.code,code)
        self.assertEqual(caught.exception.args,('Agent ledger rejected: '+code,))

    def test_checkpoint_goldens(self):
        for case in load('ORACLE')['checkpoints']:
            with self.subTest(case=case['name']):
                raw=case['canonical_bytes_ascii'].encode('ascii');self.assertEqual(len(raw),case['byte_length'])
                self.assertEqual(hashlib.sha256(raw).hexdigest(),case['sha256'])
                self.assertEqual(l.encode_checkpoint(l.decode_checkpoint(raw)),raw)

    def test_checkpoint_constructor(self):
        for n,code in [(True,'invalid_schema'),(-1,'invalid_schema'),(4097,'limit_exceeded'),(1.0,'invalid_schema')]:
            self.rejected(lambda:l.Checkpoint('demo:chain',n,'0'*64),code)
        self.rejected(lambda:l.Checkpoint('demo:chain',0,'f'*64),'inconsistent_chain')
        self.rejected(lambda:l.Checkpoint('demo:chain',0,'A'*64))
        self.rejected(lambda:l.Checkpoint('a'*129,0,'0'*64),'limit_exceeded')

    def test_wire_refusals(self):
        for c in load('CASES')['checkpoint_wire_refusals']:
            with self.subTest(case=c['id']): self.rejected(lambda:l.decode_checkpoint(bytes.fromhex(c['wire_hex'])),c['expected'])

    def test_error_precedence(self):
        self.rejected(lambda:l.decode_checkpoint(bytearray(b'x'*2000)))
        self.rejected(lambda:l.decode_checkpoint(b'x'*1025),'limit_exceeded')
        for c in ['invalid_schema','busy','outcome_unknown','closed']:
            self.assertEqual(l.LedgerError(c).code,c)
        self.assertEqual(l.LedgerError('secret/path').code,'invalid_schema')

    def test_twelve_kind_chain(self):
        result=l.verify_events(events(),chain_id='demo:chain');self.assertEqual(result.head,cp(12))
        self.assertEqual(result.verified_events,12);self.assertEqual(result.canonical_event_bytes,9667)
        self.assertEqual(len({e.kind for e in events()}),10)

    def test_unanchored_prefixes(self):
        for n in range(13):
            v=l.verify_events(events()[:n],chain_id='demo:chain');self.assertEqual(v.head,cp(n));self.assertEqual(v.anchor_status,l.AnchorStatus.NOT_SUPPLIED)

    def test_expected_anchors(self):
        for c in load('ORACLE')['anchor_cases']:
            expected=None if c['expected_sequence'] is None else l.Checkpoint(c.get('expected_chain_id','demo:chain'),c['expected_sequence'],c['expected_hash'])
            self.assertEqual(l.verify_events(events()[:c['supplied_through']],chain_id='demo:chain',expected=expected).anchor_status.value,c['anchor_status'])

    def test_replacement_anchor(self):
        old=events()[0];changed=replace(old,subject=replace(old.subject,objective='different'))
        result=l.verify_events([changed],chain_id='demo:chain',expected=cp(1));self.assertEqual(result.anchor_status,l.AnchorStatus.MISMATCH)
        self.assertEqual(l.verify_events([changed],chain_id='demo:chain').anchor_status,l.AnchorStatus.NOT_SUPPLIED)

    def test_reorder_gap_duplicate(self):
        es=events()
        for sequence in [[es[1],es[0]], [es[0],es[2]], [es[0],es[0]]]:
            self.rejected(lambda:l.verify_events(sequence,chain_id='demo:chain'),'inconsistent_chain')
        duplicate=replace(es[1],event_id=es[0].event_id)
        self.rejected(lambda:l.verify_events([es[0],duplicate],chain_id='demo:chain'),'duplicate')

    def test_explicit_empty_identity(self):
        self.assertEqual(l.verify_events([],chain_id='demo:chain').head,cp(0))
        self.rejected(lambda:l.verify_events([],chain_id='bad'))
        with self.assertRaises(TypeError):l.verify_events([])

    def test_positive_page_continuation(self):
        for case in load('PAGES')['positive']:
            with self.subTest(case=case['id']):
                result=l.verify_page(page_case(case),start=checkpoint(case['start']),through=checkpoint(case['through']),prior=[a.decode_event(x.encode('ascii')) for x in case['prior_ascii']])
                expected=case['expected'];self.assertEqual(result.reached_terminal,expected['reached_terminal'])
                for name in ['resolved','unresolved']:
                    actual=[{'chain_id':x.chain_id,'sequence':x.sequence,'event_id':x.event_id,'kind':x.kind.value,'digest':x.digest} for x in getattr(result,name)]
                    self.assertEqual(actual,expected[name])
                self.assertEqual(result.prior_membership,'not_verified');self.assertEqual(result.prior_global_uniqueness,'not_verified')

    def test_partial_prior_context(self):
        es=events();p=l.Page(cp(4),cp(8),cp(12),es[4:8]);r=l.verify_page(p,start=cp(4),through=cp(12))
        self.assertTrue(r.unresolved);self.assertEqual(r.prior_membership,'not_verified')
        r=l.verify_page(p,start=cp(4),through=cp(12),prior=es[:4]);self.assertEqual(r.unresolved,())

    def test_external_page_checkpoints(self):
        es=events();p=l.Page(cp(0),cp(4),cp(4),es[:4])
        self.rejected(lambda:l.verify_page(p,start=cp(0),through=cp(12)),'inconsistent_chain')
        self.rejected(lambda:l.verify_page(p,start=cp(1),through=cp(4)),'inconsistent_chain')
        self.rejected(lambda:l.verify_page(l.Page(cp(0),cp(0),cp(12),[]),start=cp(0),through=cp(12)),'inconsistent_chain')

    def test_asof_recording_order(self):
        es=events();self.assertEqual(es[0].recorded.at_ns,es[1].recorded.at_ns)
        self.assertEqual(l.verify_events(es[:2],chain_id='demo:chain').head,cp(2))
        self.assertNotEqual(es[0].occurred,es[1].occurred)

    def test_ownership_result_and_forgery(self):
        es=events();p=l.Page(cp(0),cp(2),cp(12),es[:2]);es.clear();self.assertEqual(len(p.events),2)
        with self.assertRaises(FrozenInstanceError):p.after=cp(0)
        for count,bytes_,code in [(1,1056,'inconsistent_chain'),(2,1,'inconsistent_chain'),(2,32769,'inconsistent_chain'),(True,1056,'invalid_schema'),(4097,1056,'limit_exceeded'),(2,-1,'invalid_schema'),(2,33554433,'limit_exceeded')]:
            self.rejected(lambda:l.Verification(cp(2),l.AnchorStatus.NOT_SUPPLIED,count,bytes_),code)
        self.rejected(lambda:l.Verification(cp(0),l.AnchorStatus.NOT_SUPPLIED,0,1),'inconsistent_chain')
        self.rejected(lambda:l.Verification(cp(0),l.AnchorStatus.MATCHED_PREFIX,0,0))
        self.rejected(lambda:l.Verification(cp(2),'not_supplied',2,1056))
        refs=[a.event_reference(e) for e in events()]
        self.rejected(lambda:l.PageVerification(cp(6),False,[None]*1024,[None]),'limit_exceeded')
        self.rejected(lambda:l.PageVerification(cp(6),False,[refs[0],refs[0]],[]),'duplicate')
        self.rejected(lambda:l.PageVerification(cp(6),False,[refs[0]],[refs[0]]),'inconsistent_reference')
        for changed in [replace(refs[0],sequence=3),replace(refs[0],digest='f'*64)]:
            self.rejected(lambda:l.PageVerification(cp(6),False,[refs[0],changed],[]),'inconsistent_reference')
        for ref in [replace(refs[0],chain_id='other:chain'),refs[5]]:
            self.rejected(lambda:l.PageVerification(cp(6),False,[ref],[]),'inconsistent_reference')
        self.rejected(lambda:l.PageVerification(cp(6),1,[],[]))
        self.rejected(lambda:l.PageVerification(cp(6),False,[],[],prior_membership='verified'))
        for status,observed in [(l.ReconciliationStatus.FOUND_EXACT,None),(l.ReconciliationStatus.ABSENT_AT_UNCHANGED_HEAD,refs[0]),(l.ReconciliationStatus.BASE_NOT_COVERED,refs[0])]:
            self.rejected(lambda:l.Reconciliation(status,cp(12),observed))
        for ref in [refs[2],replace(refs[1],digest='f'*64)]:
            self.rejected(lambda:l.Reconciliation(l.ReconciliationStatus.CONFLICT,cp(2),ref),'inconsistent_reference')
        forged=cp(2);object.__setattr__(forged,'sequence',True)
        self.rejected(lambda:l.Verification(forged,l.AnchorStatus.NOT_SUPPLIED,2,1056))
        forged_ref=a.event_reference(events()[0]);object.__setattr__(forged_ref,'sequence',True)
        self.rejected(lambda:l.PageVerification(cp(6),False,[forged_ref],[]))
        class Other(l.Checkpoint):pass
        self.rejected(lambda:l.encode_checkpoint(Other('demo:chain',0,'0'*64)))

    def test_page_limits(self):
        self.rejected(lambda:l.Page(cp(0),cp(1),cp(12),[events()[0]]*65),'limit_exceeded')
        self.rejected(lambda:l.verify_events([events()[0]]*4097,chain_id='demo:chain'),'limit_exceeded')
        self.rejected(lambda:l.verify_page(l.Page(cp(0),cp(1),cp(12),events()[:1]),start=cp(0),through=cp(12),prior=[None]*65),'limit_exceeded')

if __name__ == '__main__':unittest.main()
