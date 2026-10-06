"""Optional acquisition boundary; never imported by core calculations."""
from .resolver import (
    CatalogConfig, FilePin, ResolvedPartition, ResolvedSource,
    SourceSelection, resolve_source,
)

from .mapping import (MappingPolicy, RowOccurrence, PriceConversion, MappingReport,
                      MappedSource, map_columns, parse_utc_ns)

__version__ = "0.1.0a2"
__all__ = [
    "CatalogConfig", "FilePin", "ResolvedPartition", "ResolvedSource",
    "SourceSelection", "resolve_source",
    "MappingPolicy", "RowOccurrence", "PriceConversion", "MappingReport",
    "MappedSource", "map_columns", "parse_utc_ns",
]
