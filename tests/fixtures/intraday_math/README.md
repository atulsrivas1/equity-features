# Original intraday mathematics references

EQ136 synthetic goldens qualify the [original formulas](../../../docs/features/INTRADAY_FOUNDATIONS.md) and [API contract](../../../docs/api/INTRADAY.md). Run `python tools/verify_intraday_examples.py`. No production package is imported. Expanded smoothing weights provide an exact independent reference for later iterative kernels; population variance uses exact centered fractions and square roots use Decimal precision120.

For closes10,12,11,14,13 and N3: EMA seed11, then25/2,51/4. Gains5/3 and losses1/3 seed RSI250/3; after loss1 they become10/9 and5/9, giving200/3. TRs3,3,4,3 seed ATR10/3, then29/9. Final band mean38/3 and variance14/9 give bounds(38±2sqrt14)/3, width2sqrt14/19 and position(1+2sqrt14)/(4sqrt14).

For the carry case10,11,12,20,21 with N2: EMA seed21/2 then23/2,103/6,355/18. TRs2,2,9,2 give ATR seed2 then11/2,15/4. Reset at index3 yields EMA41/2 and insufficient RSI/ATR history; previous epoch changes cannot enter. Flat/rising/falling cases independently fix the RSI50/100/0 conventions.

Large-offset prices2^60-1,2^60,2^60+1 have variance2/3 despite equal rounded Float64 band bounds. Ratios require pre-rounding operands. Int64-price squared sums can exceed decimal128 even when variance is small. The fixtures also cover zero/negative band lower, unclamped position, relative error on tiny ratios, target-close independence for ATR, known-at equality and exact slot cutoff equality.

These are specification references, not production admission/codec/worker/installed acceptance or performance evidence. The declarative operand and timing cases bind expected mathematics; subsequent kernels must be compared to these independently, including complete quality/evidence/identity behavior under their own tests. The full transport/status contract is reviewed separately; this arithmetic verifier does not pretend to implement it.
