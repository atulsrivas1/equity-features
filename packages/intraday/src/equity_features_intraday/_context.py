"""Owned bounded grid and in-memory non-executable context codec."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
import hashlib
import json
from typing import NoReturn, cast

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, ConfigSpec, ContractError, ErrorCode,
    Parameter, PriceUnit, SessionSpec, WindowSpec,
)

CONTEXT_SCHEMA = "equity-features.intraday-context.v1"
ALGORITHM = "intraday-v1"
I64_MIN = -(2**63)
I64_MAX = 2**63-1
MAX_CONTEXT_BYTES = 65_536


def fail(message: str, code: ErrorCode = ErrorCode.INVALID_CONFIG) -> NoReturn:
    raise ContractError(code, message)


def integer(value: object, minimum: int = I64_MIN, maximum: int = I64_MAX,
            code: ErrorCode = ErrorCode.BOUNDS) -> int:
    if type(value) is not int:
        fail("exact integer required")
    if not minimum <= value <= maximum:
        fail("integer outside declared bounds", code)
    return value


def label(value: object, limit: int = 128) -> str:
    if (type(value) is not str or not value.strip() or len(value) > limit
            or any(not 32 <= ord(c) <= 126 for c in value)):
        fail("bounded nonblank printable ASCII label required")
    return value


@dataclass(frozen=True)
class IntradayRun:
    session_id: str
    start_ns: int
    step_ns: int
    count: int

    def __post_init__(self) -> None:
        label(self.session_id)
        integer(self.start_ns)
        integer(self.step_ns, 1)
        integer(self.count, 1, 4096)
        integer(self.start_ns+self.step_ns*self.count)


@dataclass(frozen=True)
class Slot:
    index: int
    session_id: str
    start_ns: int
    end_ns: int


@dataclass(frozen=True)
class IntradayContext:
    instrument_id: str
    calendar_id: str
    grid_id: str
    revision: str
    sessions: tuple[SessionSpec, ...]
    runs: tuple[IntradayRun, ...]
    anchor_index: int
    target_index: int
    mode: str

    def __post_init__(self) -> None:
        for value in (self.instrument_id, self.calendar_id, self.grid_id, self.revision):
            label(value)
        if (type(self.sessions) not in (tuple, list) or not 1 <= len(self.sessions) <= 64
                or any(type(s) is not SessionSpec for s in self.sessions)):
            fail("1..64 concrete actual sessions required")
        if (type(self.runs) not in (tuple, list) or not 1 <= len(self.runs) <= 256
                or any(type(r) is not IntradayRun for r in self.runs)):
            fail("1..256 concrete governed runs required")
        object.__setattr__(self, "sessions", tuple(self.sessions))
        object.__setattr__(self, "runs", tuple(self.runs))
        for session in self.sessions:
            label(session.namespace)
            label(session.session_id)
            label(session.timezone_label, 64)
            if session.intervals:
                fail("bar membership belongs to explicit runs, not session intervals")
        if len({s.namespace for s in self.sessions}) != 1:
            fail("one session namespace required", ErrorCode.INCONSISTENT_IDENTITY)
        if len({s.session_id for s in self.sessions}) != len(self.sessions):
            fail("duplicate governed session", ErrorCode.DUPLICATE)
        if any(a.close_ns > b.open_ns for a, b in zip(self.sessions, self.sessions[1:])):
            fail("actual sessions overlap or are unordered", ErrorCode.INVALID_ORDER)
        sessions = {s.session_id: s for s in self.sessions}
        if {r.session_id for r in self.runs} != set(sessions):
            fail("every actual session needs its own governed run", ErrorCode.INCONSISTENT_IDENTITY)
        total = sum(r.count for r in self.runs)
        integer(total, 1, 4096)
        for run in self.runs:
            session = sessions[run.session_id]
            if run.start_ns < session.open_ns or run.start_ns+run.step_ns*run.count > session.close_ns:
                fail("run outside actual session bounds", ErrorCode.BOUNDS)
        if any(a.start_ns+a.step_ns*a.count > b.start_ns for a, b in zip(self.runs, self.runs[1:])):
            fail("runs overlap or are unordered", ErrorCode.INVALID_ORDER)
        integer(self.target_index, 0, total-1, ErrorCode.INVALID_CONFIG)
        integer(self.anchor_index, 0, self.target_index, ErrorCode.INVALID_CONFIG)
        if self.target_index != total-1 or self.mode not in ("reset", "carry"):
            fail("explicit final target and reset/carry mode required")
        if self.mode == "reset":
            slots = self.slots()
            target_session = slots[-1].session_id
            first = next(s.index for s in slots if s.session_id == target_session)
            if self.anchor_index != first:
                fail("reset anchor must be first governed target-session bar")
        if len(self.to_json().encode("ascii")) > MAX_CONTEXT_BYTES:
            fail("context exceeds 65536-byte transport bound", ErrorCode.BOUNDS)

    def slots(self) -> tuple[Slot, ...]:
        result: list[Slot] = []
        for run in self.runs:
            for j in range(run.count):
                result.append(Slot(len(result), run.session_id,
                                   run.start_ns+j*run.step_ns,
                                   run.start_ns+(j+1)*run.step_ns))
        return tuple(result)

    def to_json(self) -> str:
        return json.dumps({"schema": CONTEXT_SCHEMA, **asdict(self)}, sort_keys=True,
                          separators=(",", ":"), ensure_ascii=True, allow_nan=False)

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.to_json().encode("ascii")).hexdigest()

    @classmethod
    def from_json(cls, text: str) -> IntradayContext:
        if type(text) is not str:
            fail("in-memory context text required")
        try:
            raw = text.encode("ascii")
        except UnicodeEncodeError:
            fail("canonical ASCII context required")
        if len(raw) > MAX_CONTEXT_BYTES:
            fail("context transport exceeds limit", ErrorCode.BOUNDS)
        def unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
            result: dict[str, object] = {}
            for key, value in pairs:
                if key in result:
                    fail("duplicate context key")
                result[key] = value
            return result
        def constant(value: str) -> NoReturn:
            fail("nonfinite context number")
        try:
            value: object = json.loads(text, object_pairs_hook=unique, parse_constant=constant)
            data = fields(value, {"schema", "instrument_id", "calendar_id", "grid_id", "revision",
                                  "sessions", "runs", "anchor_index", "target_index", "mode"})
            if data["schema"] != CONTEXT_SCHEMA:
                fail("context schema mismatch", ErrorCode.INCOMPATIBLE_VERSION)
            sessions = sequence(data["sessions"], 64)
            runs = sequence(data["runs"], 256)
            context = cls(label(data["instrument_id"]), label(data["calendar_id"]),
                          label(data["grid_id"]), label(data["revision"]),
                          tuple(session_from_wire(s) for s in sessions),
                          tuple(run_from_wire(r) for r in runs),
                          integer(data["anchor_index"], 0, code=ErrorCode.INVALID_CONFIG),
                          integer(data["target_index"], 0, code=ErrorCode.INVALID_CONFIG),
                          label(data["mode"]))
            if context.to_json() != text:
                fail("noncanonical context encoding")
            return context
        except (ValueError, TypeError, KeyError, RecursionError) as error:
            if isinstance(error, ContractError):
                raise
            raise ContractError(ErrorCode.INVALID_CONFIG, "malformed context encoding") from error


def fields(value: object, keys: set[str]) -> dict[str, object]:
    if type(value) is not dict or set(value) != keys:
        fail("exact closed object fields required")
    return cast(dict[str, object], value)


def sequence(value: object, maximum: int) -> list[object]:
    if type(value) is not list or len(value) > maximum:
        fail("bounded concrete JSON array required")
    return cast(list[object], value)


def boolean(value: object) -> bool:
    if type(value) is not bool:
        fail("exact Boolean required")
    return value


def session_from_wire(value: object) -> SessionSpec:
    data = fields(value, {"namespace", "session_id", "open_ns", "close_ns", "timezone_label",
                          "intervals", "scheduled_close_ns", "early_close",
                          "include_opening_auction", "include_closing_auction"})
    if data["intervals"] != []:
        fail("session interval array must be empty")
    scheduled = data["scheduled_close_ns"]
    return SessionSpec(label(data["namespace"]), label(data["session_id"]),
                       integer(data["open_ns"]), integer(data["close_ns"]),
                       label(data["timezone_label"], 64), (),
                       None if scheduled is None else integer(scheduled),
                       boolean(data["early_close"]), boolean(data["include_opening_auction"]),
                       boolean(data["include_closing_auction"]))


def run_from_wire(value: object) -> IntradayRun:
    data = fields(value, {"session_id", "start_ns", "step_ns", "count"})
    return IntradayRun(label(data["session_id"]), integer(data["start_ns"]),
                       integer(data["step_ns"], 1), integer(data["count"], 1, 4096))


def build_intraday_config(context: IntradayContext, *, period: int, band_k: Fraction,
                          availability: AvailabilitySpec, adjustment: AdjustmentSpec,
                          price_unit: PriceUnit, evidence_limit: int = 0) -> ConfigSpec:
    if (type(context) is not IntradayContext or type(availability) is not AvailabilitySpec
            or type(adjustment) is not AdjustmentSpec or type(price_unit) is not PriceUnit):
        fail("concrete context/timing/action/unit required")
    integer(period, 1, 4096, ErrorCode.INVALID_CONFIG)
    integer(evidence_limit, 0, 10000, ErrorCode.INVALID_CONFIG)
    if (type(band_k) is not Fraction or not 1 <= band_k.numerator <= 1_000_000
            or not 1 <= band_k.denominator <= 1_000_000):
        fail("positive reduced rational multiplier with bounded coefficients required")
    for value in (adjustment.policy_version, adjustment.action_snapshot, adjustment.anchor, price_unit.currency):
        label(value)
    if availability.reconstruction_reason is not None:
        label(availability.reconstruction_reason)
    slots = context.slots()
    target = next(s for s in context.sessions if s.session_id == slots[-1].session_id)
    if not slots[-1].end_ns <= availability.market_cutoff_ns <= target.close_ns:
        fail("target completion/cutoff outside actual session", ErrorCode.BOUNDS)
    text = context.to_json()
    chunks = tuple(text[i:i+4096] for i in range(0, len(text), 4096))
    params: tuple[Parameter, ...] = (Parameter("period", period), Parameter("k_num", band_k.numerator),
              Parameter("k_den", band_k.denominator), Parameter("evidence_limit", evidence_limit),
              Parameter("context_schema", CONTEXT_SCHEMA), Parameter("context_sha256", context.digest),
              Parameter("context_chunks", len(chunks)))
    params += tuple(Parameter(f"context_{i:03}", chunk) for i, chunk in enumerate(chunks))
    return ConfigSpec("intraday.snapshot.v1", ALGORITHM, params, target,
                      WindowSpec(len(context.sessions), target.session_id,
                                 tuple(s.session_id for s in context.sessions), "completed_eod"),
                      availability, adjustment, price_unit)


def validate_config(context: IntradayContext, config: ConfigSpec) -> tuple[int, Fraction, int]:
    if type(context) is not IntradayContext or type(config) is not ConfigSpec:
        fail("concrete intraday context/config required")
    if config.algorithm_version != ALGORITHM:
        fail("intraday algorithm version differs", ErrorCode.INCOMPATIBLE_VERSION)
    values = {p.name: p.value for p in config.parameters}
    count = integer(values.get("context_chunks"), 1, 16)
    required = {"period", "k_num", "k_den", "evidence_limit", "context_schema",
                "context_sha256", "context_chunks"} | {f"context_{i:03}" for i in range(count)}
    if set(values) != required:
        fail("closed intraday operation parameters required")
    if values["context_schema"] != CONTEXT_SCHEMA:
        fail("context codec mismatch", ErrorCode.INCOMPATIBLE_VERSION)
    chunks: list[str] = []
    for i in range(count):
        text = values[f"context_{i:03}"]
        if type(text) is not str or not 1 <= len(text) <= 4096 or (i < count-1 and len(text) != 4096):
            fail("canonical bounded context chunks required")
        chunks.append(text)
    decoded = IntradayContext.from_json("".join(chunks))
    if decoded != context or values["context_sha256"] != context.digest:
        fail("context identity differs", ErrorCode.INCONSISTENT_IDENTITY)
    period = integer(values["period"], 1, 4096, ErrorCode.INVALID_CONFIG)
    numerator = integer(values["k_num"], 1, 1_000_000, ErrorCode.INVALID_CONFIG)
    denominator = integer(values["k_den"], 1, 1_000_000, ErrorCode.INVALID_CONFIG)
    k = Fraction(numerator, denominator)
    if (k.numerator, k.denominator) != (numerator, denominator):
        fail("multiplier must use its reduced canonical fraction")
    limit = integer(values["evidence_limit"], 0, 10000, ErrorCode.INVALID_CONFIG)
    if config.price_unit is None:
        fail("explicit price unit required", ErrorCode.INVALID_UNIT)
    expected = build_intraday_config(context, period=period, band_k=k,
                                     availability=config.availability, adjustment=config.adjustment,
                                     price_unit=config.price_unit, evidence_limit=limit)
    if config != expected:
        fail("configuration is not the final canonical intraday envelope", ErrorCode.INCONSISTENT_IDENTITY)
    return period, k, limit
