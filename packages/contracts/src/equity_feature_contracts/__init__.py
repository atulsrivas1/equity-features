"""Pure in-memory experimental contracts; optional backends import explicitly."""
from .inputs import (
    AdjustmentSpec, BatchMetadata, CanonicalBatch, Cell, Column, Coverage,
    DataKind, DType, Field, InputSchema, InputScope, IntervalCoverage, PriceUnit, SourceBinding, schema_for,
)

from .specs import AvailabilitySpec, ConfigSpec, IntervalSpec, Parameter, SessionSpec, WindowSpec

from .errors import ContractError, ErrorCode
from .results import (QuoteDurations, TimeWeightedSpread, QuoteStateCounts, QuoteObservation, SampledSpread, TopKTrades, TopKTradeRow, IntervalOHLCV, IntervalOHLCVRow, IntervalVolumeShares, IntervalVolumeShareRow, BreadthCounts, BreadthFraction, EntityKey, EvidenceRow,
    FeatureColumn, FeatureResult, InputBinding, QualityRow, Reason, ResultCell,
    ResultMetadata, Status, ValueType)

from .validation import (KnowledgeExclusion, ValidationReport, checked_decimal128,
    checked_int64, checked_product, checked_sum, quote_state, require_compatible_inputs, validate_batch)
from .normalization import (NormalizationReport, NormalizedBatch, QuantizedPrices,
    normalize_batch, quantize_float_prices)

from .streaming import StreamPopulation, PrefixCoverage, AccumulatorState, PartitionSpan

from .registry import (Capabilities, FeatureDefinition, InputRequirement,
    OutputField, Registry, builtin_registry)

from .history import HistoryContext, SMAReference
from .volume import VolumeBaseline, TargetVolume
from .buckets import VolumeBucket, BucketContext, IntervalBaseline, BucketVolume
from .relative import ReturnReference, RelativeSpec, SectorBenchmark
from .policies import ActionPolicy, ReferenceFact, PolicyAdmission, AdjustmentApplication, ClassificationAdmission

__version__ = "0.0.3a7"
__all__ = ["ReturnReference", "RelativeSpec", "SectorBenchmark", "VolumeBucket", "BucketContext", "IntervalBaseline", "BucketVolume", "VolumeBaseline", "TargetVolume", "SMAReference", "HistoryContext", "ActionPolicy", "ReferenceFact", "PolicyAdmission", "AdjustmentApplication", "ClassificationAdmission", "PartitionSpan", "AccumulatorState", "StreamPopulation", "PrefixCoverage", "QuoteDurations", "TimeWeightedSpread", "QuoteStateCounts", "QuoteObservation", "SampledSpread", "TopKTrades", "TopKTradeRow", "AdjustmentSpec", "BatchMetadata", "CanonicalBatch", "Cell", "Column",
           "IntervalCoverage", "IntervalOHLCV", "IntervalOHLCVRow", "IntervalVolumeShares", "IntervalVolumeShareRow", "InputScope", "Coverage", "DataKind", "DType", "Field", "InputSchema", "PriceUnit",
           "SourceBinding", "schema_for", "AvailabilitySpec", "ConfigSpec", "IntervalSpec",
           "Parameter", "SessionSpec", "WindowSpec", "ContractError", "ErrorCode",
           "BreadthCounts", "BreadthFraction", "EntityKey", "EvidenceRow", "FeatureColumn",
           "FeatureResult", "InputBinding", "QualityRow", "Reason", "ResultCell",
           "ResultMetadata", "Status", "ValueType", "KnowledgeExclusion", "ValidationReport",
           "checked_decimal128", "checked_int64", "checked_product", "checked_sum",
           "quote_state", "require_compatible_inputs", "validate_batch", "NormalizationReport",
           "NormalizedBatch", "QuantizedPrices", "normalize_batch", "quantize_float_prices",
           "Capabilities", "FeatureDefinition", "InputRequirement", "OutputField",
           "Registry", "builtin_registry"]
