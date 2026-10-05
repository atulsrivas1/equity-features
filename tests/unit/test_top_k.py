"""Independent topK ranking, partition conservation and admission adversaries."""
from dataclasses import FrozenInstanceError, replace
import unittest
from equity_feature_contracts import (Column, ContractError, Coverage, ErrorCode,
    Parameter, Status, TopKTradeRow, TopKTrades, builtin_registry)
from equity_feature_contracts.columnar import to_arrow_result
from equity_features.session import compute_top_k
from test_bars import ENTITY, config
from test_trades import trades


def cfg(k=2,limit=None):
    c=config();return replace(c,parameters=c.parameters+(Parameter('top_k',k),Parameter('evidence_limit',k if limit is None else limit)))

def calc(b=None,c=None):return compute_top_k(b,cfg() if c is None else c,entity=ENTITY)
def rows(r):return r.values[0].values[0].rows

def subset(b,indices):
    return replace(b,columns=tuple(Column(c.name,tuple(c.values[i] for i in indices)) for c in b.columns),metadata=replace(b.metadata,coverage=Coverage(len(indices),len(indices),True)))

class TopK(unittest.TestCase):
    def error(self,code,fn):
        with self.assertRaises(ContractError) as caught:fn()
        self.assertEqual(caught.exception.code,code)

    def test_golden_original_rows_and_evidence(self):
        r=calc(trades());self.assertEqual([x.event_id for x in rows(r)],['t3','t2'])
        self.assertEqual([(x.price,x.size) for x in rows(r)],[(101,5),(102,3)])
        self.assertEqual([e.row_id for e in r.evidence],['t3','t2'])
        self.assertEqual(r.metadata.config_digest,cfg().digest)
        self.assertEqual(r.metadata.inputs[0].metadata,trades().metadata)

    def test_one_and_more_than_population(self):
        self.assertEqual([x.event_id for x in rows(calc(trades(),cfg(1)))],['t3'])
        self.assertEqual([x.event_id for x in rows(calc(trades(),cfg(8)))],['t3','t2','t1'])

    def test_equal_size_time_and_order_ties(self):
        b=trades(size=(5,)*3,event_ns=(110,)*3,order_key=(1,2,3),event_id=('z','y','x'))
        self.assertEqual([x.event_id for x in rows(calc(b))],['z','y'])
        a=TopKTradeRow('trades','a',110,1,110,100,5);z=replace(a,event_id='z')
        self.assertEqual(TopKTrades(2,(a,z)).rows,(a,z))
        self.error(ErrorCode.INVALID_ORDER,lambda:TopKTrades(2,(z,a)))

    def test_ineligible_not_ranked(self):
        b=trades(size=(99,3,5),eligible=(False,True,True))
        self.assertEqual([x.event_id for x in rows(calc(b))],['t3','t2'])
        self.assertEqual(calc(b).quality[0].observed,3)

    def test_empty_and_ineligible_available_empty(self):
        self.assertEqual(rows(calc(subset(trades(),[]))),())
        self.assertEqual(rows(calc(trades(eligible=(False,)*3,price=None,size=None))),())
        self.assertEqual(calc(subset(trades(),[])).quality[0].status,Status.AVAILABLE)

    def test_missing_and_absent_payload(self):
        self.assertEqual(calc().quality[0].status,Status.MISSING_INPUT)
        for field in ('price','size'):
            r=calc(trades(**{field:None}));self.assertIsNone(r.values[0].values[0]);self.assertEqual(r.evidence,())

    def test_invalid_k_and_evidence_bounds(self):
        for k in (0,-1,True,1.0,10001,'2'):
            self.error(ErrorCode.INVALID_CONFIG,lambda:calc(trades(),cfg(k,10)))
        for limit in (1,10001,True,2.0):
            self.error(ErrorCode.INVALID_CONFIG,lambda:calc(trades(),cfg(2,limit)))
        self.error(ErrorCode.INVALID_CONFIG,lambda:calc(trades(),config()))

    def test_population_coverage_and_knowledge(self):
        b=trades();r=calc(replace(b,metadata=replace(b.metadata,coverage=Coverage(4,3,False))))
        self.assertEqual(r.quality[0].status,Status.INCOMPLETE_COVERAGE);self.assertEqual(r.evidence,())
        self.assertIsNone(calc(trades(known_at_ns=(110,130,999))).values[0].values[0])
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:calc(replace(b,metadata=replace(b.metadata,coverage=Coverage(2,2,True)))))

    def test_duplicate_and_overlap_admission(self):
        self.error(ErrorCode.DUPLICATE,lambda:calc(trades(event_id=('t1','t1','t3'))))
        b=trades();twice=replace(b,columns=tuple(Column(c.name,c.values+c.values) for c in b.columns),metadata=replace(b.metadata,coverage=Coverage(6,6,True)))
        self.error(ErrorCode.DUPLICATE,lambda:calc(twice))
        row=rows(calc(b))[0];self.error(ErrorCode.DUPLICATE,lambda:TopKTrades(2,(row,row)))

    def test_disjoint_partition_conservation(self):
        b=trades(size=(5,5,5));full=rows(calc(b))
        for partition in (([0],[1,2]),([0,1],[2]),([0],[1],[2])):
            partial=[x for indices in partition for x in rows(calc(subset(b,indices)))]
            expected=tuple(sorted(partial,key=lambda x:x.rank_key)[:2]);self.assertEqual(full,expected)

    def test_retained_bound_as_population_grows(self):
        for n in (10,100,1000):
            b=trades(instrument_id=('A',)*n,session_id=('S',)*n,event_ns=(110,)*n,order_key=tuple(range(n)),event_id=tuple(str(i) for i in range(n)),price=(100,)*n,size=tuple(range(1,n+1)),eligible=(True,)*n,known_at_ns=(110,)*n)
            r=calc(b,cfg(3));self.assertEqual(len(rows(r)),3);self.assertEqual(len(r.evidence),3)
            self.assertEqual([x.size for x in rows(r)],[n,n-1,n-2])

    def test_owned_immutable_rows(self):
        source=list(rows(calc(trades())));table=TopKTrades(2,source);source.clear();self.assertEqual(len(table.rows),2)
        with self.assertRaises(FrozenInstanceError):table.rows[0].size=99

    def test_arrow_exact_timestamps_payload_and_bound(self):
        import pyarrow as pa
        value=to_arrow_result(calc(trades()))['values']['session.trade.top_k'].column('value').combine_chunks()
        self.assertEqual(value.field('k').to_pylist(),[2])
        nested=value.field('rows').flatten();self.assertEqual(nested.field('event_ns').cast(pa.int64()).to_pylist(),[160,130])
        self.assertEqual(nested.field('price').to_pylist(),[101,102])

    def test_registry_and_exact_evidence_identity(self):
        builtin_registry().require_capability('session.trade.top_k','batch')
        r=calc(trades());self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:replace(r,evidence=()))
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:replace(r,evidence=(replace(r.evidence[0],event_ns=159),r.evidence[1])))
        for mode in ('merge',):
            builtin_registry().require_capability('session.trade.top_k',mode)

    def test_target_boundary_and_auction_evidence(self):
        self.error(ErrorCode.BOUNDS,lambda:calc(trades(event_ns=(110,130,200))))
        b=trades(event_ns=(110,130,200));c=cfg();c=replace(c,session=replace(c.session,include_closing_auction=True))
        b=replace(b,columns=b.columns+(Column('condition',('none','none','closing_auction')),),metadata=replace(b.metadata,scope=replace(b.metadata.scope,include_closing_auction=True)))
        r=calc(b,c);self.assertEqual(r.evidence[0].boundary,'closing_auction')
