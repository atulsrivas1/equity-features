"""Experimental DV1 definition-variant slices (log-return beta and correlation; window extremes; simple-mean ATR; core spread); pure, no I/O; internal, synthetic, pre-release."""
from ._definitions import DV1Definition, dv1_definitions, require_dv1_capability
from ._dispatch import compute_dv1
from ._relative_log import (LOG_BETA, LOG_CORRELATION, RLOG_ALGORITHM, RLOG_FEATURES, RLOG_IDENTITY, RLOG_POLICY,
                            RelativeLogSettings, build_relative_log_config, compute_relative_log,
                            decode_relative_log_config)
from ._window_extreme import (OFFSET_UNIT, WEXT_ALGORITHM, WEXT_FEATURES, WEXT_IDENTITY, WEXT_POLICY,
                              WINDOW_HIGH, WINDOW_HIGH_OFFSET, WINDOW_LOW, WINDOW_LOW_OFFSET, WindowExtremeSettings,
                              build_window_extreme_config, compute_window_extreme, decode_window_extreme_config)

__all__ = ["DV1Definition", "LOG_BETA", "LOG_CORRELATION", "RLOG_ALGORITHM", "RLOG_FEATURES", "RLOG_IDENTITY",
           "RLOG_POLICY", "RelativeLogSettings", "build_relative_log_config", "compute_dv1", "compute_relative_log",
           "decode_relative_log_config", "dv1_definitions", "require_dv1_capability",
           "OFFSET_UNIT", "WEXT_ALGORITHM", "WEXT_FEATURES", "WEXT_IDENTITY", "WEXT_POLICY", "WINDOW_HIGH",
           "WINDOW_HIGH_OFFSET", "WINDOW_LOW", "WINDOW_LOW_OFFSET", "WindowExtremeSettings",
           "build_window_extreme_config", "compute_window_extreme", "decode_window_extreme_config"]

from ._atr_simple_mean import (ATR_ALGORITHM, ATR_FEATURES, ATR_IDENTITY, ATR_MEAN, ATR_POLICY, AtrSimpleMeanSettings,
                               build_atr_simple_mean_config, compute_atr_simple_mean, decode_atr_simple_mean_config)

__all__ += ["ATR_ALGORITHM", "ATR_FEATURES", "ATR_IDENTITY", "ATR_MEAN", "ATR_POLICY", "AtrSimpleMeanSettings",
            "build_atr_simple_mean_config", "compute_atr_simple_mean", "decode_atr_simple_mean_config"]

from ._core_spread import (CORE_ALGORITHM, CORE_FEATURES, CORE_IDENTITY, CORE_POLICY, CORE_RANGE, CORE_STDEV,
                           CoreSpreadSettings, build_core_spread_config, compute_core_spread, decode_core_spread_config)

__all__ += ["CORE_ALGORITHM", "CORE_FEATURES", "CORE_IDENTITY", "CORE_POLICY", "CORE_RANGE", "CORE_STDEV",
            "CoreSpreadSettings", "build_core_spread_config", "compute_core_spread", "decode_core_spread_config"]
