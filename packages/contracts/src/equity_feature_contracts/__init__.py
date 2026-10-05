"""Pure in-memory experimental contracts; optional backends import explicitly."""
from .inputs import (
    AdjustmentSpec, BatchMetadata, CanonicalBatch, Cell, Column, Coverage,
    DataKind, DType, Field, InputSchema, PriceUnit, SourceBinding, schema_for,
)

from .specs import AvailabilitySpec, ConfigSpec, IntervalSpec, Parameter, SessionSpec, WindowSpec

from .errors import ContractError, ErrorCode
from .results import (BreadthCounts, BreadthFraction, EntityKey, EvidenceRow,
    FeatureColumn, FeatureResult, InputBinding, QualityRow, Reason, ResultCell,
    ResultMetadata, Status, ValueType)

__version__ = "0.0.1a3"
__all__ = ["AdjustmentSpec", "BatchMetadata", "CanonicalBatch", "Cell", "Column",
           "Coverage", "DataKind", "DType", "Field", "InputSchema", "PriceUnit",
           "SourceBinding", "schema_for", "AvailabilitySpec", "ConfigSpec", "IntervalSpec",
           "Parameter", "SessionSpec", "WindowSpec", "ContractError", "ErrorCode",
           "BreadthCounts", "BreadthFraction", "EntityKey", "EvidenceRow", "FeatureColumn",
           "FeatureResult", "InputBinding", "QualityRow", "Reason", "ResultCell",
           "ResultMetadata", "Status", "ValueType"]
