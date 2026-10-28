"""Pure intraday context and preparation under experimental EQ137 development."""
from ._context import IntradayContext, IntradayRun, build_intraday_config
from ._prepare import IntradayPreparation, OperandEvidence, PreparedOperand, prepare_intraday
from ._dispatch import compute_intraday
from ._registry import (PACKAGE_VERSION, IntradayFeature, describe_intraday, intraday_catalog_digest,
                        require_intraday_capability)

# EF2 money flow (ef2-mf1): own config identity, discovery and dispatch; the R17 catalog is unchanged.
from ._flow_config import (MONEY_FLOW_ALGORITHM, MONEY_FLOW_IDENTITY, MONEY_FLOW_POLICY, MoneyFlowSettings,
                           build_money_flow_config, decode_money_flow_config)
from ._flow import compute_money_flow
from ._flow_registry import describe_money_flow, money_flow_catalog_digest, require_money_flow_capability

# EF2 momentum and trend (ef2-conv1): own config identity, discovery and dispatch; the R17 catalog is unchanged.
from ._momentum_config import (MOMENTUM_ALGORITHM, MOMENTUM_CONVENTIONS, MOMENTUM_IDENTITY, MomentumSettings,
                               build_momentum_config, decode_momentum_config)
from ._momentum import compute_momentum
from ._momentum_registry import describe_momentum, momentum_catalog_digest, require_momentum_capability

# EF2 Ichimoku and price channels (ef2-v1): own config identities, discovery and dispatch; the R17 catalog is unchanged.
from ._channels_config import (CHANNELS_ALGORITHM, CHANNELS_CONTRACT_VERSION, CHANNELS_CONVENTIONS,
                               CHANNELS_IDENTITIES, ChannelsSettings, build_channels_config,
                               decode_channels_config)
from ._channels import compute_channels
from ._channels_registry import (CHANNELS_PRODUCER_FEATURES, channels_catalog_digest, describe_channels,
                                 require_channels_capability)

# EF3 realized variance (ef3-rv1): own config identity, discovery and dispatch; the R17 catalog is unchanged.
from ._rv_config import (REALIZED_VARIANCE_ALGORITHM, REALIZED_VARIANCE_IDENTITY, REALIZED_VARIANCE_POLICY,
                         REALIZED_VARIANCE_SAMPLING, RealizedVarianceSettings, build_realized_variance_config,
                         decode_realized_variance_config)
from ._rv import compute_realized_variance
from ._rv_registry import (describe_realized_variance, realized_variance_catalog_digest,
                           require_realized_variance_capability)

# EF4 path efficiency and choppiness (ef4-path1): own config identity, discovery and dispatch; the R17 catalog is unchanged.
from ._path_config import (PATH_EFFICIENCY_ALGORITHM, PATH_EFFICIENCY_IDENTITY, PATH_EFFICIENCY_POLICY,
                           PATH_EFFICIENCY_PROFILES, PathEfficiencySettings, build_path_efficiency_config,
                           decode_path_efficiency_config)
from ._path import compute_path_efficiency
from ._path_registry import (describe_path_efficiency, path_efficiency_catalog_digest,
                             require_path_efficiency_capability)

from ._ef5 import compute_ef5
from ._ef5_config import ADJUSTMENT_LABELS, EF5_PROFILES, PRODUCERS as EF5_PRODUCERS, Ef5Settings, build_ef5_config, decode_ef5_config
from ._ef5_registry import describe_ef5, ef5_catalog_digest, require_ef5_capability

__version__ = PACKAGE_VERSION
__all__ = ["IntradayContext", "IntradayRun", "build_intraday_config",
           "IntradayPreparation", "OperandEvidence", "PreparedOperand", "prepare_intraday",
           "compute_intraday", "IntradayFeature", "describe_intraday",
           "intraday_catalog_digest", "require_intraday_capability",
           "MONEY_FLOW_ALGORITHM", "MONEY_FLOW_IDENTITY", "MONEY_FLOW_POLICY", "MoneyFlowSettings",
           "build_money_flow_config", "decode_money_flow_config", "compute_money_flow",
           "describe_money_flow", "money_flow_catalog_digest", "require_money_flow_capability",
           "MOMENTUM_ALGORITHM", "MOMENTUM_CONVENTIONS", "MOMENTUM_IDENTITY", "MomentumSettings",
           "build_momentum_config", "decode_momentum_config", "compute_momentum",
           "describe_momentum", "momentum_catalog_digest", "require_momentum_capability",
           "CHANNELS_ALGORITHM", "CHANNELS_CONTRACT_VERSION", "CHANNELS_CONVENTIONS", "CHANNELS_IDENTITIES",
           "CHANNELS_PRODUCER_FEATURES", "ChannelsSettings", "build_channels_config",
           "decode_channels_config", "compute_channels", "describe_channels", "channels_catalog_digest",
           "require_channels_capability",
           "REALIZED_VARIANCE_ALGORITHM", "REALIZED_VARIANCE_IDENTITY", "REALIZED_VARIANCE_POLICY",
           "REALIZED_VARIANCE_SAMPLING", "RealizedVarianceSettings", "build_realized_variance_config",
           "decode_realized_variance_config", "compute_realized_variance", "describe_realized_variance",
           "realized_variance_catalog_digest", "require_realized_variance_capability",
           "PATH_EFFICIENCY_ALGORITHM", "PATH_EFFICIENCY_IDENTITY", "PATH_EFFICIENCY_POLICY",
           "PATH_EFFICIENCY_PROFILES", "PathEfficiencySettings", "build_path_efficiency_config",
           "decode_path_efficiency_config", "compute_path_efficiency", "describe_path_efficiency",
           "path_efficiency_catalog_digest", "require_path_efficiency_capability",
           "ADJUSTMENT_LABELS", "EF5_PROFILES", "EF5_PRODUCERS", "Ef5Settings", "build_ef5_config", "compute_ef5",
           "decode_ef5_config", "describe_ef5", "ef5_catalog_digest", "require_ef5_capability"]
