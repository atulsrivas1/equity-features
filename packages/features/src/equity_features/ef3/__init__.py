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
