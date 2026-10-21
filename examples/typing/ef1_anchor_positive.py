"""PEP561 caller for the additive supplied-anchor API; no runtime calculation."""
from collections.abc import Mapping
from typing import Any

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, CanonicalBatch, ConfigSpec, EntityKey,
    FeatureResult, PriceUnit, SessionSpec, WindowSpec,
)
from equity_features.ef1 import (
    EF1Definition, build_ef1_config, compute_ef1, decode_ef1_context, ef1_definitions,
)


def configure(context: dict[str, Any], session: SessionSpec, window: WindowSpec,
              availability: AvailabilitySpec, unit: PriceUnit) -> ConfigSpec:
    return build_ef1_config(context, session=session, window=window,
                            availability=availability, price_unit=unit,
                            adjustment=AdjustmentSpec())


def describe(config: ConfigSpec) -> tuple[EF1Definition, ...]:
    context: Mapping[str, Any] = decode_ef1_context(config)
    assert context["producer"] == "anchor"
    return ef1_definitions(config)


def calculate(present_batches: tuple[CanonicalBatch, ...], config: ConfigSpec,
              entity: EntityKey) -> FeatureResult:
    return compute_ef1(present_batches, config, entity=entity)
