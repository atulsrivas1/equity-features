"""Independent whole-interval expectations, coverage and structured admission."""
from dataclasses import replace
import unittest
from equity_feature_contracts import (
    Column, ContractError, Coverage, ErrorCode, FeatureResult, InputScope,
    IntervalCoverage, IntervalOHLCV, IntervalOHLCVRow, IntervalSpec,
    IntervalVolumeShares, QualityRow, Reason, Status,
)
from equity_feature_contracts.columnar import from_arrow, to_arrow, to_arrow_result
import pyarrow as pa
from equity_features.session import compute_structure
from test_bars import ENTITY, batch, config

WINDOWS=(IntervalSpec("first",100,150),IntervalSpec("last",150,200))

def fixture(**changes):
    b=batch(**changes)
    return replace(b,metadata=replace(b.metadata,interval_coverage=tuple(IntervalCoverage(w.name,w.start_ns,w.end_ns,Coverage(1,1,True)) for w in WINDOWS)))

def cfg(intervals=WINDOWS,**changes):
    c=config(**changes);return replace(c,session=replace(c.session,intervals=intervals))

def calc(b=None,c=None):return compute_structure(b,cfg() if c is None else c,entity=ENTITY)
def table(r,idx=0):return r.values[idx].values[0]

class Structure(unittest.TestCase):
    def error(self,code,call):
        with self.assertRaises(ContractError) as caught:call()
        self.assertEqual(caught.exception.code,code)

    def test_independent_two_window_golden(self):
        r=calc(fixture());rows=table(r).rows;shares=table(r,1).rows
        self.assertEqual([(x.open_price,x.high_price,x.low_price,x.close_price,x.volume) for x in rows],[(100.,103.,99.,102.,200),(102.,104.,101.,103.,300)])
        self.assertEqual([x.share for x in shares],[.4,.6]);self.assertTrue(all(x.status==Status.AVAILABLE for x in r.quality))
        self.assertEqual(r.metadata.config_digest,cfg().digest)

    def test_missing_source_is_null_not_empty_table(self):
        r=calc();self.assertEqual([x.values for x in r.values],[(None,),(None,)])
        self.assertTrue(all(q.status==Status.MISSING_INPUT for q in r.quality))

    def test_missing_declaration_cannot_infer_window_coverage(self):
        r=calc(batch());self.assertTrue(all(x.quality.status==Status.INCOMPLETE_COVERAGE and x.volume is None for x in table(r).rows))
        self.assertTrue(all(x.share is None for x in table(r,1).rows))

    def test_window_ready_independent_of_target_coverage(self):
        b=fixture();b=replace(b,metadata=replace(b.metadata,coverage=Coverage(3,2,False)))
        r=calc(b);self.assertEqual(table(r).rows[0].volume,200)
        self.assertIsNone(table(r,1).rows[0].share)
        self.assertEqual(table(r,1).rows[0].quality.status,Status.INCOMPLETE_COVERAGE)

    def test_one_window_missing_does_not_erase_another(self):
        b=fixture();b=replace(b,metadata=replace(b.metadata,interval_coverage=b.metadata.interval_coverage[:1]))
        r=calc(b);self.assertEqual(table(r).rows[0].volume,200);self.assertIsNone(table(r).rows[1].volume)
        self.assertEqual(r.quality[0].observed,1);self.assertEqual(r.quality[0].expected,2)

    def test_future_knowledge_only_poison_its_window(self):
        r=calc(fixture(known_at_ns=(150,211)))
        self.assertEqual(table(r).rows[0].close_price,102.);self.assertIsNone(table(r).rows[1].volume)
        self.assertEqual(table(r).rows[1].quality.reasons,(Reason.FUTURE_KNOWLEDGE,))
        self.assertIsNone(table(r,1).rows[0].share)  # unavailable whole target

    def test_straddling_bars_never_prorated(self):
        self.error(ErrorCode.BOUNDS,lambda:calc(batch(),cfg((IntervalSpec("unaligned",120,150),))))

    def test_missing_expected_window_is_explicit(self):
        b=fixture();declarations=(b.metadata.interval_coverage[0],replace(b.metadata.interval_coverage[1],coverage=Coverage(2,1,False)))
        r=calc(replace(b,metadata=replace(b.metadata,interval_coverage=declarations)))
        self.assertEqual(table(r).rows[0].volume,200);self.assertEqual(table(r).rows[1].quality.expected,2)
        self.assertIsNone(table(r).rows[1].volume)

    def test_empty_covered_windows_have_volume_zero(self):
        b=fixture();b=replace(b,columns=tuple(Column(c.name,()) for c in b.columns),metadata=replace(b.metadata,coverage=Coverage(0,0,True),interval_coverage=tuple(replace(x,coverage=Coverage(0,0,True)) for x in b.metadata.interval_coverage)))
        r=calc(b);self.assertEqual([x.volume for x in table(r).rows],[0,0]);self.assertEqual(table(r).rows[0].open_price,None)
        self.assertEqual(table(r,1).rows[0].quality.reasons,(Reason.ZERO_DENOMINATOR,))

    def test_zero_and_nonzero_windows_share_correct_denominator(self):
        r=calc(fixture(open=(None,102),high=(None,104),low=(None,101),close=(None,103),volume=(0,300),actual_notional=(None,30900)))
        self.assertEqual([x.share for x in table(r,1).rows],[0.,1.]);self.assertEqual(table(r).rows[0].volume,0)

    def test_early_close_and_auction_policy(self):
        c=cfg();c=replace(c,session=replace(c.session,scheduled_close_ns=250,early_close=True,include_opening_auction=True,include_closing_auction=True))
        b=fixture();b=replace(b,metadata=replace(b.metadata,scope=replace(b.metadata.scope,include_opening_auction=True,include_closing_auction=True)))
        r=calc(b,c);self.assertEqual([x.share for x in table(r,1).rows],[.4,.6])

    def test_after_cutoff_interval_never_leaks(self):
        c=cfg();c=replace(c,availability=replace(c.availability,market_cutoff_ns=150))
        b=fixture();b=replace(b,columns=tuple(Column(x.name,x.values[:1]) for x in b.columns),metadata=replace(b.metadata,coverage=Coverage(1,1,True),scope=InputScope(100,150,"synthetic-v1"),interval_coverage=b.metadata.interval_coverage[:1]))
        r=calc(b,c);self.assertEqual(table(r).rows[0].volume,200);self.assertIsNone(table(r).rows[1].volume)
        self.assertEqual(table(r,1).rows[0].share,1.)

    def test_overlapping_windows_are_independent(self):
        w=IntervalSpec("whole",100,200);b=fixture();b=replace(b,metadata=replace(b.metadata,interval_coverage=b.metadata.interval_coverage+(IntervalCoverage("whole",100,200,Coverage(2,2,True)),)))
        r=calc(b,cfg(WINDOWS+(w,)));self.assertEqual([x.share for x in table(r,1).rows],[.4,.6,1.])

    def test_window_population_and_identity_errors(self):
        b=fixture()
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:calc(replace(b,metadata=replace(b.metadata,interval_coverage=(replace(b.metadata.interval_coverage[0],coverage=Coverage(2,2,True)),)))))
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:calc(replace(b,metadata=replace(b.metadata,interval_coverage=(replace(b.metadata.interval_coverage[0],name="unknown"),)))))
        self.error(ErrorCode.INVALID_CONFIG,lambda:calc(b,cfg(())))

    def test_input_coverage_ownership_bounds_and_duplicates(self):
        self.error(ErrorCode.DUPLICATE,lambda:replace(fixture().metadata,interval_coverage=(fixture().metadata.interval_coverage[0],)*2))
        self.error(ErrorCode.BOUNDS,lambda:replace(fixture().metadata,interval_coverage=(IntervalCoverage("outside",0,150,Coverage(1,1,True)),)))
        self.error(ErrorCode.INVALID_SCHEMA,lambda:replace(fixture().metadata,interval_coverage=iter(())))

    def test_structured_partial_types_and_consistency(self):
        q=QualityRow(ENTITY,'session.structure.interval_ohlcv',Status.AVAILABLE,0,0)
        rows=[IntervalOHLCVRow(WINDOWS[0],None,None,None,None,0,q)];t=IntervalOHLCV(rows);rows.clear();self.assertEqual(len(t.rows),1)
        self.error(ErrorCode.DUPLICATE,lambda:IntervalOHLCV(t.rows+t.rows))
        self.error(ErrorCode.INVALID_SCHEMA,lambda:IntervalOHLCV(iter(t.rows)))
        self.error(ErrorCode.INVALID_SCHEMA,lambda:replace(t.rows[0],volume=1))
        r=calc(fixture());self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:replace(r,quality=(replace(r.quality[0],observed=1,status=Status.INCOMPLETE_COVERAGE,reasons=(Reason.GOVERNED_GAP,)),r.quality[1])))

    def test_arrow_nested_rows_and_scope_roundtrip(self):
        b=fixture();self.assertEqual(from_arrow(to_arrow(b)),b)
        r=calc(b);out=to_arrow_result(r)['values']
        rows=out['session.structure.interval_ohlcv'].column('value').chunks[0].flatten()
        self.assertEqual(rows.field('volume').to_pylist(),[200,300])
        self.assertEqual(rows.field('open_price').to_pylist(),[100.,102.])
        self.assertEqual(rows.field('quality').field('status').to_pylist(),['available','available'])
        self.assertEqual(rows.field('interval').field('start_ns').cast(pa.int64()).to_pylist(),[100,150])
        self.assertEqual(out['session.structure.interval_volume_share'].column('value').chunks[0].flatten().field('share').to_pylist(),[.4,.6])

if __name__=='__main__':unittest.main()
