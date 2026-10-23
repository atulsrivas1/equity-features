"""Experimental EF4 slices (tape windows and notional top-K; quote dynamics and VWAP path); pure, no I/O."""
from ._definitions import QuoteVwapDefinition, quote_vwap_definitions, require_quote_vwap_capability
from ._dispatch import compute_quote_vwap
from ._quote import (QUOTE_ALGORITHM, QUOTE_FEATURES, QUOTE_IDENTITY, QUOTE_POLICY, QuoteDynamicsSettings,
                     build_quote_dynamics_config, compute_quote_dynamics, decode_quote_dynamics_config)
from ._tape_definitions import EF4TapeDefinition, ef4_tape_definitions, require_ef4_tape_capability
from ._tape_dispatch import compute_ef4_tape
from ._tape_topk import (NotionalPartial, NotionalTopKSettings, TOP_K_ALGORITHM, TOP_K_FEATURE, TOP_K_FEATURES,
                         TOP_K_IDENTITY, TOP_K_POLICY, build_notional_top_k_config, compute_trade_top_k_notional,
                         decode_notional_top_k_config, merge_trade_top_k_notional, notional_cell, notional_key)
from ._tape_window import (TAPE_ALGORITHM, TAPE_FEATURES, TAPE_IDENTITY, TAPE_POLICY, TapeWindowSettings,
                           build_tape_window_config, compute_tape_window, decode_tape_window_config)
from ._vwap import (VWAP_ALGORITHM, VWAP_FEATURES, VWAP_IDENTITY, VWAP_POLICY, VwapPathSettings,
                    build_vwap_path_config, compute_vwap_path, decode_vwap_path_config)

__all__ = ["EF4TapeDefinition", "NotionalPartial", "NotionalTopKSettings", "QUOTE_ALGORITHM", "QUOTE_FEATURES",
           "QUOTE_IDENTITY", "QUOTE_POLICY", "QuoteDynamicsSettings", "QuoteVwapDefinition", "TAPE_ALGORITHM",
           "TAPE_FEATURES", "TAPE_IDENTITY", "TAPE_POLICY", "TOP_K_ALGORITHM", "TOP_K_FEATURE", "TOP_K_FEATURES",
           "TOP_K_IDENTITY", "TOP_K_POLICY", "TapeWindowSettings", "VWAP_ALGORITHM", "VWAP_FEATURES",
           "VWAP_IDENTITY", "VWAP_POLICY", "VwapPathSettings", "build_notional_top_k_config",
           "build_quote_dynamics_config", "build_tape_window_config", "build_vwap_path_config", "compute_ef4_tape",
           "compute_quote_dynamics", "compute_quote_vwap", "compute_tape_window", "compute_trade_top_k_notional",
           "compute_vwap_path", "decode_notional_top_k_config", "decode_quote_dynamics_config",
           "decode_tape_window_config", "decode_vwap_path_config", "ef4_tape_definitions",
           "merge_trade_top_k_notional", "notional_cell", "notional_key", "quote_vwap_definitions",
           "require_ef4_tape_capability", "require_quote_vwap_capability"]
from ._bar_projection import (BAR_ALGORITHM, BAR_FEATURES, BAR_GRID_SCHEMA, BAR_IDENTITY, BAR_POLICY, BarGrid,
                              BarProjectionSettings, BarSlot, build_bar_projection_config, compute_bar_projection,
                              decode_bar_projection_config)
from ._path_projections_definitions import (EF4PathProjectionsDefinition, ef4_path_projections_definitions,
                                            require_ef4_path_projections_capability)
from ._path_projections_dispatch import compute_ef4_path_projections
from ._rate_projection import (RATE_ALGORITHM, RATE_FEATURES, RATE_IDENTITY, RATE_POLICY, RateProjectionSettings,
                               build_rate_projection_config, compute_rate_projection,
                               decode_rate_projection_config)
from ._relative_excess import (RELATIVE_ALGORITHM, RELATIVE_FEATURES, RELATIVE_IDENTITY, RELATIVE_POLICY,
                               RelativeExcessSettings, build_relative_excess_config, compute_relative_excess,
                               decode_relative_excess_config, encode_core_ids)
from ._session_projection import (SESSION_ALGORITHM, SESSION_FEATURES, SESSION_IDENTITY, SESSION_POLICY,
                                  SessionProjectionSettings, build_session_projection_config,
                                  compute_session_projection, decode_session_projection_config)

__all__ += ["BAR_ALGORITHM", "BAR_FEATURES", "BAR_GRID_SCHEMA", "BAR_IDENTITY", "BAR_POLICY", "BarGrid",
            "BarProjectionSettings", "BarSlot", "EF4PathProjectionsDefinition", "RATE_ALGORITHM", "RATE_FEATURES",
            "RATE_IDENTITY", "RATE_POLICY", "RELATIVE_ALGORITHM", "RELATIVE_FEATURES", "RELATIVE_IDENTITY",
            "RELATIVE_POLICY", "RateProjectionSettings", "RelativeExcessSettings", "SESSION_ALGORITHM",
            "SESSION_FEATURES", "SESSION_IDENTITY", "SESSION_POLICY", "SessionProjectionSettings",
            "build_bar_projection_config", "build_rate_projection_config", "build_relative_excess_config",
            "build_session_projection_config", "compute_bar_projection", "compute_ef4_path_projections",
            "compute_rate_projection", "compute_relative_excess", "compute_session_projection",
            "decode_bar_projection_config", "decode_rate_projection_config", "decode_relative_excess_config",
            "decode_session_projection_config", "ef4_path_projections_definitions", "encode_core_ids",
            "require_ef4_path_projections_capability"]
