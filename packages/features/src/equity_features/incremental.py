"""Pure bounded session update/snapshot/finalize lifecycle; callers own delivery and threading."""
from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Literal, cast
from equity_feature_contracts import (
    BatchMetadata, CanonicalBatch, Column, ConfigSpec, ContractError, Coverage,
    DataKind, EntityKey, ErrorCode, EvidenceRow, FeatureColumn, FeatureResult,
    InputBinding, InputScope, IntervalOHLCV, IntervalOHLCVRow, IntervalVolumeShares,
    IntervalVolumeShareRow, PrefixCoverage, PriceUnit, QualityRow, Reason,
    ResultMetadata, Status, StreamPopulation, ValueType, checked_int64,
)
from equity_features import __version__
from .session.bars import _admit, _columns, _prior_info, compute_bars, compute_structure
from .session.trades import _admit_trades, compute_trades
from .session.top_k import compute_top_k
from .session.quotes import _admit_quotes, compute_quotes
from .session.continuous import _TimeReducer, _admit_seed, compute_time_weighted
from .session._reductions import _BarTotals, _TradeTotals, _QuoteTotals, _TopTotals, _quote_values

Family = Literal['bars','structure','trades','top_k','quotes','continuous']

@dataclass
class _StreamState:
    bound: int
    observed: int = 0
    first_key: tuple[int,int] | None = None
    last_key: tuple[int,int] | None = None
    first_start: int | None = None
    last_start: int | None = None
    last_end: int | None = None
    last_event_id: str | None = None
    last_inclusive: bool = False
    known_gap: bool = False
    knowledge: tuple[Reason,...] = ()
    sealed: PrefixCoverage | None = None
    bars: _BarTotals | None = None
    windows: tuple[_BarTotals,...] = ()
    trades: _TradeTotals | None = None
    top: _TopTotals | None = None
    quotes: _QuoteTotals | None = None
    temporal: _TimeReducer | None = None

    def clone(self) -> _StreamState:
        return replace(self,bars=self.bars.clone() if self.bars is not None else None,windows=tuple(x.clone() for x in self.windows),trades=self.trades.clone() if self.trades is not None else None,top=self.top.clone() if self.top is not None else None,quotes=self.quotes.clone() if self.quotes is not None else None,temporal=replace(self.temporal,duration=dict(self.temporal.duration)) if self.temporal is not None else None)

class SessionAccumulator:
    """One fixed-schema/source population; no growing input bindings or raw history."""
    def __init__(self, family: Family, config: ConfigSpec, *, entity: EntityKey,
                 population: StreamPopulation, prior_close: CanonicalBatch | None = None,
                 seed: CanonicalBatch | None = None) -> None:
        if family not in ('bars','structure','trades','top_k','quotes','continuous') or type(config) is not ConfigSpec or type(entity) is not EntityKey or type(population) is not StreamPopulation:
            raise ContractError(ErrorCode.INVALID_CONFIG,'typed supported accumulator family/config/population required')
        kind=DataKind.BAR if family in ('bars','structure') else DataKind.TRADE if family in ('trades','top_k') else DataKind.QUOTE
        if population.kind != kind:
            raise ContractError(ErrorCode.INVALID_SCHEMA,'population kind/family mismatch')
        if prior_close is not None and family != 'bars' or seed is not None and family != 'continuous':
            raise ContractError(ErrorCode.INVALID_CONFIG,'enrichment/family mismatch')
        empty=CanonicalBatch(kind,tuple(Column(name,()) for name in population.fields),replace(population.metadata,coverage=Coverage(0,0,True),interval_coverage=()))
        if family == 'bars': compute_bars(empty,config,entity=entity,prior_close=prior_close)
        elif family == 'structure': compute_structure(empty,config,entity=entity)
        elif family == 'trades': compute_trades(empty,config,entity=entity)
        elif family == 'top_k': compute_top_k(empty,config,entity=entity)
        elif family == 'quotes': compute_quotes(empty,config,entity=entity)
        else: compute_time_weighted(empty,config,entity=entity,seed=seed)
        self._family=family;self._config=config;self._entity=entity;self._population=population
        self._prior_close=prior_close;self._seed=seed
        self._seed_reason: Reason | None=None;self._seed_evidence: tuple[EvidenceRow,...]=()
        self._state=_StreamState(config.session.open_ns)
        params={p.name:p.value for p in config.parameters}
        fields=population.fields
        if family in ('bars','structure'):
            self._state.bars=_BarTotals(fields)
            if family == 'structure': self._state.windows=tuple(_BarTotals(fields) for _ in config.session.intervals)
        elif family == 'trades': self._state.trades=_TradeTotals(fields)
        elif family == 'top_k': self._state.top=_TopTotals(fields,k=cast(int,params['top_k']))
        elif family == 'quotes': self._state.quotes=_QuoteTotals(fields,limit=cast(int,params['observation_limit']),scale=cast(PriceUnit,config.price_unit).scale)
        else:
            initial=cast(str,params['initial_state'])
            self._state.temporal=_TimeReducer(config.session.open_ns,cast(int,params['max_age_ns']),cast(PriceUnit,config.price_unit).scale,state='invalid' if initial == 'inactive' else 'unknown')
            if seed is None:
                self._seed_reason=Reason.ABSENT_INPUT if initial == 'seed' else None
            else:
                self._seed_reason=_admit_seed(seed,config,entity,cast(str,params['eligibility_policy']),empty)
                columns=_columns(seed);event=cast(int,columns['event_ns'][0]);known=cast(int | None,columns['known_at_ns'][0]) if 'known_at_ns' in columns else None
                if self._seed_reason is None:
                    self._state.temporal.anchor=event;self._state.temporal.bid=cast(int | None,columns['bid'][0]);self._state.temporal.ask=cast(int | None,columns['ask'][0]);self._state.temporal.state=_quote_values(self._state.temporal.bid,self._state.temporal.ask,self._state.temporal.scale)[0]
                self._seed_evidence=(EvidenceRow(entity,'session.quote.time_weighted_spread',seed.metadata.source.input_id,cast(str,columns['event_id'][0]),event,known,use='excluded' if self._seed_reason is not None else 'consumed',exclusion_reason=self._seed_reason),)

    @property
    def family(self) -> Family: return self._family
    @property
    def config(self) -> ConfigSpec: return self._config
    @property
    def entity(self) -> EntityKey: return self._entity
    @property
    def population(self) -> StreamPopulation: return self._population

    def update(self, batch: CanonicalBatch, *, start_ordinal: int) -> None:
        if self._state.sealed is not None: raise ContractError(ErrorCode.BOUNDS,'finalized accumulator rejects updates')
        if type(start_ordinal) is not int or start_ordinal != self._state.observed:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,'next contiguous population ordinal required')
        if type(batch) is not CanonicalBatch or batch.kind != self._population.kind or tuple(c.name for c in batch.columns) != self._population.fields:
            raise ContractError(ErrorCode.INVALID_SCHEMA,'fixed canonical population schema required')
        if replace(batch.metadata,coverage=self._population.metadata.coverage,interval_coverage=self._population.metadata.interval_coverage) != self._population.metadata:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,'chunk source/config scope identity mismatch; replay required')
        policy=cast(str,next(p.value for p in self._config.parameters if p.name == 'eligibility_policy'))
        if self._family in ('bars','structure'): _admit(batch,self._config,self._entity,policy)
        elif self._family in ('trades','top_k'): _admit_trades(batch,self._config,self._entity,policy)
        else: _admit_quotes(batch,self._config,self._entity,policy)
        columns=_columns(batch)
        if batch.row_count:
            if batch.kind == DataKind.BAR:
                start=cast(int,columns['start_ns'][0]);end=cast(int,columns['end_ns'][0])
                if (start,end) == (self._state.last_start,self._state.last_end): raise ContractError(ErrorCode.DUPLICATE,'repeated completed bar identity')
                if self._state.last_end is not None and start < self._state.last_end: raise ContractError(ErrorCode.INVALID_ORDER,'bar overlap across chunks')
                if end <= self._state.bound: raise ContractError(ErrorCode.BOUNDS,'late completed bar requires replay')
            else:
                first=(cast(int,columns['event_ns'][0]),cast(int,columns['order_key'][0]))
                if first == self._state.last_key: raise ContractError(ErrorCode.DUPLICATE,'repeated event order key')
                if self._state.last_key is not None and first < self._state.last_key: raise ContractError(ErrorCode.INVALID_ORDER,'event order overlap across chunks')
                if first[0] < self._state.bound: raise ContractError(ErrorCode.BOUNDS,'late event requires replay')
            retained={x.event_id for x in self._state.top.rows} if self._state.top is not None else {x.event_id for x in self._state.quotes.rows} if self._state.quotes is not None else set()
            if self._state.last_event_id is not None: retained.add(self._state.last_event_id)
            if self._seed is not None: retained.add(cast(str,_columns(self._seed)['event_id'][0]))
            if batch.kind != DataKind.BAR and any(x in retained for x in columns['event_id']):
                raise ContractError(ErrorCode.DUPLICATE,'known retained or seed event identity repeated')
        if self._family == 'structure':
            configured={x.name:x for x in self._config.session.intervals}
            for item in batch.metadata.interval_coverage:
                if item.name not in configured or (item.start_ns,item.end_ns) != (configured[item.name].start_ns,configured[item.name].end_ns):
                    raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,'chunk interval/config mismatch')
                actual=sum(item.start_ns <= cast(int,a) and cast(int,b) <= item.end_ns for a,b in zip(columns['start_ns'],columns['end_ns'],strict=True))
                if actual != item.coverage.observed:
                    raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,'chunk interval certificate must match chunk population')
        candidate=self._state.clone()
        candidate.observed=checked_int64(candidate.observed+batch.row_count)
        expected=self._population.metadata.coverage.expected
        if expected is not None and candidate.observed > expected:
            raise ContractError(ErrorCode.BOUNDS,'supplied population exceeds declared final expected count')
        if not batch.metadata.coverage.complete: candidate.known_gap=True
        known=columns.get('known_at_ns')
        for i in range(batch.row_count):
            text=self._config.availability.knowledge_reason(cast(int | None,known[i]) if known is not None else None)
            reason=Reason(text) if text is not None else None
            if reason is not None and reason not in candidate.knowledge: candidate.knowledge+=(reason,)
            if candidate.bars is not None:
                candidate.bars.add(columns,i,reason)
                start=cast(int,columns['start_ns'][i]);end=cast(int,columns['end_ns'][i])
                if self._family == 'structure':
                    for interval,window in zip(self._config.session.intervals,candidate.windows,strict=True):
                        if any(start < bound < end for bound in (interval.start_ns,interval.end_ns)):
                            raise ContractError(ErrorCode.BOUNDS,'requested interval straddles supplied whole bar')
                        if interval.start_ns <= start and end <= interval.end_ns: window.add(columns,i,reason)
                if candidate.first_start is None: candidate.first_start=start
                candidate.last_start=start;candidate.last_end=end;candidate.last_inclusive=True
            elif candidate.trades is not None: candidate.trades.add(columns,i,reason)
            elif candidate.top is not None: candidate.top.add(columns,i,reason,self._population.metadata.source.input_id)
            elif candidate.quotes is not None: candidate.quotes.add(columns,i,reason,self._population.metadata.source.input_id)
            elif candidate.temporal is not None and {'bid','ask'} <= set(self._population.fields):
                candidate.temporal.update(cast(int,columns['event_ns'][i]),cast(int | None,columns['bid'][i]),cast(int | None,columns['ask'][i]))
            if batch.kind != DataKind.BAR:
                candidate.last_key=(cast(int,columns['event_ns'][i]),cast(int,columns['order_key'][i]));candidate.last_event_id=cast(str,columns['event_id'][i])
                if candidate.first_key is None: candidate.first_key=candidate.last_key
                candidate.last_inclusive=batch.kind == DataKind.TRADE and 'condition' in columns and columns['condition'][i] == 'closing_auction'
        self._state=candidate

    def _metadata(self, config: ConfigSpec, metadata: BatchMetadata) -> ResultMetadata:
        role='bars' if self._family in ('bars','structure') else 'trades' if self._family in ('trades','top_k') else 'quotes'
        bindings=[InputBinding(role,self._population.kind,metadata)]
        if self._prior_close is not None: bindings.append(InputBinding('prior_close',DataKind.DAILY,self._prior_close.metadata))
        if self._seed is not None: bindings.append(InputBinding('quote_seed',DataKind.QUOTE,self._seed.metadata))
        params={p.name:p.value for p in config.parameters}
        limit=cast(int,params['evidence_limit']) if self._family == 'top_k' else cast(int,params['observation_limit']) if self._family == 'quotes' else 1 if self._family == 'continuous' else 0
        backend='python-exact-compensated' if self._family in ('quotes','continuous') else 'python-exact'
        return ResultMetadata(config.session.namespace,self._entity.session_id,config.availability,config.digest,tuple(bindings),backend,__version__,limit)

    def snapshot(self, certificate: PrefixCoverage) -> FeatureResult:
        if type(certificate) is not PrefixCoverage:
            raise ContractError(ErrorCode.INVALID_SCHEMA,'typed requested-prefix certificate required')
        if self._state.sealed is not None and certificate != self._state.sealed:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,'sealed snapshot certificate cannot change')
        cutoff=certificate.cutoff_ns
        if not self._config.session.open_ns < cutoff <= self._config.availability.market_cutoff_ns or cutoff < self._state.bound:
            raise ContractError(ErrorCode.BOUNDS,'cutoff outside legal forward snapshot range')
        if certificate.coverage.observed != self._state.observed:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,'prefix certificate must bind actual consumed population')
        expected=self._population.metadata.coverage.expected
        if cutoff == self._config.availability.market_cutoff_ns and expected is not None and certificate.coverage.expected != expected:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,'final expected population contradicts declaration')
        if self._state.known_gap and certificate.coverage.complete:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,'known missing past delivery requires replay')
        last=self._state.last_end if self._population.kind == DataKind.BAR else self._state.last_key[0] if self._state.last_key is not None else None
        if last is not None and (last > cutoff or last == cutoff and not self._state.last_inclusive):
            raise ContractError(ErrorCode.BOUNDS,'snapshot cannot precede consumed market facts')
        config=replace(self._config,availability=replace(self._config.availability,market_cutoff_ns=cutoff))
        scope=cast(InputScope,self._population.metadata.scope)
        supplied=replace(self._population.metadata,scope=replace(scope,end_ns=cutoff),coverage=certificate.coverage,interval_coverage=certificate.interval_coverage)
        candidate=self._state.clone()
        if candidate.temporal is not None: candidate.temporal.advance(cutoff)
        if certificate.coverage.expected is not None and certificate.coverage.expected > certificate.coverage.observed: candidate.known_gap=True
        metadata=self._metadata(config,supplied)
        if candidate.bars is not None:
            if self._family == 'structure': result=self._structure(candidate,config,certificate,metadata,supplied)
            else: result=candidate.bars.result(config,self._entity,certificate.coverage,metadata,_prior_info(self._prior_close,config))
        elif candidate.trades is not None: result=candidate.trades.result(config,self._entity,certificate.coverage,metadata)
        elif candidate.top is not None: result=candidate.top.result(config,self._entity,certificate.coverage,metadata)
        elif candidate.quotes is not None: result=candidate.quotes.result(config,self._entity,certificate.coverage,metadata,supplied.sampling)
        else: result=self._continuous(candidate,config,certificate,metadata)
        candidate.bound=cutoff;self._state=candidate
        return result

    def finalize(self, certificate: PrefixCoverage) -> FeatureResult:
        if self._state.sealed is not None: raise ContractError(ErrorCode.BOUNDS,'finalize is single-use')
        if type(certificate) is not PrefixCoverage or certificate.cutoff_ns != self._config.availability.market_cutoff_ns:
            raise ContractError(ErrorCode.BOUNDS,'finalize requires configured final cutoff')
        result=self.snapshot(certificate);self._state=replace(self._state,sealed=certificate)
        return result

    def _continuous(self, state: _StreamState, config: ConfigSpec, certificate: PrefixCoverage, metadata: ResultMetadata) -> FeatureResult:
        status=Status.AVAILABLE;reasons: tuple[Reason,...]=()
        if not certificate.coverage.complete: status,reasons=Status.INCOMPLETE_COVERAGE,(Reason.GOVERNED_GAP,)
        elif state.knowledge: status,reasons=Status.MISSING_INPUT,state.knowledge
        elif state.observed and not {'bid','ask'} <= set(self._population.fields): status,reasons=Status.MISSING_INPUT,(Reason.ABSENT_INPUT,)
        value=None;evidence: tuple[EvidenceRow,...]=()
        if status == Status.AVAILABLE:
            initial=cast(str,next(p.value for p in config.parameters if p.name == 'initial_state'))
            value=cast(_TimeReducer,state.temporal).summary(initial);evidence=self._seed_evidence
            if value.durations.unknown:
                status=Status.INCOMPLETE_COVERAGE;reasons=tuple(dict.fromkeys((Reason.UNKNOWN_AVAILABILITY,)+((self._seed_reason,) if self._seed_reason is not None else ())))
            elif not value.durations.valid: status,reasons=Status.NOT_APPLICABLE,(Reason.ZERO_DENOMINATOR,)
        feature_id='session.quote.time_weighted_spread'
        return FeatureResult((FeatureColumn(feature_id,'v1',ValueType.TIME_WEIGHTED_SPREAD,'currency/share; bps; ns; fraction',(self._entity,),(value,)),),(QualityRow(self._entity,feature_id,status,certificate.coverage.expected,state.observed,reasons),),metadata,evidence)

    def _structure(self, state: _StreamState, config: ConfigSpec, certificate: PrefixCoverage, metadata: ResultMetadata, supplied: BatchMetadata) -> FeatureResult:
        whole=cast(_BarTotals,state.bars).result(config,self._entity,certificate.coverage,metadata)
        total=next(c.values[0] for c in whole.values if c.feature_id == 'session.bar.volume')
        total_quality=next(q for q in whole.quality if q.feature_id == 'session.bar.volume')
        declared={x.name:x for x in certificate.interval_coverage};configured={x.name:x for x in config.session.intervals}
        for name,item in declared.items():
            if name not in configured or (item.start_ns,item.end_ns) != (configured[name].start_ns,configured[name].end_ns):
                raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,'prefix interval/config mismatch')
        ohlcv_id='session.structure.interval_ohlcv';share_id='session.structure.interval_volume_share'
        ohlcv_rows: list[IntervalOHLCVRow]=[];share_rows: list[IntervalVolumeShareRow]=[]
        for interval,window in zip(config.session.intervals,state.windows,strict=True):
            delivery=declared.get(interval.name);expected=delivery.coverage.expected if delivery is not None else None
            if delivery is not None and delivery.coverage.observed != window.observed:
                raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,'actual interval population/certificate mismatch')
            status=Status.INCOMPLETE_COVERAGE;reasons: tuple[Reason,...]=(Reason.GOVERNED_GAP,)
            volume: int | None=None;prices: tuple[float | None,...]=(None,None,None,None)
            volume_status=status;volume_reasons=reasons
            if delivery is not None and delivery.coverage.complete and interval.end_ns <= certificate.cutoff_ns:
                session=replace(config.session,open_ns=interval.start_ns,close_ns=interval.end_ns,intervals=(),scheduled_close_ns=None,early_close=False)
                scoped_config=replace(config,session=session,availability=replace(config.availability,market_cutoff_ns=interval.end_ns))
                scoped_meta=replace(supplied,scope=replace(cast(InputScope,supplied.scope),start_ns=interval.start_ns,end_ns=interval.end_ns),coverage=delivery.coverage,interval_coverage=())
                reduced=window.result(scoped_config,self._entity,delivery.coverage,self._metadata(scoped_config,scoped_meta))
                cells={c.feature_id.rsplit('.',1)[1]:c.values[0] for c in reduced.values};qualities={q.feature_id.rsplit('.',1)[1]:q for q in reduced.quality}
                volume=cast(int | None,cells['volume']);status=volume_status=qualities['volume'].status;reasons=volume_reasons=qualities['volume'].reasons
                if status == Status.AVAILABLE and volume:
                    bad=next((qualities[x] for x in ('open','high','low','close') if qualities[x].status != Status.AVAILABLE),None)
                    if bad is not None: status,reasons=bad.status,bad.reasons;volume=None
                    else: prices=tuple(cast(float,cells[x]) for x in ('open','high','low','close'))
            q=QualityRow(self._entity,ohlcv_id,status,expected,window.observed,reasons)
            ohlcv_rows.append(IntervalOHLCVRow(interval,prices[0],prices[1],prices[2],prices[3],volume,q))
            share_status=volume_status;share_reasons=volume_reasons;share: float | None=None
            if share_status == Status.AVAILABLE:
                if total_quality.status != Status.AVAILABLE: share_status,share_reasons=total_quality.status,total_quality.reasons
                elif total == 0: share_status,share_reasons=Status.NOT_APPLICABLE,(Reason.ZERO_DENOMINATOR,)
                else:
                    from fractions import Fraction
                    share=float(Fraction(cast(int,volume if volume is not None else cells['volume']),cast(int,total)))
            share_rows.append(IntervalVolumeShareRow(interval,share,QualityRow(self._entity,share_id,share_status,expected,window.observed,share_reasons)))
        values=(FeatureColumn(ohlcv_id,'v1',ValueType.INTERVAL_OHLCV,'currency/share; shares',(self._entity,),(IntervalOHLCV(tuple(ohlcv_rows)),)),FeatureColumn(share_id,'v1',ValueType.INTERVAL_VOLUME_SHARES,'fraction',(self._entity,),(IntervalVolumeShares(tuple(share_rows)),)))
        quality=tuple(QualityRow(self._entity,feature_id,Status.AVAILABLE if ready == len(rows) else Status.INCOMPLETE_COVERAGE,len(rows),ready,tuple(dict.fromkeys(reason for row in rows for reason in row.quality.reasons))) for feature_id,rows in ((ohlcv_id,ohlcv_rows),(share_id,share_rows)) for ready in (sum(row.quality.status == Status.AVAILABLE for row in rows),))
        return FeatureResult(values,quality,metadata)
