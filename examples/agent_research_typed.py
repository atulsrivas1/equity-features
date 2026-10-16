"""Typed pure consumer/replay usage; the calculator is an explicit optional import."""
from __future__ import annotations
from dataclasses import asdict
import json
from agent_research import Assessment,ReplayObservation,ResearchExampleError,assess,replay,fixture,expected_reports
from equity_feature_contracts import CanonicalBatch,ConfigSpec,FeatureResult
from equity_feature_evidence import canonical_content


def consume(configuration: ConfigSpec, inputs: tuple[tuple[str,CanonicalBatch],...],
            producer: FeatureResult, receipt: bytes | None, explanation: bytes | None,
            diagnostics: bytes | None, narrative: str) -> Assessment:
    return assess(configuration,inputs,producer,receipt,explanation,diagnostics,narrative)


def demonstrate() -> tuple[Assessment,ReplayObservation]:
    # Acquisition, optional computation and publication belong to this caller.
    # Nothing is fetched; fixture() is a literal caller-owned synthetic example.
    from equity_features.session import compute_trades
    from equity_feature_contracts import EntityKey
    configuration,batch,expected=fixture()
    actual=compute_trades(batch,configuration,entity=EntityKey('A','S'))
    if canonical_content(actual)!=canonical_content(expected):
        raise ResearchExampleError('inconsistent_evidence')
    receipt,explanation,diagnostics=expected_reports()
    assessment=consume(configuration,(('trades',batch),),actual,receipt,explanation,diagnostics,'session.trade.count=3')
    observed=replay(configuration,(('trades',batch),),actual,receipt,explanation,diagnostics,'session.trade.count=3')
    return assessment,observed


if __name__=='__main__':
    assessment,replayed=demonstrate()
    print(json.dumps(dict(assessment=asdict(assessment),replay=asdict(replayed)),sort_keys=True,separators=(',',':')))
