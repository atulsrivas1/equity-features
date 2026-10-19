"""Original supplied-data preparation and selected batch snapshots; no acquisition."""
from fractions import Fraction
from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, Coverage,
    DataKind, InputScope, IntervalCoverage, PriceUnit, SessionSpec, SourceBinding,
)
from equity_features_intraday import IntradayContext, IntradayRun, build_intraday_config, prepare_intraday, compute_intraday


def example() -> None:
    context=IntradayContext('A','synthetic-calendar','ten-ns-grid','revision1',
        (SessionSpec('synthetic','S',0,100,'UTC'),),(IntradayRun('S',0,10,3),),0,2,'reset')
    config=build_intraday_config(context,period=3,band_k=Fraction(2),
        availability=AvailabilitySpec(30,30,30),adjustment=AdjustmentSpec(),price_unit=PriceUnit(0,'USD'))
    batch=CanonicalBatch(DataKind.BAR,(
        Column('instrument_id',('A','A','A')),Column('session_id',('S','S','S')),
        Column('start_ns',(0,10,20)),Column('end_ns',(10,20,30)),
        Column('known_at_ns',(10,20,30)),Column('close',(10,12,11))),
        BatchMetadata('synthetic',SourceBinding('synthetic','snap1','map1','input1'),Coverage(3,3,True),
            PriceUnit(0,'USD'),scope=InputScope(0,30,'synthetic-v1'),
            interval_coverage=tuple(IntervalCoverage(f'slot:{i}',i*10,(i+1)*10,Coverage(1,1,True)) for i in range(3))))
    prepared=prepare_intraday((batch,),context,config,requirements=('price_moments','anchored_closes'))
    assert prepared.operand('price_moments').values==(Fraction(11),Fraction(2,3),Fraction(0))
    assert prepared.operand('anchored_closes').values==(Fraction(10),Fraction(12),Fraction(11))
    result=compute_intraday((batch,),context,config,features=('intraday.ema','intraday.band_middle','intraday.band_position'),preparation=prepared)
    assert {column.feature_id:column.values[0] for column in result.values}=={
        'intraday.band_middle':11.0,'intraday.band_position':0.5,'intraday.ema':11.0}
    assert result.metadata.backend_version=='0.1.0a3'


if __name__=='__main__':example()
