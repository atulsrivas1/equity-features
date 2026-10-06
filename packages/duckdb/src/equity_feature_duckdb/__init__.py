"""Optional acquisition boundary; never imported by core calculations."""
from .resolver import (
    CatalogConfig, FilePin, ResolvedPartition, ResolvedSource,
    SourceSelection, resolve_source,
)

__version__ = "0.1.0a1"
__all__ = [
    "CatalogConfig", "FilePin", "ResolvedPartition", "ResolvedSource",
    "SourceSelection", "resolve_source",
]
