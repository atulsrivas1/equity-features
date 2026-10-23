"""Experimental EF4 tape slices (rolling trade windows with tick-rule signed volume, notional-ranked largest prints); pure, no I/O."""
from ._tape_definitions import EF4TapeDefinition, ef4_tape_definitions, require_ef4_tape_capability
from ._tape_dispatch import compute_ef4_tape
from ._tape_topk import (NotionalPartial, NotionalTopKSettings, TOP_K_ALGORITHM, TOP_K_FEATURE, TOP_K_FEATURES,
                         TOP_K_IDENTITY, TOP_K_POLICY, build_notional_top_k_config, compute_trade_top_k_notional,
                         decode_notional_top_k_config, merge_trade_top_k_notional, notional_cell, notional_key)
from ._tape_window import (TAPE_ALGORITHM, TAPE_FEATURES, TAPE_IDENTITY, TAPE_POLICY, TapeWindowSettings,
                           build_tape_window_config, compute_tape_window, decode_tape_window_config)

__all__ = ["EF4TapeDefinition", "NotionalPartial", "NotionalTopKSettings", "TAPE_ALGORITHM", "TAPE_FEATURES",
           "TAPE_IDENTITY", "TAPE_POLICY", "TOP_K_ALGORITHM", "TOP_K_FEATURE", "TOP_K_FEATURES", "TOP_K_IDENTITY",
           "TOP_K_POLICY", "TapeWindowSettings", "build_notional_top_k_config", "build_tape_window_config",
           "compute_ef4_tape", "compute_tape_window", "compute_trade_top_k_notional", "decode_notional_top_k_config",
           "decode_tape_window_config", "ef4_tape_definitions", "merge_trade_top_k_notional", "notional_cell",
           "notional_key", "require_ef4_tape_capability"]
