"""Fixed-schema, exact, non-executable in-memory accumulator state codec."""
from __future__ import annotations
from dataclasses import asdict
import hashlib
import json
import math
from typing import Any, cast
from equity_feature_contracts import (
    AccumulatorState, CanonicalBatch, ConfigSpec, ContractError, Coverage, DataKind,
    EntityKey, ErrorCode, IntervalCoverage, PrefixCoverage,
    QuoteObservation, Reason, StreamPopulation, TopKTradeRow, TopKTrades,
    checked_decimal128,
)
from equity_feature_contracts.inputs import I64_MAX, I64_MIN
from . import __version__
from .incremental import Family, SessionAccumulator, _StreamState
from .session._reductions import _BarTotals, _TradeTotals, _TopTotals, _QuoteTotals, _Sum, _quote_values
from .session.continuous import _TimeReducer, _CATEGORIES


def _fail() -> None:
    raise ContractError(ErrorCode.INVALID_SCHEMA,'invalid bounded accumulator state')

def _wire(value: Any) -> Any:
    if type(value) is float:
        if not math.isfinite(value): _fail()
        return {'binary64':value.hex()}
    if isinstance(value,dict): return {k:_wire(v) for k,v in value.items()}
    if isinstance(value,(list,tuple,set)): return [_wire(x) for x in (sorted(value) if isinstance(value,set) else value)]
    return value

def _text(value: Any) -> str:
    return json.dumps(_wire(value),sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)

def _digest(text: str) -> str: return hashlib.sha256(text.encode('utf-8')).hexdigest()

def _binding(a: SessionAccumulator) -> str:
    return _digest(_text(dict(family=a.family,config=asdict(a.config),entity=asdict(a.entity),population=asdict(a.population),prior=asdict(a._prior_close) if a._prior_close is not None else None,seed=asdict(a._seed) if a._seed is not None else None,math='r1-exact-compensated-v1',backend='python')))

def export_state(a: SessionAccumulator) -> AccumulatorState:
    payload=_text(asdict(a._state))
    return AccumulatorState('2',__version__,_binding(a),payload,_digest(payload))

def _pairs(pairs: list[tuple[str,Any]]) -> dict[str,Any]:
    if len({k for k,v in pairs}) != len(pairs): _fail()
    return dict(pairs)

def _decode(value: Any, depth: int=0) -> Any:
    if depth > 12: _fail()
    if type(value) is dict:
        if set(value)=={'binary64'}:
            if type(value['binary64']) is not str: _fail()
            result=float.fromhex(value['binary64'])
            if not math.isfinite(result) or result.hex() != value['binary64']: _fail()
            return result
        return {k:_decode(v,depth+1) for k,v in value.items()}
    if type(value) is list: return [_decode(v,depth+1) for v in value]
    if type(value) in (float,): _fail()
    return value

def _obj(value: Any, keys: set[str]) -> dict[str,Any]:
    if type(value) is not dict or set(value) != keys: _fail()
    return cast(dict[str,Any],value)

def _integer(value: Any, low: int=0, high: int=I64_MAX) -> int:
    if type(value) is not int or not low <= value <= high: _fail()
    return cast(int,value)

def _boolean(value: Any) -> bool:
    if type(value) is not bool: _fail()
    return cast(bool,value)

def _optional(value: Any) -> int | None:
    return None if value is None else _integer(value,I64_MIN)

def _reasons(value: Any) -> tuple[Reason,...]:
    if type(value) is not list or len(value)>2: _fail()
    result=tuple(Reason(x) for x in value)
    if len(set(result)) != len(result) or any(x not in (Reason.UNKNOWN_AVAILABILITY,Reason.FUTURE_KNOWLEDGE) for x in result): _fail()
    return result

def _sum(value: Any, width: str) -> _Sum:
    d=_obj(value,{'width','value','overflow'})
    if d['width'] != width: _fail()
    amount=_integer(d['value'],0,I64_MAX if width=='int64' else 10**38-1);overflow=_boolean(d['overflow'])
    if overflow and amount != 0: _fail()
    return _Sum(width,amount,overflow)

def _basis(d: dict[str,Any], fields: tuple[str,...], maximum: int) -> dict[str,Any]:
    if type(d['fields']) is not list or tuple(d['fields']) != fields: _fail()
    return dict(fields=fields,observed=_integer(d['observed'],0,maximum),knowledge=_reasons(d['knowledge']))

def _bar(value: Any, fields: tuple[str,...], maximum: int) -> _BarTotals:
    d=_obj(value,set(asdict(_BarTotals(fields))))
    basis=_basis(d,fields,maximum);positive=_integer(d['positive'],0,basis['observed'])
    prices=_obj(d['prices'],{'open','high','low','close'})
    prices={k:None if v is None else _integer(v,1) for k,v in prices.items()}
    nulls=d['nulls']
    if type(nulls) is not list or len(set(nulls)) != len(nulls) or not set(nulls)<= {'volume','actual_notional','open','high','low','close'}: _fail()
    result=_BarTotals(**basis,positive=positive,volume=_sum(d['volume'],'int64'),notional=_sum(d['notional'],'decimal128'),proxy=_sum(d['proxy'],'decimal128'),prices=prices,nulls=set(nulls))
    if not positive and any(x is not None for x in prices.values()): _fail()
    if positive and 'volume' not in nulls and not result.volume.overflow and result.volume.value < positive: _fail()
    if not positive and (result.notional.value or result.notional.overflow or result.proxy.value or result.proxy.overflow): _fail()
    if not result.observed and (result.volume.value or result.volume.overflow or result.nulls): _fail()
    if prices['low'] is not None and prices['high'] is not None and prices['low']>prices['high']: _fail()
    return result

def _float(value: Any) -> float:
    if type(value) is not float or not math.isfinite(value): _fail()
    return cast(float,value)

def _ordered(value: Any) -> tuple[int,int] | None:
    if value is None: return None
    if type(value) is not list or len(value) != 2: _fail()
    return (_integer(value[0],I64_MIN),_integer(value[1],I64_MIN))

def _certificate(value: Any) -> PrefixCoverage | None:
    if value is None: return None
    d=_obj(value,{'cutoff_ns','coverage','interval_coverage'})
    coverage=Coverage(**_obj(d['coverage'],{'expected','observed','complete'}))
    if type(d['interval_coverage']) is not list: _fail()
    rows=[]
    for x in d['interval_coverage']:
        x=_obj(x,{'name','start_ns','end_ns','coverage'})
        rows.append(IntervalCoverage(x['name'],x['start_ns'],x['end_ns'],Coverage(**_obj(x['coverage'],{'expected','observed','complete'}))))
    return PrefixCoverage(d['cutoff_ns'],coverage,tuple(rows))

def _read(a: SessionAccumulator, raw: Any) -> _StreamState:
    d=_obj(raw,set(asdict(a._state)));n=_integer(d['observed']);expected=a.population.metadata.coverage.expected
    if expected is not None and n>expected: _fail()
    bound=_integer(d['bound'],a.config.session.open_ns,a.config.availability.market_cutoff_ns)
    s=_StreamState(bound,n,first_key=_ordered(d['first_key']),last_key=_ordered(d['last_key']),first_start=_optional(d['first_start']),last_start=_optional(d['last_start']),last_end=_optional(d['last_end']),last_event_id=d['last_event_id'],last_inclusive=_boolean(d['last_inclusive']),known_gap=_boolean(d['known_gap']),knowledge=_reasons(d['knowledge']),sealed=_certificate(d['sealed']))
    if a.population.kind==DataKind.BAR:
        if s.first_key is not None or s.last_key is not None or s.last_event_id is not None or s.last_inclusive != bool(n): _fail()
        if n and (s.first_start is None or s.last_start is None or s.last_end is None or not a.config.session.open_ns <= s.first_start <= s.last_start < s.last_end <= a.config.availability.market_cutoff_ns): _fail()
        if not n and any(x is not None for x in (s.first_start,s.last_start,s.last_end)): _fail()
    else:
        if any(x is not None for x in (s.first_start,s.last_start,s.last_end)): _fail()
        if n and (s.first_key is None or s.last_key is None or s.first_key>s.last_key or type(s.last_event_id) is not str or not s.last_event_id.strip()): _fail()
        if not n and any(x is not None for x in (s.first_key,s.last_key,s.last_event_id)): _fail()
        if n and not a.config.session.open_ns <= cast(tuple[int,int],s.first_key)[0] <= cast(tuple[int,int],s.last_key)[0] <= a.config.availability.market_cutoff_ns: _fail()
        if s.last_inclusive and a.population.kind != DataKind.TRADE: _fail()
    for key in ('bars','trades','top','quotes','temporal'):
        expected_slot=asdict(a._state)[key]
        if (expected_slot is None) != (d[key] is None): _fail()
    if type(d['windows']) is not list or len(d['windows']) != len(a._state.windows): _fail()
    if type(d['window_gaps']) is not list or len(d['window_gaps']) != len(a._state.windows): _fail()
    s.window_gaps=tuple(_boolean(x) for x in d['window_gaps'])
    if any(s.window_gaps) and not s.known_gap: _fail()
    fields=a.population.fields
    if d['bars'] is not None: s.bars=_bar(d['bars'],fields,n)
    s.windows=tuple(_bar(x,fields,n) for x in d['windows'])
    if d['trades'] is not None:
        t=_obj(d['trades'],set(asdict(_TradeTotals(fields))));basis=_basis(t,fields,n)
        s.trades=_TradeTotals(**basis,eligible=_integer(t['eligible'],0,n),volume=_sum(t['volume'],'int64'),notional=_sum(t['notional'],'decimal128'))
        if 'size' in fields and not s.trades.volume.overflow and s.trades.volume.value < s.trades.eligible: _fail()
        if not s.trades.notional.overflow and not s.trades.volume.overflow and {'price','size'}<=set(fields) and s.trades.notional.value < s.trades.volume.value: _fail()
        if not s.trades.eligible and (s.trades.volume.value or s.trades.notional.value or s.trades.volume.overflow or s.trades.notional.overflow): _fail()
    if d['top'] is not None:
        t=_obj(d['top'],set(asdict(cast(_TopTotals,a._state.top))));basis=_basis(t,fields,n)
        if t['k'] != cast(_TopTotals,a._state.top).k or type(t['rows']) is not list or len(t['rows'])>cast(_TopTotals,a._state.top).k: _fail()
        rows=[TopKTradeRow(**_obj(x,{'input_id','event_id','event_ns','order_key','known_at_ns','price','size'})) for x in t['rows']]
        TopKTrades(t['k'],tuple(rows));eligible=_integer(t['eligible'],0,n)
        if len(rows) != (min(t['k'],eligible) if {'price','size'}<=set(fields) else 0): _fail()
        s.top=_TopTotals(**basis,k=t['k'],eligible=eligible,rows=rows)
    if d['quotes'] is not None:
        q=_obj(d['quotes'],set(asdict(cast(_QuoteTotals,a._state.quotes))));basis=_basis(q,fields,n);template=cast(_QuoteTotals,a._state.quotes)
        if q['limit'] != template.limit or q['scale'] != template.scale or type(q['rows']) is not list or len(q['rows'])>template.limit: _fail()
        counts={k:_integer(v) for k,v in _obj(q['counts'],{'normal','locked','crossed','invalid'}).items()}
        if sum(counts.values()) != (n if {'bid','ask'}<=set(fields) else 0): _fail()
        rows_q=[QuoteObservation(**_obj(x,{'input_id','event_id','event_ns','order_key','known_at_ns','bid','ask','state','spread','bps'})) for x in q['rows']]
        if len(rows_q)!=min(template.limit,sum(counts.values())): _fail()
        if len({(x.event_ns,x.order_key) for x in rows_q})!=len(rows_q) or len({x.event_id for x in rows_q})!=len(rows_q) or [(x.event_ns,x.order_key) for x in rows_q]!=sorted((x.event_ns,x.order_key) for x in rows_q): _fail()
        for row in rows_q:
            if _quote_values(row.bid,row.ask,template.scale)!=(row.state,row.spread,row.bps): _fail()
        s.quotes=_QuoteTotals(**basis,limit=template.limit,scale=template.scale,counts=counts,spread=_sum(q['spread'],'decimal128'),bps_sum=_float(q['bps_sum']),compensation=_float(q['compensation']),rows=rows_q)
    if d['temporal'] is not None:
        t=_obj(d['temporal'],set(asdict(cast(_TimeReducer,a._state.temporal))));template_t=cast(_TimeReducer,a._state.temporal)
        if t['max_age_ns'] != template_t.max_age_ns or t['scale'] != template_t.scale or t['state'] not in _CATEGORIES[:4]+('unknown',): _fail()
        duration={k:_integer(v) for k,v in _obj(t['duration'],set(_CATEGORIES)).items()}
        cursor=_integer(t['cursor'],bound,a.config.availability.market_cutoff_ns)
        if sum(duration.values())!=cursor-a.config.session.open_ns: _fail()
        anchor=_optional(t['anchor']);bid=_optional(t['bid']);ask=_optional(t['ask'])
        if anchor is not None and anchor>cursor: _fail()
        if anchor is not None and _quote_values(bid,ask,template_t.scale)[0] != t['state']: _fail()
        spread_sum=_integer(t['spread_sum'],0,10**38-1);checked_decimal128(spread_sum)
        s.temporal=_TimeReducer(cursor,template_t.max_age_ns,template_t.scale,t['state'],anchor,bid,ask,duration,spread_sum,_float(t['bps_sum']),_float(t['compensation']))
    for reducer in (s.bars,s.trades,s.top,s.quotes):
        if reducer is not None and (reducer.observed!=n or reducer.knowledge!=s.knowledge): _fail()
    for reducer in s.windows:
        if not set(reducer.knowledge)<=set(s.knowledge): _fail()
    rows_all=cast(list[Any],s.top.rows if s.top is not None else s.quotes.rows if s.quotes is not None else [])
    for row in rows_all:
        if row.input_id != a.population.metadata.source.input_id or s.first_key is None or s.last_key is None or not s.first_key <= (row.event_ns,row.order_key) <= s.last_key: _fail()
        if a._seed is not None and row.event_id == cast(str,a._seed.column('event_id').values[0]): _fail()  # type: ignore[union-attr]
    if not n and s.knowledge: _fail()
    if s.quotes is not None:
        valid=s.quotes.counts['normal']+s.quotes.counts['locked']
        if s.quotes.bps_sum<0 or s.quotes.bps_sum>20000*valid*(1+1e-12): _fail()
        if not valid and (s.quotes.spread.value or s.quotes.spread.overflow or s.quotes.bps_sum or s.quotes.compensation): _fail()
    if s.temporal is not None:
        temporal=s.temporal
        latest=s.last_key[0] if s.last_key is not None and {'bid','ask'}<=set(fields) else a.config.session.open_ns
        if temporal.cursor!=max(bound,latest): _fail()
        valid=temporal.duration['normal']+temporal.duration['locked']
        if temporal.bps_sum<0 or temporal.bps_sum>20000*valid*(1+1e-12) or not valid and (temporal.spread_sum or temporal.bps_sum or temporal.compensation): _fail()
        if s.last_key is not None and {'bid','ask'}<=set(fields) and temporal.anchor!=s.last_key[0]: _fail()
        if temporal.anchor is None and (temporal.bid is not None or temporal.ask is not None): _fail()
    if s.sealed is not None:
        if s.sealed.cutoff_ns!=a.config.availability.market_cutoff_ns or bound!=s.sealed.cutoff_ns or s.sealed.coverage.observed!=n or s.known_gap and s.sealed.coverage.complete: _fail()
    return s

def restore_state(state: AccumulatorState, family: Family, config: ConfigSpec, *, entity: EntityKey, population: StreamPopulation, prior_close: CanonicalBatch | None=None, seed: CanonicalBatch | None=None) -> SessionAccumulator:
    if type(state) is not AccumulatorState or state.schema_version!='2' or state.implementation_version!=__version__:
        raise ContractError(ErrorCode.INVALID_SCHEMA,'state schema/implementation version incompatible; no implicit migration')
    a=SessionAccumulator(family,config,entity=entity,population=population,prior_close=prior_close,seed=seed)
    if _binding(a)!=state.binding_digest:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,'state config/entity/source/enrichment/math binding mismatch')
    try:
        raw=_decode(json.loads(state.payload,object_pairs_hook=_pairs));a._state=_read(a,raw)
        if export_state(a)!=state: _fail()
        if a._state.sealed is not None: a.snapshot(a._state.sealed)
    except (ValueError,TypeError,KeyError,IndexError,RecursionError,AttributeError,OverflowError) as error:
        raise ContractError(ErrorCode.INVALID_SCHEMA,'malformed bounded state payload') from error
    return a
