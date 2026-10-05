"""Exact resumed execution and adversarial state schema/compatibility admission."""
from dataclasses import asdict, replace
import hashlib
import json
import unittest
from equity_feature_contracts import AccumulatorState, ContractError, Coverage, PrefixCoverage, StreamPopulation
from equity_features.incremental import SessionAccumulator
from test_incremental import accumulator,chunk,certificate,ENTITY,batch,config,prior,fixture,structure_config,trades,top_config,quotes,quote_config,updates,continuous_config,seed

CASES=(('bars',batch,config,{}),('structure',fixture,structure_config,{}),('trades',trades,config,{}),('top_k',trades,top_config,{}),('quotes',quotes,quote_config,{}),('continuous',updates,continuous_config,{}))

def changed(state,fn):
    raw=json.loads(state.payload);fn(raw);payload=json.dumps(raw,sort_keys=True,separators=(',',':'),ensure_ascii=True)
    return replace(state,payload=payload,payload_digest=hashlib.sha256(payload.encode()).hexdigest())

def restore(a,state=None,**extra):
    return SessionAccumulator.restore_state(a.export_state() if state is None else state,a.family,a.config,entity=a.entity,population=a.population,prior_close=a._prior_close,seed=a._seed,**extra)

class State(unittest.TestCase):
    def bad(self,a,state):
        with self.assertRaises(ContractError):restore(a,state)

    def test_all_families_every_split_exact_resumed_result(self):
        for family,bf,cf,extra in CASES:
            b=bf();c=cf()
            for split in range(b.row_count+1):
                with self.subTest(family=family,split=split):
                    a=accumulator(family,b,c,**extra);a.update(chunk(b,list(range(split))),start_ordinal=0)
                    state=a.export_state();r=restore(a);self.assertEqual(r.export_state(),state)
                    tail=chunk(b,list(range(split,b.row_count)))
                    a.update(tail,start_ordinal=split);r.update(tail,start_ordinal=split)
                    self.assertEqual(asdict(a.finalize(certificate(b))),asdict(r.finalize(certificate(b))))

    def test_seed_original_anchor_and_prior_fingerprints(self):
        for family,b,c,extra in (('continuous',updates(),continuous_config(initial='seed'),{'seed':seed()}),('bars',batch(),config(),{'prior_close':prior()})):
            a=accumulator(family,b,c,**extra);a.update(chunk(b,[0]),start_ordinal=0);r=restore(a)
            for i in range(1,b.row_count):
                a.update(chunk(b,[i]),start_ordinal=i);r.update(chunk(b,[i]),start_ordinal=i)
            self.assertEqual(asdict(a.finalize(certificate(b))),asdict(r.finalize(certificate(b))))
            with self.assertRaises(ContractError):SessionAccumulator.restore_state(r.export_state(),family,c,entity=ENTITY,population=r.population)

    def test_snapshotted_temporal_exact_expiry_and_binary64_pair(self):
        b=updates();a=accumulator('continuous',b,continuous_config());a.update(chunk(b,[0]),start_ordinal=0)
        a.snapshot(PrefixCoverage(101,Coverage(1,1,True)));r=restore(a)
        self.assertEqual(a._state.temporal.bps_sum.hex(),r._state.temporal.bps_sum.hex())
        self.assertEqual(a._state.temporal.compensation.hex(),r._state.temporal.compensation.hex())
        for i in range(1,b.row_count):
            a.update(chunk(b,[i]),start_ordinal=i);r.update(chunk(b,[i]),start_ordinal=i)
        self.assertEqual(a.finalize(certificate(b)),r.finalize(certificate(b)))

    def test_owned_state_two_restores_no_aliases(self):
        b=trades();a=accumulator('top_k',b,top_config());a.update(chunk(b,[0]),start_ordinal=0);state=a.export_state();r=restore(a);s=restore(a)
        r.update(chunk(b,[1]),start_ordinal=1)
        self.assertEqual(a.export_state(),state);self.assertEqual(s.export_state(),state)
        with self.assertRaises(Exception):state.payload='changed'

    def test_finalized_state_preserves_seal_and_result(self):
        for family,bf,cf,extra in CASES:
            b=bf();a=accumulator(family,b,cf());a.update(b,start_ordinal=0);result=a.finalize(certificate(b));r=restore(a)
            self.assertEqual(r.snapshot(certificate(b)),result)
            with self.assertRaises(ContractError):r.update(chunk(b,[]),start_ordinal=b.row_count)
            with self.assertRaises(ContractError):r.finalize(certificate(b))

    def test_permanent_gap_and_watermark_survive(self):
        b=trades();a=accumulator('trades',b,config());a.update(chunk(b,[0]),start_ordinal=0);a.snapshot(PrefixCoverage(120,Coverage(2,1,False)));r=restore(a)
        with self.assertRaises(ContractError):r.snapshot(PrefixCoverage(120,Coverage(1,1,True)))
        with self.assertRaises(ContractError):r.snapshot(PrefixCoverage(119,Coverage(2,1,False)))
        self.assertEqual(r.export_state(),a.export_state())

    def test_empty_unknown_initial_state_roundtrip(self):
        b=updates();a=accumulator('continuous',b,continuous_config(initial='unknown'));self.assertEqual(restore(a).export_state(),a.export_state())
        a.snapshot(PrefixCoverage(101,Coverage(0,0,True)));self.assertEqual(restore(a).export_state(),a.export_state())

    def test_envelope_digest_size_and_versions(self):
        a=accumulator('trades',trades(),config());s=a.export_state()
        with self.assertRaises(ContractError):replace(s,payload=s.payload+' ')
        for key,value in (('schema_version','future'),('implementation_version','future'),('binding_digest','0'*64)):
            self.bad(a,replace(s,**{key:value}))
        with self.assertRaises(ContractError):replace(s,payload='x'*(16*1024*1024+1))

    def test_config_source_entity_enrichment_changes_reject(self):
        a=accumulator('trades',trades(),config());s=a.export_state()
        for pop in (replace(a.population,fields=tuple(reversed(a.population.fields))),replace(a.population,metadata=replace(a.population.metadata,source=replace(a.population.metadata.source,snapshot_id='other')))):
            with self.assertRaises(ContractError):SessionAccumulator.restore_state(s,'trades',config(),entity=ENTITY,population=pop)
        with self.assertRaises(ContractError):SessionAccumulator.restore_state(s,'trades',replace(config(),identity='other'),entity=ENTITY,population=a.population)

    def test_rehashed_root_types_unknown_keys_counts_order_reject(self):
        a=accumulator('trades',trades(),config());a.update(chunk(trades(),[0]),start_ordinal=0);s=a.export_state()
        mutations=(lambda d:d.update(extra=1),lambda d:d.update(observed=True),lambda d:d.update(observed=-1),lambda d:d.update(bound=201),lambda d:d.update(first_key=[190,9]),lambda d:d.update(last_key=None),lambda d:d.update(last_event_id=''),lambda d:d.update(knowledge=['absent_input']),lambda d:d['trades'].update(observed=0),lambda d:d['trades'].update(eligible=2),lambda d:d['trades']['volume'].update(value=-1),lambda d:d['trades']['volume'].update(overflow=True))
        for fn in mutations:
            with self.subTest(fn=fn):self.bad(a,changed(s,fn))

    def test_duplicate_keys_truncated_noncanonical_and_nonfinite_reject(self):
        a=accumulator('trades',trades(),config());s=a.export_state()
        for payload in (s.payload[:-1],'{"bound":100,"bound":100}',json.dumps(json.loads(s.payload),indent=1)):
            self.bad(a,replace(s,payload=payload,payload_digest=hashlib.sha256(payload.encode()).hexdigest()))
        a=accumulator('quotes',quotes(),quote_config());s=a.export_state()
        for value in ({'binary64':'inf'},{'binary64':'nan'},0.5):self.bad(a,changed(s,lambda d:d['quotes'].update(bps_sum=value)))

    def test_top_rank_retention_input_identity_reject(self):
        b=trades();a=accumulator('top_k',b,top_config());a.update(b,start_ordinal=0);s=a.export_state()
        for fn in (lambda d:d['top'].update(rows=[]),lambda d:d['top']['rows'].reverse(),lambda d:d['top']['rows'][0].update(input_id='other'),lambda d:d['top'].update(k=10001)):
            self.bad(a,changed(s,fn))

    def test_quote_counts_diagnostics_retention_reject(self):
        b=quotes();a=accumulator('quotes',b,quote_config());a.update(b,start_ordinal=0);s=a.export_state()
        for fn in (lambda d:d['quotes']['counts'].update(normal=100),lambda d:d['quotes'].update(rows=[]),lambda d:d['quotes']['rows'][0].update(spread={'binary64':'0x1.0000000000000p+4'}),lambda d:d['quotes'].update(limit=True)):
            self.bad(a,changed(s,fn))

    def test_temporal_conservation_cursor_anchor_and_config_reject(self):
        b=updates();a=accumulator('continuous',b,continuous_config());a.update(chunk(b,[0,1]),start_ordinal=0);s=a.export_state()
        for fn in (lambda d:d['temporal']['duration'].update(normal=999),lambda d:d['temporal'].update(cursor=100),lambda d:d['temporal'].update(anchor=999),lambda d:d['temporal'].update(max_age_ns=1),lambda d:d['temporal'].update(bps_sum={'binary64':'-0x1.0000000000000p+0'})):
            self.bad(a,changed(s,fn))

    def test_window_and_null_flags_roundtrip(self):
        b=fixture();a=accumulator('structure',b,structure_config());a.update(chunk(b,[0]),start_ordinal=0);self.assertEqual(a.export_state(),restore(a).export_state())
        self.bad(a,changed(a.export_state(),lambda d:d['windows'].append(d['windows'][0])))
        b=batch();b=replace(b,columns=tuple(x for x in b.columns if x.name!='close'));a=accumulator('bars',b,config());a.update(b,start_ordinal=0);self.assertEqual(a.export_state(),restore(a).export_state())

    def test_overflow_flag_and_incomplete_state_restored_without_false_ready(self):
        from equity_feature_contracts.inputs import I64_MAX
        b=trades(size=(I64_MAX,I64_MAX,2));a=accumulator('trades',b,config());a.update(b,start_ordinal=0)
        a.snapshot(PrefixCoverage(200,Coverage(3,3,False)));r=restore(a)
        self.assertTrue(r._state.trades.volume.overflow)
        with self.assertRaises(ContractError):r.snapshot(certificate(b))
        self.assertEqual(a.export_state(),r.export_state())

    def test_missing_fields_and_future_knowledge_state_remain_unavailable(self):
        from equity_feature_contracts import Column
        for b in (replace(quotes(),columns=tuple(c for c in quotes().columns if c.name!='ask')),replace(quotes(),columns=tuple(Column(c.name,(300,)*quotes().row_count) if c.name=='known_at_ns' else c for c in quotes().columns))):
            a=accumulator('quotes',b,quote_config());a.update(b,start_ordinal=0);r=restore(a)
            self.assertEqual(a.finalize(certificate(b)),r.finalize(certificate(b)))

    def test_bounded_state_after_many_chunks(self):
        b=trades();a=accumulator('trades',b,config());a.update(b,start_ordinal=0)
        raw=json.loads(a.export_state().payload)
        self.assertNotIn('columns',raw);self.assertEqual(set(raw['trades']),{'fields','observed','knowledge','eligible','volume','notional'})
        self.bad(a,changed(a.export_state(),lambda d:d['trades'].update(raw_rows=[1,2,3])))

if __name__=='__main__':unittest.main()
