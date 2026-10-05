# Synthetic context references

tools/verify_context_examples.py uses exact Fraction arithmetic and hand-derived
assertions: [100,200,300] → 200, 500/200 → 5/2; 10% minus 5% → 5%; partial
four-member universe → 1 advancing, 1 declining, 1 unchanged, coverage 3/4;
one of three eligible closes above SMA → 1/3. Other cases establish exclusion,
early closes, zeros, missingness, alignment and invalid identity boundaries.
No data acquisition, provider fixture, production kernel or benchmark is involved.
