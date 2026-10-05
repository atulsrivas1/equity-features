"""BUG003 independent omission/re-certification goldens (synthetic whole bars)."""
from dataclasses import replace
import unittest
from equity_feature_contracts import ContractError, Coverage, ErrorCode, PartitionSpan, PrefixCoverage, Status, StreamPopulation
from equity_features.incremental import SessionAccumulator
from test_incremental import fixture, structure_config, ENTITY, chunk
from test_state import changed, restore


def fresh():
    b=fixture()
    p=StreamPopulation(b.kind,tuple(x.name for x in b.columns),replace(b.metadata,coverage=Coverage(None,0,False),interval_coverage=()))
    return SessionAccumulator('structure',structure_config(),entity=ENTITY,population=p),b


def missing(a,b):
    a.update(chunk(b,[0]),start_ordinal=0)
    a.snapshot(PrefixCoverage(150,Coverage(None,1,False),(replace(b.metadata.interval_coverage[0],coverage=Coverage(2,1,False)),)))


class IntervalOmissions(unittest.TestCase):
    def reject_unchanged(self,a,call):
        before=a.export_state()
        with self.assertRaises(ContractError) as caught: call()
        self.assertEqual(caught.exception.code,ErrorCode.INCONSISTENT_IDENTITY)
        self.assertEqual(a.export_state(),before)

    def test_original_direct_and_restored_recertification_rejects(self):
        for resumed in (False,True):
            with self.subTest(restored=resumed):
                a,b=fresh();missing(a,b)
                if resumed: a=restore(a)
                a.update(chunk(b,[1]),start_ordinal=1)
                self.reject_unchanged(a,lambda:a.finalize(PrefixCoverage(200,Coverage(2,2,True),b.metadata.interval_coverage)))
                self.reject_unchanged(a,lambda:a.snapshot(PrefixCoverage(200,Coverage(None,2,False),b.metadata.interval_coverage)))

    def test_omitted_or_lowered_incomplete_certificate_preserves_gap_and_other_window(self):
        for first in ((),(replace(fixture().metadata.interval_coverage[0],coverage=Coverage(1,1,False)),)):
            a,b=fresh();missing(a,b);a=restore(a);a.update(chunk(b,[1]),start_ordinal=1)
            cert=PrefixCoverage(200,Coverage(None,2,False),first+(b.metadata.interval_coverage[1],))
            r=a.snapshot(cert);rows=r.values[0].values[0].rows
            self.assertIsNone(rows[0].volume);self.assertEqual(rows[0].quality.status,Status.INCOMPLETE_COVERAGE)
            self.assertEqual(rows[1].volume,300);self.assertEqual(rows[1].quality.status,Status.AVAILABLE)
            self.assertTrue(all(x.share is None for x in r.values[1].values[0].rows))
            self.assertEqual(restore(a).export_state(),a.export_state())
            self.reject_unchanged(a,lambda:a.finalize(PrefixCoverage(200,Coverage(2,2,True),())))

    def test_new_interval_gap_cannot_contradict_complete_whole_atomically(self):
        a,b=fresh();a.update(b,start_ordinal=0)
        intervals=(replace(b.metadata.interval_coverage[0],coverage=Coverage(2,1,False)),b.metadata.interval_coverage[1])
        self.reject_unchanged(a,lambda:a.finalize(PrefixCoverage(200,Coverage(2,2,True),intervals)))
        self.assertEqual(a._state.window_gaps,(False,False))

    def test_chunk_local_omission_survives_legal_merge_and_restore(self):
        a,b=fresh();other,_=fresh()
        left=chunk(b,[0]);left=replace(left,metadata=replace(left.metadata,interval_coverage=(replace(b.metadata.interval_coverage[0],coverage=Coverage(2,1,False)),)))
        a.update(left,start_ordinal=0);other.update(chunk(b,[1]),start_ordinal=0)
        before=(a.export_state(),other.export_state())
        merged=a.merge_partitions(other,left=PartitionSpan(0,1),right=PartitionSpan(1,2))
        self.assertEqual(merged._state.window_gaps,(True,False));merged=restore(merged)
        self.reject_unchanged(merged,lambda:merged.finalize(PrefixCoverage(200,Coverage(2,2,True),b.metadata.interval_coverage)))
        cert=PrefixCoverage(200,Coverage(None,2,False),(replace(b.metadata.interval_coverage[0],coverage=Coverage(2,1,False)),b.metadata.interval_coverage[1]))
        self.assertEqual(merged.finalize(cert).values[0].values[0].rows[1].volume,300)
        self.assertEqual(before,(a.export_state(),other.export_state()))

    def test_rehashed_gap_shape_boolean_and_consistency_reject(self):
        a,b=fresh();missing(a,b);s=a.export_state()
        for fn in (lambda d:d.update(window_gaps=[]),lambda d:d.update(window_gaps=[1,False]),lambda d:d.update(known_gap=False)):
            with self.subTest(mutation=fn):
                with self.assertRaises(ContractError) as caught:restore(a,changed(s,fn))
                self.assertEqual(caught.exception.code,ErrorCode.INVALID_SCHEMA)
                self.assertEqual(a.export_state(),s)
        with self.assertRaises(ContractError):restore(a,replace(s,schema_version='1'))

    def test_unknown_without_omission_can_be_certified_complete(self):
        a,b=fresh();a.update(chunk(b,[0]),start_ordinal=0)
        a.snapshot(PrefixCoverage(150,Coverage(None,1,False),(replace(b.metadata.interval_coverage[0],coverage=Coverage(None,1,False)),)))
        a.update(chunk(b,[1]),start_ordinal=1)
        r=a.finalize(PrefixCoverage(200,Coverage(2,2,True),b.metadata.interval_coverage))
        self.assertEqual([x.volume for x in r.values[0].values[0].rows],[200,300])
        self.assertEqual([x.share for x in r.values[1].values[0].rows],[.4,.6])

    def test_fixed_population_expected_interval_cannot_change(self):
        b=fixture();a=SessionAccumulator('structure',structure_config(),entity=ENTITY,population=StreamPopulation.from_batch(b));a.update(b,start_ordinal=0)
        intervals=(replace(b.metadata.interval_coverage[0],coverage=Coverage(2,1,False)),b.metadata.interval_coverage[1])
        self.reject_unchanged(a,lambda:a.snapshot(PrefixCoverage(200,Coverage(None,2,False),intervals)))
