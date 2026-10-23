"""Experimental EF2 supplied feature slices; pure, no I/O."""
from ._definitions import EF2Definition, ef2_definitions, require_ef2_capability
from ._dispatch import compute_ef2
from ._retracement import (RETRACEMENT_ALGORITHM, RETRACEMENT_IDENTITY, RETRACEMENT_POLICY,
                           RetracementSettings, build_retracement_config, compute_retracement_level,
                           decode_retracement_config)

__all__ = ["EF2Definition", "RETRACEMENT_ALGORITHM", "RETRACEMENT_IDENTITY", "RETRACEMENT_POLICY",
           "RetracementSettings", "build_retracement_config", "compute_ef2",
           "compute_retracement_level", "decode_retracement_config", "ef2_definitions",
           "require_ef2_capability"]
