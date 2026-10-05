"""Stable public failure vocabulary; unavailable data uses result statuses."""
from enum import StrEnum

class ErrorCode(StrEnum):
    INVALID_SCHEMA = "invalid_schema"
    INVALID_ORDER = "invalid_order"
    DUPLICATE = "duplicate"
    INVALID_UNIT = "invalid_unit"
    BOUNDS = "bounds"
    OVERFLOW = "overflow"
    INCONSISTENT_IDENTITY = "inconsistent_identity"
    INVALID_CONFIG = "invalid_config"
    INCOMPATIBLE_VERSION = "incompatible_version"
    UNSUPPORTED_SAMPLING = "unsupported_sampling"
    UNSUPPORTED_ADJUSTMENT = "unsupported_adjustment"

class ContractError(ValueError):
    def __init__(self, code: ErrorCode, message: str) -> None:
        self.code = code
        super().__init__(message)
