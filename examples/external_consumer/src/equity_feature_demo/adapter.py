"""Synthetic historical BAR acquisition, outside both numerical distributions."""
from dataclasses import dataclass, replace
from typing import Iterator, cast
from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, CanonicalBatch, Column, ContractError, Coverage, DataKind, PriceUnit, SourceBinding, validate_batch,
)
from equity_feature_contracts.adapters import (
    AcquisitionRequest, AdapterBatch, AdapterCapabilities, Cancellation, SourceError,
    SourceErrorCode, require_adapter_capability,
)
from equity_feature_contracts.adapter_kit import ConformanceCase, run_conformance
from equity_feature_demo import FEATURE_ID, calculate, definition, fixture
from equity_features.custom import CustomInput, CustomRegistry, CustomRequest


@dataclass(frozen=True)
class NeverCancelled:
    def is_cancelled(self) -> bool:
        return False


@dataclass(frozen=True)
class InMemoryBarAdapter:
    source: SourceBinding
    data: CanonicalBatch | None
    namespace: str = "demo"
    price_unit: PriceUnit = PriceUnit(0, "USD")
    start_ns: int = 100
    end_ns: int = 200

    def __post_init__(self) -> None:
        try:
            self._validate_fixture()
        except ContractError as error:
            raise SourceError(SourceErrorCode.SCHEMA, "synthetic fixture violates canonical source contract") from error

    def _validate_fixture(self) -> None:
        if type(self.source) is not SourceBinding or (self.data is not None and type(self.data) is not CanonicalBatch):
            raise SourceError(SourceErrorCode.SCHEMA, "typed synthetic source and supplied canonical fixture required")
        AcquisitionRequest("fixture", DataKind.BAR, self.namespace, ("A",), ("S",),
            self.start_ns, self.end_ns, self.source.snapshot_id, self.price_unit,
            AvailabilitySpec(self.end_ns, self.end_ns, self.end_ns), selection="completed_intervals")
        if self.data is not None:
            meta = self.data.metadata
            if (self.data.kind != DataKind.BAR or meta.source != self.source or meta.namespace != self.namespace
                    or meta.price_unit != self.price_unit or meta.adjustment != AdjustmentSpec()
                    or meta.coverage != Coverage(self.data.row_count, self.data.row_count, True)):
                raise SourceError(SourceErrorCode.SCHEMA, "fixed synthetic fixture metadata mismatch")
            validate_batch(self.data)
            fields = {c.name: c.values for c in self.data.columns}
            if any(not self.start_ns <= cast(int, start) < cast(int, end) <= self.end_ns
                   for start, end in zip(fields["start_ns"], fields["end_ns"], strict=True)):
                raise SourceError(SourceErrorCode.SCHEMA, "fixture outside declared source bounds")

    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities((DataKind.BAR,), (self.namespace,), (self.price_unit,), max_batch_rows=1024)

    def iter_batches(self, request: AcquisitionRequest, cancellation: Cancellation) -> Iterator[AdapterBatch]:
        require_adapter_capability(self.capabilities(), request)
        if (request.snapshot_id != self.source.snapshot_id or request.start_ns < self.start_ns
                or request.end_ns > self.end_ns or request.adjustment != AdjustmentSpec()):
            raise SourceError(SourceErrorCode.UNSUPPORTED, "request outside synthetic fixture contract")
        if cancellation.is_cancelled():
            raise SourceError(SourceErrorCode.CANCELLED, "cancelled before synthetic acquisition")
        if self.data is None:
            yield AdapterBatch(request.request_id, 0, True, self.source, Coverage(None, 0, False),
                Coverage(None, 0, False), None, "missing", "synthetic fixture absent")
            return
        fields = {c.name: c.values for c in self.data.columns}
        selected = tuple(i for i in range(self.data.row_count)
            if fields["instrument_id"][i] in request.instruments and fields["session_id"][i] in request.sessions
            and request.start_ns <= cast(int, fields["start_ns"][i]) < cast(int, fields["end_ns"][i]) <= request.end_ns)
        count = len(selected)
        chunks = max(1, (count + request.max_batch_rows - 1) // request.max_batch_rows)
        if count > request.max_rows or chunks > request.max_batches:
            raise SourceError(SourceErrorCode.LIMIT, "complete fixture selection exceeds declared bounds")
        for ordinal in range(chunks):
            if cancellation.is_cancelled():
                raise SourceError(SourceErrorCode.CANCELLED, "cancelled between synthetic chunks")
            indices = selected[ordinal * request.max_batch_rows:(ordinal + 1) * request.max_batch_rows]
            try:
                source = replace(self.source, input_id=f"{self.source.input_id}:{request.request_id}:{ordinal}")
                batch = CanonicalBatch(DataKind.BAR,
                    tuple(Column(c.name, tuple(c.values[i] for i in indices)) for c in self.data.columns),
                    replace(self.data.metadata, source=source))
            except ContractError as error:
                raise SourceError(SourceErrorCode.SCHEMA, "synthetic chunk violates canonical source contract") from error
            yield AdapterBatch(request.request_id, ordinal, ordinal == chunks - 1, source,
                self.data.metadata.coverage, Coverage(len(indices), len(indices), True), batch)


def adapter_fixture() -> tuple[InMemoryBarAdapter, AcquisitionRequest]:
    supplied = fixture()
    data = supplied.inputs[0].batch
    adapter = InMemoryBarAdapter(data.metadata.source, data)
    request = AcquisitionRequest("consumer", DataKind.BAR, "demo", ("A",), ("S",), 100, 200,
        data.metadata.source.snapshot_id, PriceUnit(0, "USD"), supplied.config.availability,
        selection="completed_intervals", max_batch_rows=2, max_rows=2, max_batches=2)
    return adapter, request


def main() -> None:
    adapter, request = adapter_fixture()
    batches = tuple(adapter.iter_batches(request, NeverCancelled()))
    case = ConformanceCase("actual-installed-adapter", request, adapter.capabilities(), batches)
    assert run_conformance((case,)).passed
    assert len(batches) == 1 and batches[0].batch is not None
    original = fixture()
    custom = CustomRequest((CustomInput("bars", batches[0].batch),), original.config, original.entity)
    result = CustomRegistry("demo").register(definition(), calculate).compute(FEATURE_ID, custom)
    assert result.values[0].values == (5/100,)
    assert result.metadata.inputs[0].metadata.source == batches[0].source
    print("Installed external BAR adapter passed public SDK conformance and custom5/100 binding.")
