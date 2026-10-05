# Independently derived historical expectations

Synthetic daily closes100,110,105,120,115,130; period3. Prices are scale0 currency/share; end timestamps are illustrative UTC-nanosecond offsets. Sessions0–5 are a supplied consecutive governed grid, not calendar days. No provider or private data is used.

Return3 at session5=130/105-1=5/21. SMA3=(120+115+130)/3=365/3. EMA3 seed at2=(100+110+105)/3=105; alpha1/2 gives112.5,113.75,121.875=975/8.

RSI3 first gains10,0,15 and losses0,5,0 seedG25/3,L5/3 at3. At4:G50/9,L25/9; at5:G235/27,L50/27.100G/(G+L)=4700/57. Flat initialized history uses the explicit neutral50 convention; upward-only100 and downward-only0. ATR3 uses previous closes: TR sessions1–5 are13,8,18,8,18. Seed(13+8+18)/3=13; updates34/3 then122/9. Prior3high=max111,122,121=122; prior3low=min103,104,113=103; target5 excluded.

Last3simple returns are1/7,-1/24,3/23; mean895/11592. Deviations are761/11592,-1378/11592,617/11592. Sample variance=(761²+1378²+617²)/(2*11592²)=476449/44791488. Unannualized volatility is its square root. Golden variance is exact; the golden square-root decimal is independently evaluated with Python math.sqrt (double precision). The verifier uses Decimal.sqrt at60digits and compares that decimal within1e-12, without pretending the double fixture has60digits of precision.

Run `python tools/verify_history_examples.py`. Exact-rational references check equations, independent golden expectations and governed gaps/warm-up/causality/precision/partition cases. This is a documentation reference, not production package code, provider admission or backend qualification. Integers/retained fractions compare exactly; floating outputs use the contract's declared tolerance.
