"""Experimental EF1 supplied feature slices, including observables; no I/O."""
from ._context import build_ef1_config, decode_ef1_context
from ._definitions import EF1Definition, ef1_definitions
from ._dispatch import compute_ef1

__all__ = ["EF1Definition", "build_ef1_config", "decode_ef1_context",
           "ef1_definitions", "compute_ef1"]
