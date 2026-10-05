"""Pure in-memory experimental contracts; optional backends import explicitly."""
from .inputs import (
    AdjustmentSpec, BatchMetadata, CanonicalBatch, Cell, Column, Coverage,
    DataKind, DType, Field, InputSchema, PriceUnit, SourceBinding, schema_for,
)

from .specs import AvailabilitySpec, ConfigSpec, IntervalSpec, Parameter, SessionSpec, WindowSpec

__version__ = "0.0.1a2"
__all__ = ["AdjustmentSpec", "BatchMetadata", "CanonicalBatch", "Cell", "Column",
           "Coverage", "DataKind", "DType", "Field", "InputSchema", "PriceUnit",
           "SourceBinding", "schema_for", "AvailabilitySpec", "ConfigSpec", "IntervalSpec",
           "Parameter", "SessionSpec", "WindowSpec"]
