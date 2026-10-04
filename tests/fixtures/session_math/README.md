# Exact synthetic session fixtures

No provider credentials or market data. Times are toy integer nanosecond bounds on a synthetic session [0,120); first/last windows [0,60)/[60,120). Scale0 prices are illustrative currency/share. Bar and trade fixtures are separate examples, not the same reconstructed market session.

golden.json was written from the worked arithmetic, not emitted by a production library. Bar volume200+300=500; notional20300+30900=51200. The bar-close proxy=(102*200+103*300)/500=513/5, deliberately distinct from actual bar notional/volume512/5. Session range104-99=5, close location(103-99)/5=4/5. Gap(100-98)/98=1/49, close return5/98. Trade notional100*2+102*3+101*5=1011, volume10, count3, VWAP1011/10 and mean size10/3. Top2 by size is t3 then t2.

Run `python tools/verify_session_examples.py` from the repository. The independent stdlib reference verifier checks all20golden IDs, policy boundary/error cases, missing/empty/coverage behavior, exact ratios, safe integer arithmetic and legal partition reductions. It also checks scope/spec ID coverage. These checks validate the specifications and reference examples; production kernel/API/state/performance validation belongs to the implementation stories.

Case coverage: normal arithmetic; proxy distinction; absent notional; missing prior close; incompatible prior close; missing versus observed-empty; flat range; zero volume; invalid prices/quantities/OHLC; duplicates/order; exact boundaries and auction exception; early close; cutoff/future input; missing intervals; aligned/straddling windows; stable top-K ties; wide products/count overflow; compatible partition conservation. No claim of provider trade-condition normalization or historical availability admission is made.
