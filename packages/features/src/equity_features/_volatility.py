"""Exact finite centered sample variance, then high-precision square root."""
from decimal import Decimal, localcontext
from fractions import Fraction


def volatility(closes: list[int], factor: int) -> float:
    returns = [Fraction(b, a)-1 for a, b in zip(closes, closes[1:])]
    mean = sum(returns, Fraction())/len(returns)
    variance = sum(((r-mean)**2 for r in returns), Fraction())/(len(returns)-1)
    scaled = variance*factor
    with localcontext() as context:
        context.prec = 80
        return float((Decimal(scaled.numerator)/Decimal(scaled.denominator)).sqrt())
