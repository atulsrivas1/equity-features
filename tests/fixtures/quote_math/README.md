# Independent quote mathematics fixtures

Synthetic scale0 prices in currency/share; timestamps are UTC-nanosecond offsets from an arbitrary session open. Tiny12ns targets are chosen for transparent arithmetic, not recommended real-market validity defaults. No provider or private data is used.

Hand derivation: q1 bid100/ask102 is normal, spread2, midpoint101, bps20000/101. q2 bid102/ask102 is locked, spread0. q3 bid105/ask104 is crossed with signed spread-1 and signed bps-20000/209, excluded from spread means. q4 has missing bid and is invalid. Counts:4total,2valid including1locked,1crossed,1invalid. Sampled mean price spread=(2+0)/2=1; mean bps=(20000/101+0)/2=10000/101.

Continuous window[0,12), max_age6ns: q1 holds[0,3) for3ns; q2 holds[3,7) for4ns; q3 is crossed[7,9) for2ns; q4 invalid[9,12) for3ns. No quote reaches expiry before its next replacement/cutoff. Valid duration7ns; weighted spread=(2*3+0*4)/7=6/7; weighted bps=(20000/101*3)/7=60000/707; valid fraction7/12. This is a valid-time mean, not a whole-session or trade-size mean.

Run `python tools/verify_quote_examples.py`. The standard-library exact-rational verifier checks these independently written expectations and boundary/quality/precision/partition cases. It is reference evidence for the specification, not production package code, provider admission or numerical-backend qualification. Final floats inherit rtol/atol1e-12; integer counts/durations and retained fractions compare exactly here.
