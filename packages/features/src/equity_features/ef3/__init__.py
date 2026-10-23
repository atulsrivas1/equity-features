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
