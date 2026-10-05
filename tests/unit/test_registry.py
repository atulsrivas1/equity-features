"""Frozen scope, metadata semantics and caller-scoped immutability fixtures."""
from dataclasses import FrozenInstanceError, replace
import json
import unittest
from equity_feature_contracts import (
    Capabilities, ContractError, DataKind, ErrorCode, FeatureDefinition,
    InputRequirement, OutputField, Registry, builtin_registry,
)
from equity_features.registry import builtin_registry as feature_registry

EXPECTED = (
"session.bar.open","session.bar.high","session.bar.low","session.bar.close","session.bar.volume","session.bar.notional","session.bar.close_weighted_price",
"session.price.open_close_return","session.price.range_fraction","session.price.close_location","session.price.overnight_gap","session.price.close_close_return",
"session.structure.interval_ohlcv","session.structure.interval_volume_share",
"session.trade.count","session.trade.volume","session.trade.notional","session.trade.vwap","session.trade.mean_size","session.trade.top_k",
"session.quote.sampled_spread","session.quote.state_counts","session.quote.time_weighted_spread",
"history.return","history.sma","history.ema","history.rsi","history.atr","history.prior_high","history.prior_low","history.return_volatility",
"baseline.daily_volume","baseline.relative_volume","baseline.interval_volume","baseline.interval_relative_volume","relative.market_return","relative.sector_return","breadth.direction_counts","breadth.above_sma_fraction")

def custom(feature_id="demo:mean"):
    return FeatureDefinition(feature_id,"caller synthetic mean",(InputRequirement("daily","canonical:1",("close",),DataKind.DAILY),),(OutputField("value","float64","currency/share"),),"sum(closes)/N","N complete governed closes","end<=C and known_at<=K","unavailable scalar null","caller:specification",(2,))

class RegistryDefinitions(unittest.TestCase):
    def assertCode(self,code,call):
        with self.assertRaises(ContractError) as caught:call()
        self.assertEqual(caught.exception.code,code)
    def test_exact_frozen_scope(self):
        definitions=builtin_registry().list_features();self.assertEqual(tuple(x.feature_id for x in definitions),EXPECTED)
        self.assertEqual(len(set(EXPECTED)),39);self.assertEqual(feature_registry().list_features(),definitions)
    def test_all_definitions_have_contracts(self):
        for d in builtin_registry().list_features():
            with self.subTest(feature=d.feature_id):
                self.assertTrue(d.requirements and d.outputs and d.formula and d.warmup and d.timing and d.missing_policy)
                self.assertEqual(d.schema_version,"1");self.assertEqual(d.algorithm_version,"v1")
                self.assertEqual(FeatureDefinition.from_json(d.to_json()),d)
    def test_exact_implemented_capabilities(self):
        registry=builtin_registry()
        self.assertEqual(tuple(x.feature_id for x in registry.list_features(capability="batch")),EXPECTED[:26]+EXPECTED[28:30])
        self.assertEqual(tuple(x.feature_id for x in registry.list_features(capability="merge")),EXPECTED[:22])
        for d in registry.list_features():
            self.assertEqual(d.capabilities,Capabilities(batch=d.feature_id in EXPECTED[:26]+EXPECTED[28:30],update=d.feature_id in EXPECTED[:23],restore=d.feature_id in EXPECTED[:23],merge=d.feature_id in EXPECTED[:22]))
        for feature in EXPECTED[:23]:
            registry.require_capability(feature,"batch");registry.require_capability(feature,"update");registry.require_capability(feature,"restore")
        for mode in ("merge",):
            self.assertCode(ErrorCode.UNSUPPORTED_CAPABILITY,lambda:registry.require_capability("session.quote.time_weighted_spread",mode))
    def test_family_selection(self):
        self.assertEqual(len(builtin_registry().list_features(family="history")),8)
        self.assertEqual(len(builtin_registry().list_features(family="session.quote")),3)
        self.assertEqual(builtin_registry().list_features(family="unknown"),())
    def test_unknown_feature_and_mode(self):
        self.assertCode(ErrorCode.UNKNOWN_FEATURE,lambda:builtin_registry().get("missing"))
        self.assertCode(ErrorCode.INVALID_CONFIG,lambda:builtin_registry().list_features(capability="live"))
    def test_prior_only_history_and_baseline(self):
        r=builtin_registry();self.assertEqual(r.get("history.prior_high").default_periods,(20,60,252))
        self.assertIn("target excluded",r.get("history.prior_high").warmup)
        self.assertEqual(r.get("baseline.daily_volume").default_periods,(20,));self.assertIn("/N",r.get("baseline.daily_volume").formula)
        self.assertIn("target excluded",r.get("baseline.daily_volume").warmup)
    def test_return_and_volatility_coverage(self):
        r=builtin_registry();self.assertEqual(r.get("history.return").default_periods,(1,5,20,60,252))
        self.assertIn("h+1",r.get("history.return").warmup)
        v=r.get("history.return_volatility");self.assertIn("N+1",v.warmup);self.assertIn("N-1",v.warmup);self.assertIn("default1",v.warmup)
    def test_recursive_initialization_and_flat_rsi(self):
        r=builtin_registry()
        for name in ("history.ema","history.rsi","history.atr"):self.assertIn("anchor",r.get(name).initialization)
        self.assertIn("flat seed50",r.get("history.rsi").warmup)
        self.assertIn("no automatic restart",r.get("history.ema").warmup)
        self.assertIn("previous close",r.get("history.atr").requirements[0].rule)
    def test_trade_vwap_distinct_from_proxy(self):
        r=builtin_registry();self.assertNotEqual(r.get("session.trade.vwap").formula,r.get("session.bar.close_weighted_price").formula)
        self.assertIn("proxy",r.get("session.bar.close_weighted_price").outputs[0].unit)
        self.assertIn("event_id",r.get("session.trade.top_k").formula)
    def test_quote_sampling_and_duration_schema(self):
        r=builtin_registry();self.assertEqual(r.get("session.quote.sampled_spread").requirements[0].sampling,"sampled_or_continuous")
        weighted=r.get("session.quote.time_weighted_spread");self.assertEqual(weighted.requirements[0].sampling,"continuous")
        self.assertIn("max_age_ns",weighted.warmup);self.assertEqual([(x.name,x.dtype) for x in weighted.outputs],[("value","time_weighted_spread")])
    def test_breadth_partial_denominator(self):
        d=builtin_registry().get("breadth.above_sma_fraction")
        self.assertIn("K/E",d.formula);self.assertIn("never K/M",d.formula);self.assertEqual(d.outputs[0].dtype,"breadth_fraction")
        self.assertIn("partial structured",d.missing_policy)
    def test_scoped_custom_registry_is_immutable(self):
        original=Registry("demo");new=original.with_definition(custom())
        self.assertEqual(len(original.list_features()),39);self.assertEqual(len(new.list_features()),40)
        self.assertEqual(new.get("demo:mean"),custom());self.assertEqual(len(new.list_features(family="demo")),1)
        self.assertCode(ErrorCode.UNKNOWN_FEATURE,lambda:Registry("other").get("demo:mean"))
    def test_reserved_and_duplicate_ids(self):
        self.assertCode(ErrorCode.DUPLICATE,lambda:Registry("demo").with_definition(replace(custom(),feature_id="history.sma")))
        self.assertCode(ErrorCode.DUPLICATE,lambda:Registry("demo",(custom(),custom())))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY,lambda:Registry("demo").with_definition(custom("other:mean")))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY,lambda:Registry("demo").with_definition(custom("session.new")))
    def test_namespace_admission(self):
        for name in ("", "UPPER", "demo:bad", "bad space"):
            self.assertCode(ErrorCode.INVALID_CONFIG,lambda:Registry(name))
    def test_schema_field_validation(self):
        self.assertCode(ErrorCode.INCOMPATIBLE_VERSION,lambda:InputRequirement("x","unknown:1",()))
        self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:InputRequirement("x","canonical:1",("wrong",),DataKind.DAILY))
        self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:InputRequirement("x","result:1",("wrong",)))
        self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:OutputField("x","object","unit"))
        self.assertCode(ErrorCode.UNSUPPORTED_SAMPLING,lambda:InputRequirement("x","canonical:1",("close",),DataKind.DAILY,"continuous"))
    def test_execution_claim_rejected(self):
        self.assertCode(ErrorCode.UNSUPPORTED_CAPABILITY,lambda:replace(custom(),capabilities=Capabilities(batch=True)))
        self.assertCode(ErrorCode.UNSUPPORTED_CAPABILITY,lambda:replace(custom(),capabilities=Capabilities(update=True)))
    def test_definition_metadata_negatives(self):
        d=custom();self.assertCode(ErrorCode.INCOMPATIBLE_VERSION,lambda:replace(d,schema_version="2"))
        self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:replace(d,requirements=()))
        self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:replace(d,formula=lambda:None))
        self.assertCode(ErrorCode.DUPLICATE,lambda:replace(d,outputs=d.outputs+d.outputs))
        self.assertCode(ErrorCode.INVALID_CONFIG,lambda:replace(d,default_periods=(True,)))
    def test_owned_metadata_and_no_global_mutation(self):
        definitions=[custom()];r=Registry("demo",definitions);definitions.clear();self.assertEqual(len(r.custom),1)
        with self.assertRaises(FrozenInstanceError):r.custom[0].formula="changed"
        self.assertEqual(builtin_registry().get("history.sma").algorithm_version,"v1")
    def test_no_lazy_definition_containers(self):
        def lazy():raise AssertionError("source executed");yield custom()
        self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:Registry("demo",lazy()))
        self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:replace(custom(),requirements=lazy()))
    def test_registry_json_round_trip(self):
        r=Registry("demo").with_definition(custom());parsed=Registry.from_json(r.to_json())
        self.assertEqual(parsed,r);self.assertEqual(parsed.to_json(),r.to_json());self.assertEqual(parsed.list_features(),r.list_features())
    def test_json_versions_and_builtin_snapshot(self):
        raw=json.loads(Registry().to_json())
        for field,value in (("schema_version","2"),("builtin_scope_version","2"),("builtin_digest","0"*64)):
            bad={**raw,field:value};self.assertCode(ErrorCode.INCOMPATIBLE_VERSION,lambda:Registry.from_json(json.dumps(bad)))
        self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:Registry.from_json(json.dumps({**raw,"unknown":True})))
    def test_json_duplicate_and_malformed_metadata(self):
        self.assertCode(ErrorCode.DUPLICATE,lambda:Registry.from_json('{"schema_version":"1","schema_version":"1"}'))
        self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:FeatureDefinition.from_json("{"))
        raw=json.loads(custom().to_json());raw["capabilities"]["batch"]=True
        self.assertCode(ErrorCode.UNSUPPORTED_CAPABILITY,lambda:FeatureDefinition.from_json(json.dumps(raw)))

if __name__ == "__main__":unittest.main()
