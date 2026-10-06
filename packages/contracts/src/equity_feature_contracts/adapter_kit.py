"""Reusable pure conformance of supplied finite deliveries and captured error codes."""
from __future__ import annotations

from dataclasses import dataclass
from .adapters import (
    AcquisitionRequest, AdapterBatch, AdapterCapabilities, SourceError,
    SourceErrorCode, validate_delivery,
)


@dataclass(frozen=True)
class ConformanceCase:
    case_id: str
    request: AcquisitionRequest
    capabilities: AdapterCapabilities
    batches: tuple[AdapterBatch, ...]
    expected_error: SourceErrorCode | None = None
    acquisition_error: SourceErrorCode | None = None
    live: bool = False

    def __post_init__(self) -> None:
        if (type(self.case_id) is not str or not self.case_id.strip()
                or type(self.request) is not AcquisitionRequest
                or type(self.capabilities) is not AdapterCapabilities or type(self.live) is not bool):
            raise SourceError(SourceErrorCode.SCHEMA, "typed named conformance case required")
        if (type(self.batches) not in (tuple, list)
                or any(type(x) is not AdapterBatch for x in self.batches)
                or any(x is not None and type(x) is not SourceErrorCode
                       for x in (self.expected_error, self.acquisition_error))):
            raise SourceError(SourceErrorCode.SCHEMA, "finite typed delivery/error facts required")
        object.__setattr__(self, "batches", tuple(self.batches))
        if self.acquisition_error is not None and self.batches:
            raise SourceError(SourceErrorCode.SCHEMA, "captured source errors do not certify partial deliveries")


@dataclass(frozen=True)
class ConformanceOutcome:
    case_id: str
    expected_error: SourceErrorCode | None
    observed_error: SourceErrorCode | None

    def __post_init__(self) -> None:
        if (type(self.case_id) is not str or not self.case_id.strip()
                or any(x is not None and type(x) is not SourceErrorCode
                       for x in (self.expected_error, self.observed_error))):
            raise SourceError(SourceErrorCode.SCHEMA, "named typed conformance outcome required")

    @property
    def passed(self) -> bool:
        return self.expected_error == self.observed_error


@dataclass(frozen=True)
class ConformanceReport:
    outcomes: tuple[ConformanceOutcome, ...]

    def __post_init__(self) -> None:
        if (type(self.outcomes) not in (tuple, list)
                or any(type(x) is not ConformanceOutcome for x in self.outcomes)
                or len({x.case_id for x in self.outcomes}) != len(self.outcomes)):
            raise SourceError(SourceErrorCode.SCHEMA, "concrete unique conformance outcomes required")
        object.__setattr__(self, "outcomes", tuple(self.outcomes))

    @property
    def passed(self) -> bool:
        return bool(self.outcomes) and all(x.passed for x in self.outcomes)


def run_conformance(cases: tuple[ConformanceCase, ...], *, max_cases: int = 128) -> ConformanceReport:
    """No adapter invocation, lazy collection, source access or exception-message retention."""
    if type(max_cases) is not int or not 1 <= max_cases <= 10000:
        raise SourceError(SourceErrorCode.LIMIT, "conformance case limit must be1..10000")
    if type(cases) not in (tuple, list) or not cases or any(type(x) is not ConformanceCase for x in cases):
        raise SourceError(SourceErrorCode.SCHEMA, "concrete nonempty conformance cases required")
    if len(cases) > max_cases:
        raise SourceError(SourceErrorCode.LIMIT, "conformance case bound exceeded")
    if len({x.case_id for x in cases}) != len(cases):
        raise SourceError(SourceErrorCode.SCHEMA, "conformance case IDs must be unique")
    outcomes = []
    for case in cases:
        observed = case.acquisition_error
        if observed is None:
            try:
                validate_delivery(case.request, case.capabilities, case.batches, live=case.live)
            except SourceError as error:
                observed = error.code
        outcomes.append(ConformanceOutcome(case.case_id, case.expected_error, observed))
    return ConformanceReport(tuple(outcomes))
