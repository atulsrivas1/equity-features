"""Own fixed descriptive batch capabilities, separate from the core registry."""
from __future__ import annotations
from dataclasses import dataclass
from equity_feature_contracts import ContractError, ErrorCode

_SPECS = (
    ('cross_venue.basis', 'basis', 'reference_currency_per_reference_quantity'),
    ('cross_venue.premium', 'basis', 'ratio'),
    ('cross_venue.freeze_max_abs', 'freeze', 'reference_currency_per_reference_quantity'),
    ('cross_venue.freeze_mean_abs', 'freeze', 'reference_currency_per_reference_quantity'),
    ('cross_venue.reopen_gap', 'reopen', 'reference_currency_per_reference_quantity'),
    ('cross_venue.reopen_premium', 'reopen', 'ratio'),
)


@dataclass(frozen=True, slots=True)
class ContinuousFeature:
    id: str
    operation: str
    algorithm_version: str
    unit: str
    batch: bool
    update: bool
    merge: bool
    restore: bool

    def __post_init__(self) -> None:
        if type(self) is not ContinuousFeature or any(type(value) is not str for value in
                (self.id, self.operation, self.algorithm_version, self.unit)) or any(
                type(value) is not bool for value in (self.batch, self.update, self.merge, self.restore)):
            raise ContractError(ErrorCode.INVALID_SCHEMA, 'exact descriptive continuous feature fields required')
        if (self.id, self.operation, self.unit) not in _SPECS or self.algorithm_version != '1' or (
                self.batch, self.update, self.merge, self.restore) != (True, False, False, False):
            raise ContractError(ErrorCode.UNSUPPORTED_CAPABILITY, 'unsupported continuous feature declaration')


_FEATURES = tuple(ContinuousFeature(identity, operation, '1', unit, True, False, False, False)
                  for identity, operation, unit in _SPECS)


def list_features() -> tuple[ContinuousFeature, ...]:
    """Return immutable own metadata; no old Registry/CanonicalBatch claim."""
    return _FEATURES


def require_capability(feature_id: str, mode: str) -> None:
    if type(feature_id) is not str or type(mode) is not str:
        raise ContractError(ErrorCode.INVALID_SCHEMA, 'exact feature ID and capability strings required')
    if mode != 'batch' or feature_id not in tuple(item.id for item in _FEATURES):
        raise ContractError(ErrorCode.UNSUPPORTED_CAPABILITY, 'continuous feature capability is unsupported')
