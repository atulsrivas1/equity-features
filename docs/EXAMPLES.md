# Runnable supplied-input examples

EQ040 adds the independently installed consumer0.3.0 walkthrough for matching corepair0.0.4a4. All data are synthetic supplied facts; calendars, coverage, source revisions and C/K/E are explicit. Core does not acquire data, consult a clock or schedule work. [Public API](api/PUBLIC_API.md), [extension/install commands](api/EXTENSIONS.md), [build delivery](BUILD_DELIVERY.md).

## Standalone installed workflow

Follow the extension guide to install both actual core artifacts and the separately built consumer wheel into a fresh environment. Then run, using that environment's Python, from any directory:

```text
python -I -m equity_feature_demo.walkthrough
```

The packaged [walkthrough](../examples/external_consumer/src/equity_feature_demo/walkthrough.py) imports public installed APIs only. It requires neither the repository fixture directory nor editable core imports. Its independent assertions cover:

- Supplied O100/H103/L99/C102 and O102/H104/L101/C103 produce session O100/H104/L99/C103, volume500 and original notional20300+30900=51200. Builtin range/close is5/103. Absent bars return null/MISSING_INPUT instead of zeros.
- Explicit two-chunk stream produces first prefix close102 at C150 and full final batch parity at C200. Ordinals and per-chunk/prefix/final coverage are supplied; the returned prefix remains102 after later updates. This illustrates supported session streaming, not history/custom incremental execution.
- Governed DAILY closes100/110/121 give one-session return(121-110)/110=1/10 and two-session return(121-100)/100=21/100. Missing history remains null/MISSING_INPUT.
- Composition preserves supplied h2/h1 results in declared order and names the absent instance explicitly. It does not execute or manufacture that dependency.
- Explicit custom registration retains range/open5/100=0.05, distinct from builtin5/103, and the separately packaged synthetic BAR adapter passes public supplied-delivery conformance and exact custom input binding.

Expected stdout names these checks. Assertions fail on incorrect arithmetic, timing/parity, null quality, missing-instance or source binding; a print alone is not qualification. The custom mathematical algorithm remainsv2, builtin mathematicsv1; consumer implementation0.3.0 identifies this newly packaged walkthrough. Core versions/equations/modes are unchanged. Trusted callback/adapter qualification remains bounded; no arbitrary-code purity/resource/source-truth or provider support claim.

Fresh core wheel/sdist qualification executes the actual `-I -m` command, type-checks all installed consumer modules and public caller, checks public imports/site-packages/py.typed, and fingerprints installed core files before/after the complete consumer workflow. Source and actual artifact receipts remain release gates; the development editable smoke run does not establish delivered installation.

## Existing synthetic fixture catalog

The following22 repository scripts remain fixture resources outside both core distributions. Their sibling imports contain synthetic examples; they do not import core from its src checkout. Use the matching public repository revision, a fresh installed matching core pair, and optional pinned NumPy2.2.6/PyArrow20.0.0 for the full catalog. Run `python examples/<name>.py`, with the fresh environment's Python. All22 execute in every wheel/sdist qualification; the helper verifies installed core locations first. The standalone consumer command above works without these resources.

| Script under examples/ | Independent behavior exercised |
| --- | --- |
| [canonical_inputs.py](../examples/canonical_inputs.py) | Exact canonical timestamps/units/nulls, discovery and explicit columnar round trip |
| [in_memory_adapter.py](../examples/in_memory_adapter.py) | Supplied synthetic acquisition protocol and finite delivery |
| [session_bars.py](../examples/session_bars.py) | OHLC/volume/actual notional versus proxy; absent prior returns unavailable |
| [session_structure.py](../examples/session_structure.py) | Whole-bar interval tables and shares; early-close window unavailable |
| [session_trades.py](../examples/session_trades.py) | Count3/volume10/notional1011/VWAP101.1 from supplied trades |
| [session_top_k.py](../examples/session_top_k.py) | Stable ranked original trade evidence and operational bounds |
| [session_quotes.py](../examples/session_quotes.py) | Event-weighted valid quote means/state counts and bounded diagnostics |
| [continuous_quotes.py](../examples/continuous_quotes.py) | Original quote expiry and duration conservation, explicit seed/unknown durations |
| [session_incremental.py](../examples/session_incremental.py) | Contiguous chunks, supplied prefix/final certificates and batch parity |
| [session_state.py](../examples/session_state.py) | Exact compatible owned checkpoint export/restore; no persistence in core |
| [session_merge.py](../examples/session_merge.py) | Caller-certified legal adjacent partition merge |
| [action_policies.py](../examples/action_policies.py) | Supplied causal split/adjustment/classification evidence |
| [history_windows.py](../examples/history_windows.py) | Governed return5/21 and prior extrema122/103; explicit gaps/coverage |
| [history_averages.py](../examples/history_averages.py) | SMA3=365/3, anchored EMA3=975/8 and supplied comparison |
| [history_recursive.py](../examples/history_recursive.py) | Anchored RSI3=4700/57 and ATR3=122/9; required previous close |
| [history_volatility.py](../examples/history_volatility.py) | Centered sample variance476449/44791488 and explicit scaling |
| [daily_volume.py](../examples/daily_volume.py) | Prior volume600/3=200 and separately supplied target ratio5/2 |
| [interval_volume.py](../examples/interval_volume.py) | Historical bucket mean20/ratio5/2; early-close late bucket unavailable |
| [relative_returns.py](../examples/relative_returns.py) | Market spread1/20, sector3/100 and independent missing membership |
| [declared_breadth.py](../examples/declared_breadth.py) | Declared universe counts/coverage3/4 and above-SMA1/3; missing members excluded |
| [feature_composition.py](../examples/feature_composition.py) | Supplied horizon1/10 and21/100 with explicit missing family |
| [legacy_comparison.py](../examples/legacy_comparison.py) | Five captured actual Go observations versus accepted independent EMA/ATR math |

The legacy comparison uses retained licensed/public synthetic observations, not private source execution or fetched data. Other example assertions and accepted mathematical references remain linked to their owning stories. Examples demonstrate supported contracts, not production source completeness, rights, strategy performance or hidden acceleration. EQ095 adds independent combined external negatives; EQ048 owns whole R3 acceptance.
