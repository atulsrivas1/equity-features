"""Pure bounded legal merge of caller-certified disjoint adjacent partitions."""
from __future__ import annotations
from dataclasses import replace
from typing import cast
from equity_feature_contracts import ContractError, DataKind, ErrorCode, PartitionSpan, checked_int64
from .incremental import SessionAccumulator
from .state import _binding
from .session._reductions import _BarTotals, _TradeTotals, _TopTotals, _QuoteTotals, _Sum


def _sum(a: _Sum, b: _Sum) -> _Sum:
    result=replace(a)
    if b.overflow: result.value=0;result.overflow=True
    else: result.add(b.value)
    return result

def _bar(a: _BarTotals, b: _BarTotals) -> _BarTotals:
    result=a.clone();result.observed=checked_int64(a.observed+b.observed);result.positive=checked_int64(a.positive+b.positive)
    result.knowledge=tuple(dict.fromkeys(a.knowledge+b.knowledge));result.nulls=a.nulls|b.nulls
    result.volume=_sum(a.volume,b.volume);result.notional=_sum(a.notional,b.notional);result.proxy=_sum(a.proxy,b.proxy)
    result.prices['open']=a.prices['open'] if a.prices['open'] is not None else b.prices['open']
    result.prices['close']=b.prices['close'] if b.prices['close'] is not None else a.prices['close']
    for key,combine in (('high',max),('low',min)):
        values=[x for x in (a.prices[key],b.prices[key]) if x is not None]
        result.prices[key]=combine(values) if values else None
    return result

def _compensated(a: _QuoteTotals, value: float) -> None:
    adjusted=value-a.compensation;updated=a.bps_sum+adjusted
    a.compensation=(updated-a.bps_sum)-adjusted;a.bps_sum=updated

def merge_partitions(a: SessionAccumulator, b: SessionAccumulator, *, left: PartitionSpan, right: PartitionSpan) -> SessionAccumulator:
    if type(a) is not SessionAccumulator or type(b) is not SessionAccumulator or type(left) is not PartitionSpan or type(right) is not PartitionSpan:
        raise ContractError(ErrorCode.INVALID_SCHEMA,'typed accumulators and certified partition spans required')
    if a.family=='continuous' or b.family=='continuous':
        raise ContractError(ErrorCode.UNSUPPORTED_CAPABILITY,'continuous quote carry requires replay; no legal merge')
    if _binding(a)!=_binding(b):
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,'partition config/entity/source/schema/enrichment/math mismatch')
    if left.count!=a._state.observed or right.count!=b._state.observed:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,'certified partition count differs from actual consumption')
    if right.start_ordinal<left.start_ordinal: a,b,left,right=b,a,right,left
    if left.end_ordinal!=right.start_ordinal:
        raise ContractError(ErrorCode.BOUNDS,'only disjoint adjacent population partitions merge')
    expected=a.population.metadata.coverage.expected
    if expected is not None and right.end_ordinal>expected:
        raise ContractError(ErrorCode.BOUNDS,'partition span exceeds declared final population')
    x=a._state;y=b._state
    if any(s.sealed is not None or s.bound!=a.config.session.open_ns for s in (x,y)):
        raise ContractError(ErrorCode.BOUNDS,'merge before publication/finalization only; replay otherwise')
    if a.population.kind==DataKind.BAR:
        if cast(int,x.last_end)>cast(int,y.first_start):
            raise ContractError(ErrorCode.INVALID_ORDER,'completed bar partitions overlap or contradict global ordinal order')
    elif cast(tuple[int,int],x.last_key)>=cast(tuple[int,int],y.first_key):
        raise ContractError(ErrorCode.INVALID_ORDER,'event partition order overlaps or contradicts global ordinals')
    ids_a={r.event_id for r in x.top.rows} if x.top is not None else {r.event_id for r in x.quotes.rows} if x.quotes is not None else set()
    ids_b={r.event_id for r in y.top.rows} if y.top is not None else {r.event_id for r in y.quotes.rows} if y.quotes is not None else set()
    if x.last_event_id is not None:ids_a.add(x.last_event_id)
    if y.last_event_id is not None:ids_b.add(y.last_event_id)
    if ids_a&ids_b: raise ContractError(ErrorCode.DUPLICATE,'known retained or last event identities overlap')
    result=SessionAccumulator(a.family,a.config,entity=a.entity,population=a.population,prior_close=a._prior_close,seed=a._seed)
    z=x.clone();z.observed=checked_int64(x.observed+y.observed);z.known_gap=x.known_gap or y.known_gap;z.knowledge=tuple(dict.fromkeys(x.knowledge+y.knowledge))
    z.last_key=y.last_key;z.last_start=y.last_start;z.last_end=y.last_end;z.last_event_id=y.last_event_id;z.last_inclusive=y.last_inclusive
    if x.bars is not None:
        z.bars=_bar(x.bars,cast(_BarTotals,y.bars));z.windows=tuple(_bar(l,r) for l,r in zip(x.windows,y.windows,strict=True))
    elif x.trades is not None:
        l=x.trades;r=cast(_TradeTotals,y.trades)
        z.trades=replace(l,observed=z.observed,eligible=checked_int64(l.eligible+r.eligible),knowledge=z.knowledge,volume=_sum(l.volume,r.volume),notional=_sum(l.notional,r.notional))
    elif x.top is not None:
        l_top=x.top;r_top=cast(_TopTotals,y.top)
        z.top=replace(l_top,observed=z.observed,eligible=checked_int64(l_top.eligible+r_top.eligible),knowledge=z.knowledge,rows=sorted(l_top.rows+r_top.rows,key=lambda row:row.rank_key)[:l_top.k])
    elif x.quotes is not None:
        l_quote=x.quotes;r_quote=cast(_QuoteTotals,y.quotes);q=l_quote.clone()
        q.observed=z.observed;q.knowledge=z.knowledge;q.counts={k:checked_int64(l_quote.counts[k]+r_quote.counts[k]) for k in l_quote.counts};q.spread=_sum(l_quote.spread,r_quote.spread)
        _compensated(q,r_quote.bps_sum);_compensated(q,-r_quote.compensation)
        q.rows=(l_quote.rows+r_quote.rows)[:q.limit];z.quotes=q
    result._state=z
    return result
