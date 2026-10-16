"""Independent pre-code wires and public operation/ownership controls."""
from dataclasses import FrozenInstanceError, replace
import hashlib
import json
from pathlib import Path
import unittest
from equity_feature_contracts import AvailabilitySpec
from equity_feature_evidence import ContentFingerprint, InputFingerprint
import equity_feature_agent_evidence as a

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / 'docs/stories'


def load(name):
    return json.loads((FIXTURES / ('EQ-106_' + name + '.json')).read_bytes())


def events():
    return [a.decode_event(x['canonical_bytes_ascii'].encode('ascii')) for x in load('KIND_CASES')['cases']]


def reference(event):
    return a.event_reference(event)


class EventTests(unittest.TestCase):
    def rejected(self, callback, code='invalid_schema'):
        with self.assertRaises(a.AgentEvidenceError) as c: callback()
        self.assertEqual(c.exception.code, code)
        self.assertIsNone(c.exception.__context__)
        self.assertIsNone(c.exception.__cause__)
        self.assertEqual(c.exception.args, ('Agent evidence rejected: ' + code,))

    def test_original_two_literal_oracles(self):
        for x in load('EVENT_ORACLE')['fixtures']:
            with self.subTest(name=x['name']):
                raw=x['canonical_bytes_ascii'].encode('ascii')
                self.assertEqual(len(raw), x['byte_length'])
                self.assertEqual(hashlib.sha256(raw).hexdigest(), x['sha256'])
                v=a.decode_event(raw)
                self.assertEqual(a.encode_event(v), raw)
                self.assertEqual(a.event_digest(v), x['sha256'])

    def test_twelve_all_kind_events_and_links(self):
        previous='0'*64; retained=[]; kinds=set()
        for x in load('KIND_CASES')['cases']:
            with self.subTest(name=x['name']):
                raw=x['canonical_bytes_ascii'].encode('ascii'); v=a.decode_event(raw)
                self.assertEqual(a.encode_event(v),raw)
                self.assertEqual(a.event_digest(v),x['sha256'])
                self.assertEqual(v.previous_hash, previous)
                self.assertEqual(json.loads(raw), x['event'])
                self.assertTrue(a.check_references(v,retained).fully_resolved)
                kinds.add(v.kind); retained.append(v); previous=x['sha256']
        self.assertEqual(kinds,set(a.EventKind))
        self.assertLess(retained[1].occurred.at_ns,retained[1].recorded.at_ns)
        self.assertEqual(retained[-1].subject.target.event_id,retained[5].event_id)

    def test_54_independent_decoder_refusals(self):
        for x in load('REFUSAL_CASES')['decode_refusals']:
            with self.subTest(name=x['name']):
                raw=bytes.fromhex(x['wire_hex']) if 'wire_hex' in x else x['wire_ascii'].encode('ascii')
                self.rejected(lambda:a.decode_event(raw),x['expected_error'])

    def test_23_independent_structural_variants(self):
        for x in load('REFUSAL_CASES')['structural_variants']:
            with self.subTest(name=x['name']):
                raw=x['wire_ascii'].encode('ascii'); v=a.decode_event(raw)
                self.assertEqual(a.encode_event(v),raw)
                self.assertEqual(a.event_digest(v),x['sha256'])

    def test_lookup_match_missing_and_empty(self):
        req,model,call=events()[:3]
        good=a.check_references(call,[req]); missing=a.check_references(call,[model])
        self.assertEqual(good.verified,(reference(req),));self.assertEqual(good.unresolved,())
        self.assertEqual(missing.verified,());self.assertEqual(missing.unresolved,(reference(req),))
        self.assertFalse(missing.fully_resolved)
        empty=a.check_references(model,[])
        self.assertEqual((empty.verified,empty.unresolved,empty.fully_resolved),((),(),True))

    def test_id_sequence_split_and_digest_conflicts(self):
        req,model,call=events()[:3]; r=reference(req)
        cases=[(replace(r,sequence=2),[req]),(replace(r,event_id='demo:absent'),[req]),
               (replace(r,sequence=2),[req,model]),(replace(r,digest='f'*64),[req])]
        for ref,context in cases:
            v=replace(call,subject=replace(call.subject,request=ref))
            self.rejected(lambda:a.check_references(v,context),'inconsistent_reference')
        ref=replace(r,kind=a.EventKind.MODEL_DECLARATION)
        v=replace(call,subject=a.ErrorSubject(ref,a.EventErrorCode.UNKNOWN))
        self.rejected(lambda:a.check_references(v,[req]),'inconsistent_reference')

    def test_conflict_after_missing_and_subset_order(self):
        v=events(); req=v[0]; feature=v[4]; decision=v[5]
        result=a.check_references(decision,[feature])
        self.assertEqual(result.verified,(reference(feature),))
        self.assertEqual(result.unresolved,(reference(req),))
        bad=replace(feature,event_id='demo:other')
        self.rejected(lambda:a.check_references(decision,[bad]),'inconsistent_reference')

    def test_all_context_validated_before_resolution(self):
        req,model,call=events()[:3]
        for context in ([req,req],[req,replace(req,event_id='demo:other')],[req,replace(model,event_id=req.event_id)]):
            self.rejected(lambda:a.check_references(call,context),'duplicate')
        self.rejected(lambda:a.check_references(call,[replace(req,chain_id='other:chain')]),'invalid_reference')
        self.rejected(lambda:a.check_references(call,[call]),'invalid_reference')
        self.rejected(lambda:a.check_references(call,[req]*65),'limit_exceeded')

    def test_context_need_not_be_linked_prefix(self):
        v=events(); decision=v[5]
        self.assertTrue(a.check_references(decision,[v[0],v[4]]).fully_resolved)
        changed=replace(v[4],previous_hash='f'*64)
        self.rejected(lambda:a.check_references(decision,[v[0],changed]),'inconsistent_reference')
        # Rebinding to supplied changed identity checks consistency only, not linkage.
        local=replace(decision,subject=replace(decision.subject,feature_reads=[reference(changed)]))
        self.assertTrue(a.check_references(local,[v[0],changed]).fully_resolved)

    def test_reference_header_roles_and_corrections(self):
        v=events(); r=reference(v[0]); call=v[2]
        for bad in (replace(r,chain_id='other:chain'),replace(r,sequence=3),replace(r,event_id=call.event_id)):
            self.rejected(lambda:replace(call,subject=replace(call.subject,request=bad)),'invalid_reference')
        self.rejected(lambda:replace(call.subject,request=reference(v[1])),'invalid_reference')
        target=reference(v[5]); replacement=reference(v[10])
        self.rejected(lambda:a.CorrectionSubject(target,a.CorrectionOperation.AMEND,None,'revision'),'invalid_reference')
        self.rejected(lambda:a.CorrectionSubject(target,a.CorrectionOperation.REVOKE,replacement,'revision'),'invalid_reference')
        self.rejected(lambda:a.CorrectionSubject(target,a.CorrectionOperation.AMEND,target,'revision'),'invalid_reference')
        self.rejected(lambda:a.CorrectionSubject(reference(v[9]),a.CorrectionOperation.REVOKE,None,'revision'),'invalid_reference')

    def test_aggregate_reference_limit_and_duplicates(self):
        req=reference(events()[0]);v=events()[5]
        refs=[a.EventReference(req.chain_id,2,'demo:r'+str(i),a.EventKind.FEATURE_READ,'a'*64) for i in range(16)]
        subject=a.DecisionSubject(req,refs,a.DecisionAction.DEFER,'synthetic')
        self.rejected(lambda:replace(v,subject=subject),'limit_exceeded')
        self.rejected(lambda:a.DecisionSubject(req,[refs[0],refs[0]],a.DecisionAction.DEFER,'synthetic'),'duplicate')
        self.rejected(lambda:a.ReferenceCheck([req],[req]),'duplicate')

    def test_payload_complete_changed_length_and_empty(self):
        raw=b'{"job_ref":"j1"}'
        p=a.PayloadReference(a.PayloadKind.TOOL_RESULT,hashlib.sha256(raw).hexdigest(),16,16,a.DisclosureState.RETAINED_COMPLETE)
        result=a.verify_payload(p,raw)
        self.assertEqual((result.status,result.disclosure,result.retained_bytes,result.retained_matched),
                         (a.PayloadCheckStatus.MATCHED_RETAINED,a.DisclosureState.RETAINED_COMPLETE,16,True))
        self.rejected(lambda:a.verify_payload(p,raw.replace(b'j1',b'j2')),'inconsistent_content')
        for data in (raw[:-1],raw+b' '):self.rejected(lambda:a.verify_payload(p,data),'inconsistent_content')
        empty=replace(p,digest='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',retained_bytes=0,full_bytes=0)
        self.assertTrue(a.verify_payload(empty,b'').retained_matched)

    def test_truncated_missing_redacted_unknown(self):
        prefix=b'{"jo';dg=hashlib.sha256(prefix).hexdigest()
        refs=[a.PayloadReference(a.PayloadKind.ARTIFACT,dg,4,16,a.DisclosureState.TRUNCATED),
              a.PayloadReference(a.PayloadKind.ARTIFACT,dg,4,4,a.DisclosureState.RETAINED_COMPLETE)]
        self.assertTrue(a.verify_payload(refs[0],prefix).retained_matched)
        refs.extend(a.PayloadReference(a.PayloadKind.ARTIFACT,None,0,None,state) for state in
                    (a.DisclosureState.REDACTED,a.DisclosureState.NOT_SUPPLIED,a.DisclosureState.UNKNOWN))
        for p in refs:
            result=a.verify_payload(p,None)
            self.assertEqual((result.status,result.disclosure,result.retained_bytes,result.retained_matched),
                             (a.PayloadCheckStatus.UNAVAILABLE,p.state,0,False))
        for p in refs[2:]:self.assertFalse(a.verify_payload(p,b'synthetic absent evidence').retained_matched)

    def test_payload_types_caps_and_result_invariants(self):
        raw=b'a'*65536;p=a.PayloadReference(a.PayloadKind.ARTIFACT,hashlib.sha256(raw).hexdigest(),len(raw),len(raw),a.DisclosureState.RETAINED_COMPLETE)
        self.assertTrue(a.verify_payload(p,raw).retained_matched)
        for value in (bytearray(b'a'),memoryview(b'a'),'a',object()):self.rejected(lambda:a.verify_payload(p,value))
        class Bytes(bytes):pass
        self.rejected(lambda:a.verify_payload(p,Bytes(b'a')))
        for ref in (p,a.PayloadReference(a.PayloadKind.ARTIFACT,None,0,None,a.DisclosureState.REDACTED)):
            self.rejected(lambda:a.verify_payload(ref,raw+b'a'),'limit_exceeded')
        for state in (a.DisclosureState.REDACTED,a.DisclosureState.NOT_SUPPLIED,a.DisclosureState.UNKNOWN):
            self.rejected(lambda:a.PayloadCheck(a.PayloadCheckStatus.MATCHED_RETAINED,state,0))
        self.rejected(lambda:a.PayloadCheck(a.PayloadCheckStatus.UNAVAILABLE,a.DisclosureState.UNKNOWN,1))
        object.__setattr__(p,'retained_bytes',True)
        self.rejected(lambda:a.verify_payload(p,b'a'))

    def test_list_inputs_detach_and_tuple_outputs(self):
        entry=a.Argument('limit',1);original=[entry]
        arguments=a.ArgumentSet(a.DisclosureState.RETAINED_COMPLETE,1,original)
        original.clear();object.__setattr__(entry,'value',False)
        self.assertEqual(arguments.entries,(a.Argument('limit',1),));self.assertIs(type(arguments.entries),tuple)
        v=events();features=['trade.count'];fp=ContentFingerprint('canonical_batch','a'*64,1)
        inp=InputFingerprint('trades','t1',fp);inputs=[inp]
        read=a.FeatureReadSubject(reference(v[3]),a.PayloadReference(a.PayloadKind.EXECUTION_RECEIPT,None,0,None,a.DisclosureState.NOT_SUPPLIED),None,inputs,None,features,None)
        features.clear();inputs.clear();object.__setattr__(fp,'digest','b'*64);object.__setattr__(inp,'input_id','changed')
        self.assertEqual(read.inputs[0].content.digest,'a'*64);self.assertEqual(read.inputs[0].input_id,'t1')
        self.assertEqual(read.feature_ids,('trade.count',));self.assertIs(type(read.inputs),tuple)
        refs=[reference(v[4])];decision=a.DecisionSubject(reference(v[0]),refs,a.DecisionAction.DEFER,'review')
        refs.clear();self.assertEqual(decision.feature_reads,(reference(v[4]),))
        good=[reference(v[0])];check=a.ReferenceCheck(good,[]);good.clear()
        self.assertEqual(check.verified,(reference(v[0]),));self.assertIs(type(check.unresolved),tuple)

    def test_nested_headers_subject_and_availability_detach(self):
        original=events()[0];availability=AvailabilitySpec(1,2,3)
        context=a.DecisionContext('demo','S',availability);subject=a.RequestSubject('r1','research',context)
        event=replace(original,subject=subject);before=a.encode_event(event)
        for value,key,new in ((availability,'market_cutoff_ns',-1),(context.availability,'knowledge_cutoff_ns',-2),
                              (subject,'objective','changed'),(original.actor,'actor_id','changed'),
                              (original.occurred,'at_ns',-1),(original.recorded,'at_ns',-2)):
            object.__setattr__(value,key,new)
        self.assertEqual(a.encode_event(event),before)
        v=events();ref=reference(v[0]);call=a.ToolCallSubject(ref,'read',None,a.ArgumentSet(a.DisclosureState.UNKNOWN,None,()))
        object.__setattr__(ref,'digest','f'*64);self.assertEqual(call.request.digest,reference(v[0]).digest)

    def test_revalidate_hostile_tampering_all_event_paths(self):
        for operation in (a.encode_event,a.event_digest,a.event_reference,lambda e:a.check_references(e,[])):
            v=events()[0];object.__setattr__(v,'sequence',True)
            self.rejected(lambda:operation(v))
            v=events()[0];object.__setattr__(v.subject,'objective','x'*257)
            self.rejected(lambda:operation(v),'limit_exceeded')

    def test_constructor_aggregate_escaped_byte_cap(self):
        v=events()[2];entries=[a.Argument('arg'+str(i),'😀'*256) for i in range(16)]
        args=a.ArgumentSet(a.DisclosureState.RETAINED_COMPLETE,16,entries)
        subject=replace(v.subject,arguments=args)
        self.rejected(lambda:replace(v,subject=subject),'limit_exceeded')

    def test_exact_types_before_callbacks(self):
        class Spy:
            def __iter__(self):raise AssertionError('untrusted iterator called')
        class List(list):
            def __iter__(self):raise AssertionError('subclass iterator called')
        class Actor(a.ActorDeclaration):pass
        for value in (Spy(),List(),iter(())):
            self.rejected(lambda:a.ArgumentSet(a.DisclosureState.UNKNOWN,None,value))
            self.rejected(lambda:a.check_references(events()[0],value))
        self.rejected(lambda:replace(events()[0],actor=Actor(None,a.ActorKind.UNKNOWN)))
        self.rejected(lambda:a.ActorDeclaration(None,'unknown'))
        self.rejected(lambda:a.TimeDeclaration(True,None,None))

    def test_frozen_properties_and_no_mutable_returns(self):
        v=events()[0];check=a.check_references(v,[])
        p=a.PayloadCheck(a.PayloadCheckStatus.UNAVAILABLE,a.DisclosureState.UNKNOWN,0)
        for obj,name,value in ((v,'kind',a.EventKind.ERROR),(check,'fully_resolved',False),(p,'retained_matched',True),(v,'sequence',2)):
            with self.assertRaises((FrozenInstanceError,AttributeError)):setattr(obj,name,value)

    def test_privacy_fixed_errors_and_constructor_domains(self):
        canary='synthetic-private-canary'
        self.rejected(lambda:a.decode_event(('{"'+canary+'":').encode()))
        self.rejected(lambda:a.ActorDeclaration(canary,a.ActorKind.UNKNOWN))
        self.rejected(lambda:a.decode_event(bytearray()))
        for n in (-(2**63),2**63-1):self.assertEqual(a.TimeDeclaration(n,None,0).at_ns,n)
        for n in (-(2**63)-1,2**63):self.rejected(lambda:a.TimeDeclaration(n,None,None))
        v=events()[0];self.rejected(lambda:replace(v,previous_hash='a'*64),'invalid_reference')

    def test_earlier_parameter_semantics_before_later_nested_error(self):
        raw=load('KIND_CASES')['cases'][0]['event']
        raw['subject']['request_key']='x'*257;raw['subject']['context']={}
        wire=json.dumps(raw,sort_keys=True,separators=(',',':')).encode('ascii')
        self.rejected(lambda:a.decode_event(wire),'limit_exceeded')
        self.rejected(lambda:a.RequestSubject('x'*257,'research',object()),'limit_exceeded')
        raw=load('KIND_CASES')['cases'][2]['event']
        raw['subject']['tool_name']='x'*257;raw['subject']['arguments']={}
        self.rejected(lambda:a.decode_event(json.dumps(raw,sort_keys=True,separators=(',',':')).encode('ascii')),'limit_exceeded')
        raw=load('KIND_CASES')['cases'][0]['event']
        raw['actor']={'actor_id':'x'*257,'kind':'bad'}
        self.rejected(lambda:a.decode_event(json.dumps(raw,sort_keys=True,separators=(',',':')).encode('ascii')),'limit_exceeded')

    def test_member_semantics_before_later_member_type(self):
        arg=a.Argument('first',None);object.__setattr__(arg,'name','x'*65)
        self.rejected(lambda:a.ArgumentSet(a.DisclosureState.RETAINED_COMPLETE,2,[arg,object()]),'limit_exceeded')
        ref=reference(events()[0]);object.__setattr__(ref,'event_id','x'*129)
        self.rejected(lambda:a.ReferenceCheck([ref,object()],[]),'limit_exceeded')
        self.rejected(lambda:a.ArgumentSet(a.DisclosureState.RETAINED_COMPLETE,17,[object()]*17),'limit_exceeded')

    def test_fingerprint_exact_type_before_unsupported_version(self):
        v=events()[4]
        for field in ('schema_version','canonicalization','algorithm'):
            for value,code in ((True,'invalid_schema'),('unsupported','unsupported_version')):
                fp=ContentFingerprint('configuration','a'*64,1);object.__setattr__(fp,field,value)
                self.rejected(lambda:replace(v.subject,configuration=fp),code)
                raw=load('KIND_CASES')['cases'][4]['event'];raw['subject']['configuration'][field]=value
                self.rejected(lambda:a.decode_event(json.dumps(raw,sort_keys=True,separators=(',',':')).encode('ascii')),code)

    def test_reference_context_first_member_semantics_before_later_type(self):
        v=events();first=replace(v[0],chain_id='other:chain')
        self.rejected(lambda:a.check_references(v[2],[first,object()]),'invalid_reference')

    def test_shallow_subject_tag_and_keys_before_typed_headers(self):
        for mutation in ('unknown_kind','extra_key'):
            raw=load('KIND_CASES')['cases'][0]['event'];raw['chain_id']='x'*129
            if mutation=='unknown_kind':raw['subject']['kind']='unselected'
            else:raw['subject']['extra']=True
            self.rejected(lambda:a.decode_event(json.dumps(raw,sort_keys=True,separators=(',',':')).encode('ascii')))


if __name__ == '__main__':unittest.main()
