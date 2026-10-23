"""Pure intraday context and preparation under experimental EQ137 development."""
from ._context import IntradayContext, IntradayRun, build_intraday_config
from ._prepare import IntradayPreparation, OperandEvidence, PreparedOperand, prepare_intraday
from ._dispatch import compute_intraday
from ._registry import (IntradayFeature, describe_intraday, intraday_catalog_digest,
                        require_intraday_capability)

# EF2 money flow (ef2-mf1): own config identity, discovery and dispatch; the R17 catalog is unchanged.
from ._flow_config import (MONEY_FLOW_ALGORITHM, MONEY_FLOW_IDENTITY, MONEY_FLOW_POLICY, MoneyFlowSettings,
                           build_money_flow_config, decode_money_flow_config)
from ._flow import compute_money_flow
from ._flow_registry import describe_money_flow, money_flow_catalog_digest, require_money_flow_capability

__version__ = "0.1.0a3"
__all__ = ["IntradayContext", "IntradayRun", "build_intraday_config",
           "IntradayPreparation", "OperandEvidence", "PreparedOperand", "prepare_intraday",
           "compute_intraday", "IntradayFeature", "describe_intraday",
           "intraday_catalog_digest", "require_intraday_capability",
           "MONEY_FLOW_ALGORITHM", "MONEY_FLOW_IDENTITY", "MONEY_FLOW_POLICY", "MoneyFlowSettings",
           "build_money_flow_config", "decode_money_flow_config", "compute_money_flow",
           "describe_money_flow", "money_flow_catalog_digest", "require_money_flow_capability"]
