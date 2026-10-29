"""Experimental DV1 definition-variant slices (log-return beta and correlation); pure, no I/O; internal, synthetic, pre-release."""
from ._definitions import DV1Definition, dv1_definitions, require_dv1_capability
from ._dispatch import compute_dv1
from ._relative_log import (LOG_BETA, LOG_CORRELATION, RLOG_ALGORITHM, RLOG_FEATURES, RLOG_IDENTITY, RLOG_POLICY,
                            RelativeLogSettings, build_relative_log_config, compute_relative_log,
                            decode_relative_log_config)

__all__ = ["DV1Definition", "LOG_BETA", "LOG_CORRELATION", "RLOG_ALGORITHM", "RLOG_FEATURES", "RLOG_IDENTITY",
           "RLOG_POLICY", "RelativeLogSettings", "build_relative_log_config", "compute_dv1", "compute_relative_log",
           "decode_relative_log_config", "dv1_definitions", "require_dv1_capability"]
