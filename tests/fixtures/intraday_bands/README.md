# Original price-band mathematical goldens

Thirteen synthetic original cases cover exact lower/position zero, zero variance, negative/unclamped values, near cancellation, wide integer offsets, scale18/int64 limits and bounded multiplier extremes. Values are supplied scaled integers, with exact reduced rational multiplier. No provider or comparison-derived data is used.

GOLDENS.json stores exact mean/population variance/squared radius and five expected Float64 cells (middle, upper, lower, width, position); null position is the zero-variance rule. Exact rational-square cases retain exact expected fractions. The standalone generator uses exact pairwise population variance and rational-square arithmetic, otherwise independent direct Decimal240 expressions. It imports no production module and does not use the production rationalized lower/position formula.

The generator_sha256_lf field hashes the generator with CRLF normalized to LF; it identifies this mathematical generator, not an environment/artifact signature. Generate with CPython3.12 by running generate_original.py. The producer tests independently compare centered Fraction/Decimal300 oracles and these fixed values, including exact zero/sign checks. Fixture equality is not performance, installed or release acceptance.
