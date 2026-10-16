"""Frozen EQ111 public capability probes; synthetic finite bounds, no calendar/source I/O."""
from dataclasses import replace
import hashlib
import json
import unittest
from equity_feature_contracts import (AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ConfigSpec,
    ContractError, Coverage, DataKind, EntityKey, HistoryContext, InputScope, IntervalSpec,
    Parameter, PriceUnit, SessionSpec, SourceBinding, Status, WindowSpec)
from equity_features.session import compute_trades

T=1700000000000000000
D=86400000000000
H=3600000000000
UNIT=PriceUnit(0,'USD')
def session(name='W',start=T,end=T+7*D):
    return SessionSpec('synthetic:continuous',name,start,end,'caller-supplied-UTC')
def config(s):
    return ConfigSpec('continuous-reuse-probe','v1',(Parameter('eligibility_policy','synthetic-v1'),),
        s,WindowSpec(1,s.session_id,('prior',s.session_id)),AvailabilitySpec(s.close_ns,s.close_ns,s.close_ns),price_unit=UNIT)
def batch(s,stamps=(T,T+3*D,T+7*D-1)):
    n=len(stamps)
    data=dict(instrument_id=('A',)*n,session_id=(s.session_id,)*n,event_ns=stamps,
        order_key=tuple(range(1,n+1)),event_id=tuple('e'+str(i) for i in range(n)),eligible=(True,)*n,
        price=(100,102,101)[:n],size=(2,3,5)[:n],known_at_ns=stamps)
    return CanonicalBatch(DataKind.TRADE,tuple(Column(k,v) for k,v in data.items()),
        BatchMetadata(s.namespace,SourceBinding('synthetic','continuous-v1','direct-v1','trades'),
            Coverage(n,n,True),UNIT,scope=InputScope(s.open_ns,s.close_ns,'synthetic-v1')))

class ContinuousCapability(unittest.TestCase):
    def test_week_half_open_and_cutoff(self):
        s=session()
        points=(T-1,T,T+7*D-1,T+7*D)
        self.assertEqual(tuple(s.admits_event(x,s.close_ns) for x in points),(False,True,True,False))
        self.assertFalse(s.admits_event(T+3*D,T+3*D))
        self.assertTrue(s.admits_event(T+3*D-1,T+3*D))
    def test_finite_day_partition_has_exactly_one_owner(self):
        days=tuple(session('D'+str(i),T+i*D,T+(i+1)*D) for i in range(7))
        for point,expected in ((T-1,()),(T,(0,)),(T+D,(1,)),(T+6*D,(6,)),(T+7*D,())):
            self.assertEqual(tuple(i for i,s in enumerate(days) if s.admits_event(point,s.close_ns)),expected)
        for s in days:
            c=config(s);self.assertEqual(ConfigSpec.from_json(c.to_json()),c)
    def test_overnight_supplied_bounds(self):
        s=session('overnight',T+22*H,T+26*H)
        self.assertEqual(tuple(s.admits_event(x,s.close_ns) for x in (T+22*H,T+24*H,T+26*H)),(True,True,False))
    def test_supplied_civil_days_and_opaque_timezone(self):
        for hours in (23,25):
            s=replace(session('civil',T,T+hours*H),timezone_label='opaque-no-calendar')
            self.assertEqual(s.close_ns-s.open_ns,hours*H)
            self.assertTrue(s.admits_event(s.close_ns-1,s.close_ns));self.assertFalse(s.admits_event(s.close_ns,s.close_ns))
    def test_explicit_gap_is_not_filled(self):
        a=session('A',T,T+D);b=session('B',T+2*D,T+3*D)
        self.assertFalse(any(s.admits_event(T+D,s.close_ns) for s in (a,b)))
        self.assertFalse(any(s.admits_event(T+2*D-1,s.close_ns) for s in (a,b)))
    def test_auction_disabled_and_invalid_cutoff(self):
        s=session()
        self.assertFalse(s.admits_event(T,s.close_ns,auction='opening'))
        self.assertFalse(s.admits_event(s.close_ns,s.close_ns,auction='closing'))
        with self.assertRaises(ContractError):s.admits_event(T,s.close_ns+1)
    def test_named_intervals_are_labels_not_feed_gates(self):
        s=replace(session(),intervals=(IntervalSpec('scheduled-freeze',T+D,T+2*D),))
        self.assertTrue(s.admits_event(T+D,s.close_ns))
        # Overlapping named intervals are admitted; callers cannot infer exclusivity.
        self.assertEqual(len(replace(s,intervals=s.intervals+(IntervalSpec('other',T+D,T+3*D),)).intervals),2)
    def test_governed_count_keeps_missing_slot(self):
        w=WindowSpec(2,'target',('first','missing','target'))
        self.assertEqual(w.selected_sessions(),('first','missing'));self.assertTrue(w.history_complete)
        self.assertFalse(replace(w,count=3).history_complete)
        with self.assertRaises(ContractError):replace(w,anchor='duration_ns')
    def test_history_slot_coverage_is_distinct_from_count(self):
        a=session('first',T,T+D);b=session('missing',T+D,T+2*D);c=session('target',T+2*D,T+3*D)
        h=HistoryContext(EntityKey('A','target'),'synthetic-grid-v1',(a,b,c),
            (Coverage(1,1,True),Coverage(1,0,False),Coverage(1,1,True)))
        self.assertEqual(h.slot_coverage[1],Coverage(1,0,False))
        with self.assertRaises(ContractError):replace(h,sessions=(a,replace(b,open_ns=T+D-1),c))
    def test_knowledge_is_causal_not_feed_health(self):
        a=AvailabilitySpec(T+D,T+D,T+D)
        self.assertEqual(tuple(a.knowledge_reason(x) for x in (None,T+D,T+D+1)),('unknown_availability',None,'future_knowledge'))
    def test_no_direct_feed_state_or_duration_field(self):
        with self.assertRaises(TypeError):SessionSpec('synthetic','S',T,T+D,'supplied',feed_state='outage')
        with self.assertRaises(TypeError):WindowSpec(1,'S',('S',),duration_ns=D)
    def test_subclass_is_not_a_schema1_extension(self):
        class AlternativeSession(SessionSpec):pass
        s=AlternativeSession('synthetic:continuous','W',T,T+7*D,'supplied')
        with self.assertRaises(ContractError):replace(config(session()),session=s)
    def test_existing_trade_kernel_on_seven_day_interval(self):
        s=session();c=config(s);b=batch(s);r=compute_trades(b,c,entity=EntityKey('A','W'))
        actual={x.feature_id.rsplit('.',1)[-1]:x.values[0] for x in r.values}
        self.assertEqual((actual['count'],actual['volume'],actual['notional']),(3,10,1011))
        self.assertAlmostEqual(actual['vwap'],101.1,delta=1e-12)
        self.assertAlmostEqual(actual['mean_size'],10/3,delta=1e-12)
        self.assertTrue(all(q.status==Status.AVAILABLE for q in r.quality))
        self.assertEqual(r.metadata.config_digest,c.digest);self.assertEqual(r.metadata.inputs[0].metadata,b.metadata)
    def test_day_partition_kernel_parity(self):
        got=[]
        for i in range(7):
            s=session('D'+str(i),T+i*D,T+(i+1)*D)
            b=batch(s,(s.open_ns,s.open_ns+H,s.close_ns-1))
            r=compute_trades(b,config(s),entity=EntityKey('A',s.session_id))
            got.append(tuple(x.values[0] for x in r.values))
        self.assertTrue(all(x==got[0] for x in got));self.assertEqual(len(got),7)
    def test_kernel_rejects_end_equality_and_foreign_session(self):
        s=session();b=batch(s)
        bad=replace(b,columns=tuple(Column(x.name,(T,T+3*D,s.close_ns)) if x.name=='event_ns' else x for x in b.columns))
        with self.assertRaises(ContractError):compute_trades(bad,config(s),entity=EntityKey('A','W'))
        with self.assertRaises(ContractError):compute_trades(b,config(session('other')),entity=EntityKey('A','other'))
    def test_legacy_literal_bytes_and_digest(self):
        # Independent preexisting baseline d8ff...; literal schema envelope, no production serializer for expected bytes.
        expected={
            'identity':'synthetic:baseline','algorithm_version':'v1','schema_version':'1',
            'parameters':[{'name':'a','value':20},{'name':'z','value':{'float64':'0x1.8000000000000p+0'}}],
            'session':{'namespace':'demo','session_id':'S3','open_ns':100,'close_ns':200,'timezone_label':'caller-label',
                'intervals':[{'name':'opening','start_ns':100,'end_ns':120}],'scheduled_close_ns':None,
                'early_close':False,'include_opening_auction':False,'include_closing_auction':False},
            'window':{'count':2,'target_session_id':'S3','governed_sessions':['S1','S2','S3','S4'],'anchor':'prior_only'},
            'availability':{'market_cutoff_ns':200,'knowledge_cutoff_ns':210,'evaluation_ns':210,'mode':'known_at','reconstruction_reason':None},
            'adjustment':{'basis':'raw','policy_version':'raw-v1','action_snapshot':'none','anchor':'none'},
            'price_unit':{'scale':4,'currency':'USD'}}
        raw=json.dumps(expected,sort_keys=True,separators=(',',':'),ensure_ascii=True)
        self.assertEqual(hashlib.sha256(raw.encode()).hexdigest(),'d8ff9ddb56cf26be7e9550874f8891f4db5d3ee38ed3b6a7ac9a100a5fa9d8fc')
        c=ConfigSpec('synthetic:baseline','v1',(Parameter('z',1.5),Parameter('a',20)),
            SessionSpec('demo','S3',100,200,'caller-label',(IntervalSpec('opening',100,120),)),
            WindowSpec(2,'S3',('S1','S2','S3','S4')),AvailabilitySpec(200,210,210),price_unit=PriceUnit(4,'USD'))
        self.assertEqual(c.to_json(),raw);self.assertEqual(ConfigSpec.from_json(raw),c)
        self.assertEqual(c.digest,'d8ff9ddb56cf26be7e9550874f8891f4db5d3ee38ed3b6a7ac9a100a5fa9d8fc')

if __name__=='__main__':unittest.main()
