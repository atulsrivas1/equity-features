Source: work/po-parity-reconciliation-2026-10-29.md (Product Owner ruling record, 2026-10-29). Verbatim copy follows the blank line; internal, synthetic, pre-release.

# PO reconciliation of the equity parity check, 2026-10-29

Role: Product Owner, Equity Features (internal, synthetic, pre-release). Input: `work/PARITY_CHECK_EQUITY_2026-10-29.md`.

## 0. What I verified myself (read-only) and what I did not

Verified against `watchyourlist-design/docs/features` and `origin/main` of core (`e828273`):
- P40/P41 design text: "daily log returns on adjusted closes" (price-technicals.md:133, 143). Shipped `ef3/_relative.py:3,27`: simple session returns. Confirmed.
- V12a design text: "a simple 20-day mean of true range, not Wilder", default 4.8, 12% fallback (volume-radar.md:31). Shipped `history.atr`: Wilder (`HISTORICAL_FORMULAS.md:25`, per check). Confirmed on the design side; shipped side taken from the check.
- P15 design: range at least X% of the OPEN (price-technicals.md:49). Shipped `session.price.range_fraction` = (H-L)/CLOSE (`V1_SCOPE.md:51`, "relative to close"). Confirmed. New finding: `docs/api/CUSTOM_FEATURES.md:17` already shows `custom demo:range_over_open/v2` = (H-L)/O computed from built-in OHLC. So the open-based form is demonstrated as a custom feature, not built in.
- M11 design: population standard deviation (market-context.md:32). Shipped `ef4/_relative_excess.py:32,37` says in a comment "dispersion by the range". Confirmed.
- The library's own convention is "another convention is another label" (`_relative_excess.py:32`, `_relative.py:27`). Variants with distinct ids/versions are the native way to fix these.

Not verified by me (carried over from the check, still open): no gate was run; `(c)` compositions are not numerically checked; `history.prior_high/low` periods other than 20/60/252; look-ahead safety of `session.structure.interval_ohlcv` for opening ranges. I read the design side only for the four conflicts, not all 166 rows.

## 1. Classification adjustments

| Item | Check says | I rule | Evidence / reason |
|---|---|---|---|
| P15 | DIFFERS | DIFFERS for built-in; PARTIAL via custom feature | Open-based range exists only as `CUSTOM_FEATURES.md:17` example. Not a shipped built-in id. |
| P40-P42 | DIFFERS | DIFFERS, confirmed | Simple vs log. Also: design says workers return 0 when samples are too few; design text itself says a stored 0 is never shown as zero. Library "unavailable" is the correct behaviour; design wording is the thing to correct. |
| V12a | DIFFERS | DIFFERS, confirmed | Design explicitly excludes Wilder; the 4.8 threshold was calibrated on the simple mean. |
| M11 | DIFFERS | DIFFERS, confirmed; also naming hazard | Output is called "dispersion" but is a range. |
| P25, P36, P37, V12b | MATCH(c) | AT RISK, hold as MATCH(c) only with a consumer rule | `history.prior_high/low` windows exclude the target session; check notes the design (P36, :122) includes the current session. A consumer must take max(prior_high, current high). This is a fifth, milder silent conflict (window inclusion). Needs a Tester check of P25/V12b design wording before I count them. |
| P13 | PARTIAL | agree | Donchian 60 slots is intraday-grid, reset-epoch, not a rolling hour by contract. |
| P6/P14/P17 | MATCH(c) | agree, conditional | Look-ahead safety of `interval_ohlcv` unverified; hold as provisional until a gate confirms. |

No classification moves to MATCH. Net effect on the headline: 41 MATCH stands as an upper bound; 37 to 41 once the four at-risk window items are checked. DIFFERS becomes 6 confirmed, plus up to 4 window-inclusion items.

## 2. Rulings on the four silent definition conflicts (correctness priority)

Rule applied: never change a shipped id's meaning silently; add a labelled variant, make the design's variant explicit, and make the library refuse to let the two be confused.

| # | Conflict | Ruling | Detail |
|---|---|---|---|
| 1 | Beta/correlation: simple vs log returns | FIX LIBRARY (add variant) + CHANGE DESIGN (wording) | Add `relative.beta` / `relative.correlation` log-return variants (new version label, e.g. convention "daily log returns, adjusted close"). Keep the simple-return ones as documented variants. The WatchYourList product binds to the log variant, because the design states the return type on every displayed value. Change design wording: "returns 0 when too few samples" becomes "unavailable with sample count"; library behaviour is already right. |
| 2 | ATR: Wilder vs simple 20-day mean | DOCUMENT AS VARIANT + FIX LIBRARY (add) | Do not touch Wilder `history.atr` (it is correct as an ATR, and P21/W3 want it). Add `history.atr_simple_mean` (simple mean of true range over N, with a documented missing-data rule). V12a binds to it. Design keeps "not Wilder" and the 12% fallback is a consumer rule. Both ids appear in discovery with distinct names so nobody swaps them. |
| 3 | Session range over close vs over open | FIX LIBRARY (promote custom to built-in) | Add built-in `session.price.range_over_open` (H-L)/O, using the already-demonstrated formula from `CUSTOM_FEATURES.md`. Keep `range_fraction` (over close) unchanged and documented. P15 binds to the new id. |
| 4 | Dispersion: range vs population stdev | FIX LIBRARY (add) + RENAME existing | Add `core.benchmark_return_stdev_fraction` (population stdev over the 3 core funds, n fixed by the set). Because the repo is pre-release and the current name is misleading, rename the existing range output to `core.benchmark_return_range_fraction`; no compatibility alias unless a consumer exists (none known). M11 binds to the stdev one. |

Acceptance for the ruling set: each new id has an independent recompute test, a "wrong convention fails" fixture (feed data where simple and log, Wilder and simple, range and stdev differ, assert the id returns the design's value), and a discovery description naming the convention.

## 3. Release plan: ordered stories

Ordering logic: correctness first, then the largest unblocked value that stays inside the library, then integration on real data (owner-gated), then data-feed families (owner decisions). All library stories are server-side calculations on stored data unless stated. Data assumption per project rule: Databento + FMP + public sources.

| Story | Title | Value | Data-capability matrix (data / where / sources) | Depends on | Owner-only items |
|---|---|---|---|---|---|
| EF6 | Definition-conflict fixes (4 rulings above) and window-inclusion check for P25/P36/P37/V12b | Removes wrong-number risk; every later story sits on it | Data: existing daily adjusted closes, OHLC, three core ETF closes. Server. Databento: daily or aggregated 1m, full. FMP: EOD prices and adjustment factors, full. Public: none needed. | none | none |
| EF7 | Daily-grid technicals: MACD, DMI/ADX, stochastic, Williams, Bollinger, Donchian, Keltner, pivots, OBV/CMF, ROC, daily squeeze | Largest block of presets (357 EOD presets, gap 1); P4, P12, S3, S4, S6 | Data: adjusted daily OHLCV, 250+ sessions, split basis. Server for universe scans; client only for a small list. Databento: `ohlcv-1d` or aggregation, full. FMP: EOD plus adjustment, full. Public: exchange EOD files for cross-check only. | EF6 (ATR variant naming) | Real daily data rights |
| EF8 | Dollar-volume and trade-count baselines (extend robust/mean field sets; Amihud) | Gates the liquidity floor U12, V8, V12c, V15, V16, U8, V9, V20 | Data: per-session notional and trade count, daily and per-minute-of-day, 30-60 sessions. Server. Databento: trades/ohlcv give count, volume, notional, full. FMP: daily volume only, no trade count (dollar volume derivable, trade count not). Public: none. | EF6 | Choose which source supplies trade count (Databento rights) |
| EF9 | Level carriers and event semantics: premarket high/low, YTD high/low, gap held/reversal, one shared crossing spec (break, fail, reclaim, rejection, new high) | Entry conditions need a defined moment; stops every consumer inventing its own crossing rule | Data: premarket/postmarket bars, daily for YTD, 1s/1m for event moment. Server for scans; client for live crossing on a watched name. Databento: extended hours in ohlcv, full if subscribed. FMP: premarket quotes limited. Public: none. | EF6 | Extended-hours data rights; whether premarket is in the stored set (design says it may not be) |
| EF10 | Intraday-shape measures: share of session above VWAP, share of minutes beating SPY, direction-change count, prior-session value area/POC | P16, P18, P19, P23: four requested measures with no code | Data: full-session 1m bars or trades, aligned SPY/QQQ 1m, prior-session trades. Server (heavy over a universe). Databento: full. FMP: none. Public: none. | EF6, EF8 for cost model | Databento tier and compute cost for universe-wide runs |
| EF11 | Market-context extensions: RSI-threshold breadth (M19), options-expiration week (M15), holiday adjacency (M16), median pairwise correlation (P43) | Completes Market context and list coherence | Data: RSI per member (EF7 daily), exchange calendar, member daily returns. Server. Databento: full for bars. FMP: calendar partial. Public: exchange calendars, free. | EF7, EF6 (log correlation) | none |
| EF12 | Real-data enablement: first real worker run for a daily condition set, service/MCP exposure of ef2-ef5 families, real-source parity vs design, scheduled run | Turns "computable from supplied data" into "available in the product" (gap 10); today the only real read is one symbol and one day | Data: stored 1m/1d bars for a universe, calendar, completeness proof, known-at. Server. Databento: full if rights held. FMP: full. Public: n/a. | EF6 first; runs in parallel with EF7 once started | Dataset rights, Linux qualification, real-source parity sign-off, release sign-off (all already owner-only) |
| EF13 | Data-feed families as adapters, not library maths: events and corporate actions (earnings, dividends, splits, filings, ratings, insiders, 13F, macro), short interest and short-sale volume, auctions, off-exchange share, index series (VIX, MOVE, TNX) | 28 plus 14 items; Company events is a primary surface | Data: per family. Server, scheduled ingest. Databento: corporate-actions/security master only if licensed; imbalance partial; TRF share licence-dependent; no earnings or filings. FMP: earnings, dividends, splits, ratings, insider, 13F full on supported tier; short interest tier-dependent; index quotes on supported plans. Public: EDGAR (filings, Form 4, 13D/G, 13F), FINRA short interest and short-sale volume, Fed/BLS/BEA calendars, Cboe/Fed series: free, delayed, rate limited. | EF12 (needs a real-source path) | Which provider tier to buy (cost), licence for redistribution, whether to build FINRA/EDGAR ingest. Not started until the owner decides. |
| EF14 | Pattern catalogue version (80 candlesticks, 15 chart structures) | Visible preset family; EF5 stops at primitives by decision | Data: adjusted daily OHLCV, swing structure. Server. Databento and FMP full. | EF7, EF9 | Owner decision to reverse the EF5 "no named formations" boundary |

Acceptance rule for every story: real independent review, independent docs review, retro, per the standing agreement; each new id carries a discovery description and a wrong-convention fixture.

### What stays out of library scope
- Thresholds, crossings, rule groups, confluence counts, watchlist matching (W1-W3), meta-watchlist (W4), list lifecycle, candidate episodes (L1), strategy objects, sequential combine, backtests (T1-T3), alerts (T6), person-owned levels (P27-P29), price filter (U1).
- Scores and client-visible rank. `equity_feature_strategies` exact ranking must not be surfaced (design forbids it); it stays internal.
- MFE/MAE per-candidate outcomes (design bans them, WL125).
- Halt and SSR live status: the library computes only over supplied events; no live feed is planned in the library.

## 4. Honest coverage statement

- 41 of 166 design items are MATCH, which is 25%. Of those 41, 17 need consumer arithmetic and 24 are direct. Four more (P25, P36, P37, V12b) are at risk until the window check, so the real figure is 37 to 41.
- Of the 89 conditions that are real library calculations, 38 match (43%), 32 are partial, 6 differ (13 are true calculation gaps counted separately in the check).
- 59 MISSING of which 46 are data-feed items that no amount of library maths fixes.
- Real-data coverage is minimal: every MATCH means "library calculation on synthetic data with io and worker plumbing". The only real-source read is the EF1 regular-bar-prices slice for one symbol and one day, with synthetic calendar/proof/known-at, and about a third of stored rows refused for sub-second timestamps. No equity condition is available in the product today.
- Nothing in this reconciliation was executed; the numbers are from reading code, registries and docs.

## 5. What to tell the owner

1. Parity is about one quarter on paper and close to zero on real data. Say that plainly; do not market it as release-ready.
2. Four values would have been silently wrong (beta/correlation, ATR, session range, dispersion). I have ruled each as a labelled fix in EF6 and will not count them as covered until the wrong-convention fixtures pass. A fifth, milder issue (prior-only high/low windows) is under check.
3. Decisions needed from the owner only: (a) real-data rights and the Databento tier, including trade-count and extended-hours data; (b) which FMP tier and whether to build EDGAR/FINRA ingest for the events and short-interest families (cost, licence); (c) whether to reverse the EF5 boundary on named patterns; (d) Linux qualification and real-source parity sign-off, already open.
4. Everything else in the plan (EF6 to EF11) I will run without further input. EF12 starts as soon as rights are confirmed; EF13 and EF14 wait for owner decisions.
