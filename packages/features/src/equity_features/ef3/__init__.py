"""Experimental EF3 supplied relative-statistics and daily log-volatility slices; pure, no I/O."""
from ._common import GRID_SCHEMA, DailyGrid, DailySlot
from ._definitions import EF3Definition, ef3_definitions, require_ef3_capability
from ._dispatch import compute_ef3
from ._logvol import (LOG_VOL, LOG_VOL_ALGORITHM, LOG_VOL_FEATURES, LOG_VOL_IDENTITY, LOG_VOL_POLICY,
                      LogVolatilitySettings, build_log_volatility_config, compute_log_volatility,
                      decode_log_volatility_config)
from ._relative import (BETA, CORRELATION, RELATIVE_ALGORITHM, RELATIVE_FEATURES, RELATIVE_IDENTITY,
                        RELATIVE_POLICY, RESIDUAL, RelativeStatsSettings, build_relative_stats_config,
                        compute_relative_stats, decode_relative_stats_config)

__all__ = ["BETA", "CORRELATION", "DailyGrid", "DailySlot", "EF3Definition", "GRID_SCHEMA", "LOG_VOL",
           "LOG_VOL_ALGORITHM", "LOG_VOL_FEATURES", "LOG_VOL_IDENTITY", "LOG_VOL_POLICY", "LogVolatilitySettings",
           "RELATIVE_ALGORITHM", "RELATIVE_FEATURES", "RELATIVE_IDENTITY", "RELATIVE_POLICY", "RESIDUAL",
           "RelativeStatsSettings", "build_log_volatility_config", "build_relative_stats_config", "compute_ef3",
           "compute_log_volatility", "compute_relative_stats", "decode_log_volatility_config",
           "decode_relative_stats_config", "ef3_definitions", "require_ef3_capability"]

from ._mean import (MEAN_ALGORITHM, MEAN_FEATURES, MEAN_IDENTITY, MEAN_POLICY, MeanRatioSettings,
                    build_mean_ratio_config, compute_volume_ratio_mean, decode_mean_ratio_config)
from ._pace import (PACE_ALGORITHM, PACE_FEATURES, PACE_IDENTITY, PACE_POLICY, PaceSettings, build_pace_config,
                    compute_volume_pace_robust, decode_pace_config)
from ._robust_definitions import EF3RobustDefinition, ef3_robust_definitions, require_ef3_robust_capability
from ._robust_dispatch import compute_ef3_robust
from ._robust_history import (ROBUST_ALGORITHM, ROBUST_FEATURES, ROBUST_IDENTITY, ROBUST_POLICY,
                              RobustHistorySettings, build_robust_history_config, compute_robust_history,
                              decode_robust_history_config)

__all__ += ["EF3RobustDefinition", "MEAN_ALGORITHM", "MEAN_FEATURES", "MEAN_IDENTITY", "MEAN_POLICY",
            "MeanRatioSettings", "PACE_ALGORITHM", "PACE_FEATURES", "PACE_IDENTITY", "PACE_POLICY", "PaceSettings",
            "ROBUST_ALGORITHM", "ROBUST_FEATURES", "ROBUST_IDENTITY", "ROBUST_POLICY", "RobustHistorySettings",
            "build_mean_ratio_config", "build_pace_config", "build_robust_history_config", "compute_ef3_robust",
            "compute_robust_history", "compute_volume_pace_robust", "compute_volume_ratio_mean",
            "decode_mean_ratio_config", "decode_pace_config", "decode_robust_history_config",
            "ef3_robust_definitions", "require_ef3_robust_capability"]

from ._adaptive import (ADAPTIVE_ALGORITHM, ADAPTIVE_FEATURES, ADAPTIVE_IDENTITY, ADAPTIVE_POLICY,
                        AdaptiveVolumeSettings, build_adaptive_volume_config, compute_adaptive_volume,
                        decode_adaptive_volume_config)
from ._breadth import (BREADTH_ALGORITHM, BREADTH_FEATURES, BREADTH_IDENTITY, BREADTH_POLICY, SessionBreadthSettings,
                       build_session_breadth_config, compute_session_breadth, decode_session_breadth_config)
from ._breadth_definitions import EF3BreadthDefinition, ef3_breadth_definitions, require_ef3_breadth_capability
from ._breadth_dispatch import compute_ef3_breadth
from ._observed import (OBSERVED_ALGORITHM, OBSERVED_FEATURES, OBSERVED_IDENTITY, OBSERVED_POLICY,
                        ObservedBreadthSettings, build_observed_breadth_config, compute_observed_breadth,
                        decode_observed_breadth_config)

__all__ += ["ADAPTIVE_ALGORITHM", "ADAPTIVE_FEATURES", "ADAPTIVE_IDENTITY", "ADAPTIVE_POLICY",
            "AdaptiveVolumeSettings", "BREADTH_ALGORITHM", "BREADTH_FEATURES", "BREADTH_IDENTITY", "BREADTH_POLICY",
            "EF3BreadthDefinition", "OBSERVED_ALGORITHM", "OBSERVED_FEATURES", "OBSERVED_IDENTITY",
            "OBSERVED_POLICY", "ObservedBreadthSettings", "SessionBreadthSettings", "build_adaptive_volume_config",
            "build_observed_breadth_config", "build_session_breadth_config", "compute_adaptive_volume",
            "compute_ef3_breadth", "compute_observed_breadth", "compute_session_breadth",
            "decode_adaptive_volume_config", "decode_observed_breadth_config", "decode_session_breadth_config",
            "ef3_breadth_definitions", "require_ef3_breadth_capability"]
