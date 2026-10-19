"""Pure intraday context and preparation under experimental EQ137 development."""
from ._context import IntradayContext, IntradayRun, build_intraday_config
from ._prepare import IntradayPreparation, OperandEvidence, PreparedOperand, prepare_intraday
from ._dispatch import compute_intraday
from ._registry import (IntradayFeature, describe_intraday, intraday_catalog_digest,
                        require_intraday_capability)

__version__ = "0.1.0a2"
__all__ = ["IntradayContext", "IntradayRun", "build_intraday_config",
           "IntradayPreparation", "OperandEvidence", "PreparedOperand", "prepare_intraday",
           "compute_intraday", "IntradayFeature", "describe_intraday",
           "intraday_catalog_digest", "require_intraday_capability"]
