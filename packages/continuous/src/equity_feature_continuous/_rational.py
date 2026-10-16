"""Exact normalized witnesses, with checks on reduced values rather than temporaries."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from equity_feature_contracts import ContractError, ErrorCode

CAP = 10**38


@dataclass(frozen=True, slots=True)
class Rational:
    numerator: int
    denominator: int

    def __post_init__(self) -> None:
        if type(self) is not Rational or type(self.numerator) is not int or type(self.denominator) is not int:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "exact rational integers required")
        if self.denominator <= 0:
            raise ContractError(ErrorCode.BOUNDS, "positive rational denominator required")
        value = Fraction(self.numerator, self.denominator)
        if abs(value.numerator) >= CAP or value.denominator >= CAP:
            raise ContractError(ErrorCode.OVERFLOW, "reduced rational exceeds declared bounds")
        object.__setattr__(self, "numerator", value.numerator)
        object.__setattr__(self, "denominator", value.denominator)


def validate_rational(value: object) -> None:
    if type(value) is not Rational:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "typed canonical rational required")
    if type(value.numerator) is not int or type(value.denominator) is not int or value.denominator <= 0:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "canonical rational fields required")
    if abs(value.numerator) >= CAP or value.denominator >= CAP:
        raise ContractError(ErrorCode.OVERFLOW, "reduced rational exceeds declared bounds")
    normalized = Fraction(value.numerator, value.denominator)
    if (normalized.numerator, normalized.denominator) != (value.numerator, value.denominator):
        raise ContractError(ErrorCode.INVALID_SCHEMA, "canonical reduced rational required")
