"""Caller-supplied bounds and versioned deterministic configuration."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from typing import Any, TypeAlias
from .errors import ContractError, ErrorCode
from .inputs import AdjustmentSpec, I64_MIN, I64_MAX, PriceUnit

Scalar: TypeAlias = str | int | float | bool | None

def _ns(value: int) -> None:
    if type(value) is not int or not I64_MIN <= value <= I64_MAX:
        raise ContractError(ErrorCode.BOUNDS, "UTCns int64 required")

def _identity(value: str) -> None:
    if type(value) is not str or not value.strip():
        raise ContractError(ErrorCode.INVALID_CONFIG, "nonempty identity required")

@dataclass(frozen=True)
class IntervalSpec:
    name: str
    start_ns: int
    end_ns: int

    def __post_init__(self) -> None:
        _identity(self.name); _ns(self.start_ns); _ns(self.end_ns)
        if self.start_ns >= self.end_ns:
            raise ContractError(ErrorCode.INVALID_CONFIG, "half-open interval must have positive duration")

    def contains(self, event_ns: int) -> bool:
        _ns(event_ns)
        return self.start_ns <= event_ns < self.end_ns

@dataclass(frozen=True)
class SessionSpec:
    namespace: str
    session_id: str
    open_ns: int
    close_ns: int
    timezone_label: str
    intervals: tuple[IntervalSpec, ...] = ()
    scheduled_close_ns: int | None = None
    early_close: bool = False
    include_opening_auction: bool = False
    include_closing_auction: bool = False

    def __post_init__(self) -> None:
        for label in (self.namespace, self.session_id, self.timezone_label): _identity(label)
        _ns(self.open_ns); _ns(self.close_ns)
        if self.open_ns >= self.close_ns:
            raise ContractError(ErrorCode.INVALID_CONFIG, "session open must precede close")
        if type(self.intervals) not in (tuple, list) or any(type(x) is not IntervalSpec for x in self.intervals):
            raise ContractError(ErrorCode.INVALID_CONFIG, "concrete typed intervals required")
        object.__setattr__(self, "intervals", tuple(self.intervals))
        if len({x.name for x in self.intervals}) != len(self.intervals):
            raise ContractError(ErrorCode.INVALID_CONFIG, "duplicate interval name")
        if any(x.start_ns < self.open_ns or x.end_ns > self.close_ns for x in self.intervals):
            raise ContractError(ErrorCode.INVALID_CONFIG, "interval outside actual session bounds")
        if any(type(x) is not bool for x in (self.early_close, self.include_opening_auction, self.include_closing_auction)):
            raise ContractError(ErrorCode.INVALID_CONFIG, "Boolean session policies required")
        if self.scheduled_close_ns is not None:
            _ns(self.scheduled_close_ns)
            if self.scheduled_close_ns < self.close_ns or self.early_close != (self.close_ns < self.scheduled_close_ns):
                raise ContractError(ErrorCode.INVALID_CONFIG, "scheduled/actual early-close declaration mismatch")
        elif self.early_close:
            raise ContractError(ErrorCode.INVALID_CONFIG, "early close requires scheduled close evidence")

    def admits_event(self, event_ns: int, cutoff_ns: int, *, auction: str = "none", quote: bool = False) -> bool:
        _ns(event_ns); _ns(cutoff_ns)
        if auction not in ("none", "opening", "closing") or type(quote) is not bool:
            raise ContractError(ErrorCode.INVALID_CONFIG, "explicit event kind required")
        if quote and auction != "none":
            raise ContractError(ErrorCode.INVALID_CONFIG, "quotes have no auction event exception")
        if auction == "opening":
            return self.include_opening_auction and event_ns == self.open_ns and event_ns < cutoff_ns
        if auction == "closing":
            return self.include_closing_auction and event_ns == self.close_ns and cutoff_ns == self.close_ns
        return self.open_ns <= event_ns < min(cutoff_ns, self.close_ns)

@dataclass(frozen=True)
class AvailabilitySpec:
    market_cutoff_ns: int
    knowledge_cutoff_ns: int
    evaluation_ns: int
    mode: str = "known_at"
    reconstruction_reason: str | None = None

    def __post_init__(self) -> None:
        for value in (self.market_cutoff_ns, self.knowledge_cutoff_ns, self.evaluation_ns): _ns(value)
        if self.mode == "known_at":
            if self.market_cutoff_ns > self.evaluation_ns or self.knowledge_cutoff_ns > self.evaluation_ns or self.reconstruction_reason is not None:
                raise ContractError(ErrorCode.INVALID_CONFIG, "causal C/K cannot exceed E or carry reconstruction reason")
        elif self.mode == "reconstruction":
            if self.reconstruction_reason is None:
                raise ContractError(ErrorCode.INVALID_CONFIG, "reconstruction reason required")
            _identity(self.reconstruction_reason)
        else:
            raise ContractError(ErrorCode.INVALID_CONFIG, "unsupported availability mode")

    def knowledge_reason(self, known_at_ns: int | None) -> str | None:
        if known_at_ns is not None: _ns(known_at_ns)
        if self.mode == "reconstruction": return None
        if known_at_ns is None: return "unknown_availability"
        if known_at_ns > self.knowledge_cutoff_ns: return "future_knowledge"
        return None

@dataclass(frozen=True)
class WindowSpec:
    count: int
    target_session_id: str
    governed_sessions: tuple[str, ...]
    anchor: str = "prior_only"

    def __post_init__(self) -> None:
        if type(self.count) is not int or not 1 <= self.count <= I64_MAX:
            raise ContractError(ErrorCode.INVALID_CONFIG, "positive governed window count required")
        _identity(self.target_session_id)
        if type(self.governed_sessions) not in (tuple, list):
            raise ContractError(ErrorCode.INVALID_CONFIG, "concrete governed session sequence required")
        object.__setattr__(self, "governed_sessions", tuple(self.governed_sessions))
        for session in self.governed_sessions: _identity(session)
        if len(set(self.governed_sessions)) != len(self.governed_sessions) or self.target_session_id not in self.governed_sessions:
            raise ContractError(ErrorCode.INVALID_CONFIG, "unique governed slots including target required")
        if self.anchor not in ("prior_only", "completed_eod"):
            raise ContractError(ErrorCode.INVALID_CONFIG, "unsupported window anchor")

    def selected_sessions(self) -> tuple[str, ...]:
        end = self.governed_sessions.index(self.target_session_id) + (self.anchor == "completed_eod")
        return self.governed_sessions[max(0, end-self.count):end]

    @property
    def history_complete(self) -> bool:
        return len(self.selected_sessions()) == self.count

@dataclass(frozen=True)
class Parameter:
    name: str
    value: Scalar

    def __post_init__(self) -> None:
        _identity(self.name)
        if type(self.value) not in (str, int, float, bool, type(None)) or (type(self.value) is float and not math.isfinite(self.value)):
            raise ContractError(ErrorCode.INVALID_CONFIG, "finite scalar parameter required")

@dataclass(frozen=True)
class ConfigSpec:
    identity: str
    algorithm_version: str
    parameters: tuple[Parameter, ...]
    session: SessionSpec
    window: WindowSpec
    availability: AvailabilitySpec
    adjustment: AdjustmentSpec = AdjustmentSpec()
    price_unit: PriceUnit | None = None
    schema_version: str = "1"

    def __post_init__(self) -> None:
        _identity(self.identity); _identity(self.algorithm_version)
        if self.schema_version != "1": raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported configuration schema")
        if type(self.parameters) not in (tuple, list) or any(type(p) is not Parameter for p in self.parameters):
            raise ContractError(ErrorCode.INVALID_CONFIG, "concrete typed parameter sequence required")
        object.__setattr__(self, "parameters", tuple(sorted(self.parameters, key=lambda x: x.name)))
        if len({p.name for p in self.parameters}) != len(self.parameters): raise ContractError(ErrorCode.INVALID_CONFIG, "duplicate parameter")
        if type(self.session) is not SessionSpec or type(self.window) is not WindowSpec or type(self.availability) is not AvailabilitySpec or type(self.adjustment) is not AdjustmentSpec or (self.price_unit is not None and type(self.price_unit) is not PriceUnit):
            raise ContractError(ErrorCode.INVALID_CONFIG, "typed immutable configuration components required")
        if self.session.session_id != self.window.target_session_id:
            raise ContractError(ErrorCode.INVALID_CONFIG, "session/window target identity mismatch")

    def to_json(self) -> str:
        value = asdict(self)
        value["parameters"] = [{"name": p.name, "value": {"float64": p.value.hex()} if type(p.value) is float else p.value} for p in sorted(self.parameters, key=lambda x: x.name)]
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()

    @classmethod
    def from_json(cls, text: str) -> ConfigSpec:
        if type(text) is not str: raise ContractError(ErrorCode.INVALID_CONFIG, "in-memory JSON text required")
        def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
            result: dict[str, Any] = {}
            for key, value in pairs:
                if key in result: raise ContractError(ErrorCode.INVALID_CONFIG, "duplicate JSON key")
                result[key] = value
            return result
        def reject_constant(value: str) -> Any:
            raise ContractError(ErrorCode.INVALID_CONFIG, f"nonfinite JSON number: {value}")
        try:
            raw = json.loads(text, object_pairs_hook=unique, parse_constant=reject_constant)
            params = []
            for p in raw.pop("parameters"):
                value = p["value"]
                if type(value) is dict:
                    if set(value) != {"float64"} or type(value["float64"]) is not str: raise ContractError(ErrorCode.INVALID_CONFIG, "invalid float encoding")
                    value = float.fromhex(value["float64"])
                if set(p) != {"name", "value"}: raise ContractError(ErrorCode.INVALID_CONFIG, "unknown parameter field")
                params.append(Parameter(p["name"], value))
            session = raw.pop("session")
            session["intervals"] = tuple(IntervalSpec(**x) for x in session["intervals"])
            unit = raw.pop("price_unit")
            return cls(parameters=tuple(params), session=SessionSpec(**session), window=WindowSpec(**raw.pop("window")), availability=AvailabilitySpec(**raw.pop("availability")), adjustment=AdjustmentSpec(**raw.pop("adjustment")), price_unit=PriceUnit(**unit) if unit is not None else None, **raw)
        except ContractError:
            raise
        except (ValueError, KeyError, TypeError, AttributeError) as error:
            raise ContractError(ErrorCode.INVALID_CONFIG, "invalid configuration envelope") from error
