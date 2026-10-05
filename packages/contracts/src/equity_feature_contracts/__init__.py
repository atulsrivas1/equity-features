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

from .validation import (KnowledgeExclusion, ValidationReport, checked_decimal128,
    checked_int64, checked_product, checked_sum, quote_state, require_compatible_inputs, validate_batch)
from .normalization import (NormalizationReport, NormalizedBatch, QuantizedPrices,
    normalize_batch, quantize_float_prices)

__version__ = "0.0.1a4"
__all__ = ["AdjustmentSpec", "BatchMetadata", "CanonicalBatch", "Cell", "Column",
           "Coverage", "DataKind", "DType", "Field", "InputSchema", "PriceUnit",
           "SourceBinding", "schema_for", "AvailabilitySpec", "ConfigSpec", "IntervalSpec",
           "Parameter", "SessionSpec", "WindowSpec", "ContractError", "ErrorCode",
           "BreadthCounts", "BreadthFraction", "EntityKey", "EvidenceRow", "FeatureColumn",
           "FeatureResult", "InputBinding", "QualityRow", "Reason", "ResultCell",
           "ResultMetadata", "Status", "ValueType", "KnowledgeExclusion", "ValidationReport",
           "checked_decimal128", "checked_int64", "checked_product", "checked_sum",
           "quote_state", "require_compatible_inputs", "validate_batch", "NormalizationReport",
           "NormalizedBatch", "QuantizedPrices", "normalize_batch", "quantize_float_prices"]
