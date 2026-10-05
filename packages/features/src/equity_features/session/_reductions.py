"""Shared fixed-retention reductions and result formatting for batch and chunk lifecycles."""
from __future__ import annotations
from dataclasses import dataclass, field, replace
from fractions import Fraction
from typing import cast
from equity_feature_contracts import (
    Cell, ConfigSpec, ContractError, Coverage, EntityKey, ErrorCode, EvidenceRow,
    FeatureColumn, FeatureResult, PriceUnit, QualityRow, QuoteObservation,
    QuoteStateCounts, Reason, ResultCell, ResultMetadata, SampledSpread, Status,
    TopKTradeRow, TopKTrades, ValueType, builtin_registry, checked_decimal128,
    checked_int64, quote_state,
)
from equity_feature_contracts._implemented import BAR_IDS, TRADE_IDS

Columns = dict[str,tuple[Cell,...]]
Readiness = tuple[Status,tuple[Reason,...]]
PriorInfo = tuple[Status,tuple[Reason,...],int | None]


def _quote_values(bid: int | None, ask: int | None, scale: int) -> tuple[str,float | None,float | None]:
    state=quote_state(bid,ask)
    if state == 'invalid': return state,None,None
    b=cast(int,bid);a=cast(int,ask)
    return state,float(Fraction(a-b,10**scale)),float(Fraction(20000*(a-b),a+b))

@dataclass
class _Sum:
    width: str = 'int64'
    value: int = 0
    overflow: bool = False

    def add(self, value: int) -> None:
        if self.overflow: return
        try:
            self.value=checked_int64(self.value+value) if self.width == 'int64' else checked_decimal128(self.value+value)
        except ContractError as error:
            if error.code != ErrorCode.OVERFLOW: raise
            self.value=0;self.overflow=True

    def get(self) -> int:
        if self.overflow: raise ContractError(ErrorCode.OVERFLOW,'ready aggregate exceeds checked representation')
        return self.value

@dataclass
class _Basis:
    fields: tuple[str,...]
    observed: int = 0
    knowledge: tuple[Reason,...] = ()

    def _record(self, reason: Reason | None) -> None:
        self.observed=checked_int64(self.observed+1)
        if reason is not None and reason not in self.knowledge: self.knowledge+= (reason,)

    def base(self, coverage: Coverage, override: Readiness | None = None) -> Readiness:
        if override is not None: return override
        if not coverage.complete: return Status.INCOMPLETE_COVERAGE,(Reason.GOVERNED_GAP,)
        if self.knowledge: return Status.MISSING_INPUT,self.knowledge
        return Status.AVAILABLE,()

@dataclass
class _BarTotals(_Basis):
    positive: int = 0
    volume: _Sum = field(default_factory=_Sum)
    notional: _Sum = field(default_factory=lambda:_Sum('decimal128'))
    proxy: _Sum = field(default_factory=lambda:_Sum('decimal128'))
    prices: dict[str,int | None] = field(default_factory=lambda:{x:None for x in ('open','high','low','close')})
    nulls: set[str] = field(default_factory=set)

    def clone(self) -> _BarTotals:
        return replace(self,volume=replace(self.volume),notional=replace(self.notional),proxy=replace(self.proxy),prices=dict(self.prices),nulls=set(self.nulls))

    def add(self, columns: Columns, i: int, reason: Reason | None) -> None:
        self._record(reason)
        quantity=cast(int | None,columns['volume'][i]) if 'volume' in columns else None
        if quantity is None: self.nulls.add('volume');return
        self.volume.add(quantity)
        if quantity == 0: return
        self.positive+=1
        for name in ('open','high','low','close'):
            value=cast(int | None,columns[name][i]) if name in columns else None
            if value is None: self.nulls.add(name);continue
            old=self.prices[name]
            self.prices[name]=value if old is None or name == 'close' else max(old,value) if name == 'high' else min(old,value) if name == 'low' else old
        amount=cast(int | None,columns['actual_notional'][i]) if 'actual_notional' in columns else None
        if amount is None: self.nulls.add('actual_notional')
        else: self.notional.add(amount)
        close=cast(int | None,columns['close'][i]) if 'close' in columns else None
        if close is not None: self.proxy.add(close*quantity)

    def field_ready(self, names: tuple[str,...]) -> Readiness:
        if self.observed == 0: return Status.AVAILABLE,()
        for name in names:
            if name not in self.fields: return Status.MISSING_INPUT,(Reason.ABSENT_INPUT,)
            if name in self.nulls: return Status.MISSING_INPUT,(Reason.NULL_FIELD,)
        return Status.AVAILABLE,()

    def result(self, config: ConfigSpec, entity: EntityKey, coverage: Coverage, metadata: ResultMetadata,
               prior: PriorInfo = (Status.MISSING_INPUT,(Reason.ABSENT_INPUT,),None), override: Readiness | None = None) -> FeatureResult:
        base=self.base(coverage,override);scale=10**cast(PriceUnit,config.price_unit).scale
        values: list[FeatureColumn]=[];quality: list[QualityRow]=[];registry=builtin_registry()
        requirements={'open':('open',),'high':('high',),'low':('low',),'close':('close',),'notional':('actual_notional',),'close_weighted_price':('close',),'open_close_return':('open','close'),'range_fraction':('high','low','close'),'close_location':('high','low','close'),'overnight_gap':('open',),'close_close_return':('close',)}
        for feature_id in BAR_IDS:
            name=feature_id.rsplit('.',1)[1];status,reasons=base
            value: ResultCell=None
            if status == Status.AVAILABLE:
                status,reasons=self.field_ready(('volume',))
            if status == Status.AVAILABLE:
                volume=self.volume.get()
                if name == 'volume': value=volume
                elif name == 'notional' and self.positive == 0: value=0
                elif self.positive == 0: status,reasons=Status.NOT_APPLICABLE,(Reason.NO_ELIGIBLE_OBSERVATIONS,)
                else:
                    status,reasons=self.field_ready(requirements[name])
                    if status == Status.AVAILABLE:
                        if name == 'notional': value=self.notional.get()
                        elif name in ('open','high','low','close'): value=float(Fraction(cast(int,self.prices[name]),scale))
                        elif name == 'close_weighted_price': value=float(Fraction(self.proxy.get(),volume*scale))
                        elif name == 'open_close_return': value=float(Fraction(cast(int,self.prices['close'])-cast(int,self.prices['open']),cast(int,self.prices['open'])))
                        elif name == 'range_fraction': value=float(Fraction(cast(int,self.prices['high'])-cast(int,self.prices['low']),cast(int,self.prices['close'])))
                        elif name == 'close_location':
                            width=cast(int,self.prices['high'])-cast(int,self.prices['low'])
                            if not width: status,reasons=Status.NOT_APPLICABLE,(Reason.ZERO_DENOMINATOR,)
                            else: value=float(Fraction(cast(int,self.prices['close'])-cast(int,self.prices['low']),width))
                        else:
                            status,reasons,previous=prior
                            if status == Status.AVAILABLE:
                                value=float(Fraction(cast(int,self.prices['open' if name == 'overnight_gap' else 'close'])-cast(int,previous),cast(int,previous)))
            output=registry.get(feature_id).outputs[0]
            values.append(FeatureColumn(feature_id,'v1',ValueType(output.dtype),output.unit,(entity,),(value,)))
            quality.append(QualityRow(entity,feature_id,status,coverage.expected,self.observed,reasons))
        return FeatureResult(tuple(values),tuple(quality),metadata)

@dataclass
class _TradeTotals(_Basis):
    eligible: int = 0
    volume: _Sum = field(default_factory=_Sum)
    notional: _Sum = field(default_factory=lambda:_Sum('decimal128'))

    def clone(self) -> _TradeTotals:
        return replace(self,volume=replace(self.volume),notional=replace(self.notional))

    def add(self, columns: Columns, i: int, reason: Reason | None) -> None:
        self._record(reason)
        if columns['eligible'][i] is not True: return
        self.eligible+=1
        if 'size' in columns:
            self.volume.add(cast(int,columns['size'][i]))
            if 'price' in columns: self.notional.add(cast(int,columns['size'][i])*cast(int,columns['price'][i]))

    def field_ready(self, fields: tuple[str,...]) -> Readiness:
        if self.eligible and any(x not in self.fields for x in fields): return Status.MISSING_INPUT,(Reason.ABSENT_INPUT,)
        return Status.AVAILABLE,()

    def result(self, config: ConfigSpec, entity: EntityKey, coverage: Coverage, metadata: ResultMetadata, override: Readiness | None = None) -> FeatureResult:
        base=self.base(coverage,override);scale=10**cast(PriceUnit,config.price_unit).scale
        values: list[FeatureColumn]=[];quality: list[QualityRow]=[];registry=builtin_registry()
        required={'count':(),'volume':('size',),'notional':('price','size'),'vwap':('price','size'),'mean_size':('size',)}
        # Match batch admission's eager checked dependency reductions on ready input.
        if base[0] == Status.AVAILABLE:
            if self.field_ready(('size',))[0] == Status.AVAILABLE: self.volume.get()
            if self.field_ready(('price','size'))[0] == Status.AVAILABLE: self.notional.get()
        for feature_id in TRADE_IDS:
            name=feature_id.rsplit('.',1)[1];status,reasons=base
            value: ResultCell=None
            if status == Status.AVAILABLE: status,reasons=self.field_ready(required[name])
            if status == Status.AVAILABLE:
                if name == 'count': value=self.eligible
                elif name == 'volume': value=self.volume.get()
                elif name == 'notional': value=self.notional.get()
                elif not self.eligible: status,reasons=Status.NOT_APPLICABLE,(Reason.NO_ELIGIBLE_OBSERVATIONS,)
                elif name == 'vwap': value=float(Fraction(self.notional.get(),self.volume.get()*scale))
                else: value=float(Fraction(self.volume.get(),self.eligible))
            output=registry.get(feature_id).outputs[0]
            values.append(FeatureColumn(feature_id,'v1',ValueType(output.dtype),output.unit,(entity,),(value,)))
            quality.append(QualityRow(entity,feature_id,status,coverage.expected,self.observed,reasons))
        return FeatureResult(tuple(values),tuple(quality),metadata)

@dataclass
class _QuoteTotals(_Basis):
    limit: int = 0
    scale: int = 0
    counts: dict[str,int] = field(default_factory=lambda:{x:0 for x in ('normal','locked','crossed','invalid')})
    spread: _Sum = field(default_factory=lambda:_Sum('decimal128'))
    bps_sum: float = 0.0
    compensation: float = 0.0
    rows: list[QuoteObservation] = field(default_factory=list)

    def clone(self) -> _QuoteTotals:
        return replace(self,counts=dict(self.counts),spread=replace(self.spread),rows=list(self.rows))

    def add(self, columns: Columns, i: int, reason: Reason | None, input_id: str) -> None:
        self._record(reason)
        if not {'bid','ask'} <= set(self.fields): return
        bid=cast(int | None,columns['bid'][i]);ask=cast(int | None,columns['ask'][i])
        state,spread,bps=_quote_values(bid,ask,self.scale);self.counts[state]+=1
        if state in ('normal','locked'):
            self.spread.add(cast(int,ask)-cast(int,bid))
            adjusted=cast(float,bps)-self.compensation
            updated=self.bps_sum+adjusted;self.compensation=(updated-self.bps_sum)-adjusted;self.bps_sum=updated
        if len(self.rows) < self.limit:
            self.rows.append(QuoteObservation(input_id,cast(str,columns['event_id'][i]),cast(int,columns['event_ns'][i]),cast(int,columns['order_key'][i]),cast(int | None,columns['known_at_ns'][i]) if 'known_at_ns' in columns else None,bid,ask,state,spread,bps))

    def result(self, config: ConfigSpec, entity: EntityKey, coverage: Coverage, metadata: ResultMetadata, sampling: str, override: Readiness | None = None) -> FeatureResult:
        status,reasons=self.base(coverage,override)
        if status == Status.AVAILABLE and self.observed and not {'bid','ask'} <= set(self.fields):
            status,reasons=Status.MISSING_INPUT,(Reason.ABSENT_INPUT,)
        count_value=QuoteStateCounts(*(self.counts[x] for x in ('normal','locked','crossed','invalid')))
        sampled_status=status;sampled_reasons=reasons;sampled: ResultCell=None;evidence: tuple[EvidenceRow,...]=()
        if status == Status.AVAILABLE:
            valid=count_value.valid
            if not valid: sampled_status,sampled_reasons=Status.NOT_APPLICABLE,(Reason.NO_ELIGIBLE_OBSERVATIONS,)
            sampled=SampledSpread(sampling,count_value.total,valid,float(Fraction(self.spread.get(),valid*10**self.scale)) if valid else None,self.bps_sum/valid if valid else None,self.limit,tuple(self.rows))
            evidence=tuple(EvidenceRow(entity,'session.quote.sampled_spread',x.input_id,x.event_id,x.event_ns,x.known_at_ns) for x in self.rows)
        registry=builtin_registry();sample_id='session.quote.sampled_spread';count_id='session.quote.state_counts'
        values=(FeatureColumn(sample_id,'v1',ValueType.SAMPLED_SPREAD,registry.get(sample_id).outputs[0].unit,(entity,),(sampled,)),FeatureColumn(count_id,'v1',ValueType.QUOTE_STATE_COUNTS,registry.get(count_id).outputs[0].unit,(entity,),(count_value if status == Status.AVAILABLE else None,)))
        quality=(QualityRow(entity,sample_id,sampled_status,coverage.expected,self.observed,sampled_reasons),QualityRow(entity,count_id,status,coverage.expected,self.observed,reasons))
        return FeatureResult(values,quality,metadata,evidence)

@dataclass
class _TopTotals(_Basis):
    k: int = 1
    eligible: int = 0
    rows: list[TopKTradeRow] = field(default_factory=list)

    def clone(self) -> _TopTotals: return replace(self,rows=list(self.rows))

    def add(self, columns: Columns, i: int, reason: Reason | None, input_id: str) -> None:
        self._record(reason)
        if columns['eligible'][i] is not True: return
        self.eligible+=1
        if not {'price','size'} <= set(self.fields): return
        row=TopKTradeRow(input_id,cast(str,columns['event_id'][i]),cast(int,columns['event_ns'][i]),cast(int,columns['order_key'][i]),cast(int | None,columns['known_at_ns'][i]) if 'known_at_ns' in columns else None,cast(int,columns['price'][i]),cast(int,columns['size'][i]))
        self.rows.append(row);self.rows.sort(key=lambda x:x.rank_key)
        if len(self.rows) > self.k: self.rows.pop()

    def result(self, config: ConfigSpec, entity: EntityKey, coverage: Coverage, metadata: ResultMetadata, override: Readiness | None = None) -> FeatureResult:
        status,reasons=self.base(coverage,override)
        if status == Status.AVAILABLE and self.eligible and not {'price','size'} <= set(self.fields):
            status,reasons=Status.MISSING_INPUT,(Reason.ABSENT_INPUT,)
        feature_id='session.trade.top_k';value=TopKTrades(self.k,tuple(self.rows)) if status == Status.AVAILABLE else None
        evidence=tuple(EvidenceRow(entity,feature_id,x.input_id,x.event_id,x.event_ns,x.known_at_ns,boundary='closing_auction' if x.event_ns == config.availability.market_cutoff_ns else 'ordinary') for x in self.rows) if status == Status.AVAILABLE else ()
        output=builtin_registry().get(feature_id).outputs[0]
        return FeatureResult((FeatureColumn(feature_id,'v1',ValueType.TOP_K_TRADES,output.unit,(entity,),(value,)),),(QualityRow(entity,feature_id,status,coverage.expected,self.observed,reasons),),metadata,evidence)
