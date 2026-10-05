# EQ-004 historical semantics

Definition baseline1, subject to story review/publication. See [formulas](../features/HISTORICAL_FORMULAS.md) and [plan](../stories/EQ-004_PLAN.md).

1. Use explicit governed session slots. Missing trading-session observations remain gaps; calendar-day arithmetic and compressed row windows would change horizon and coverage.
2. Completed target is included for current indicators and returns; prior extrema exclude it. A required session must be completed/eligible at the supplied cutoff. Corporate-action/reference admission is bounded to EQ-006.
3. EMAuses firstNcloseSMAseed with alpha2/(N+1); RSI/ATRuse Wilder1/Nrecurrences with explicit anchors and enough actual changes/TRs. ATRnever invents an initial previous close. Anchor identity is part of reproducibility.
4. Flat initialized RSIis50by explicit neutral convention; nonneutralRSIon a long unchanged continuation preserves ratio in exact mathematics. No missing value is replaced by50. ATR0for genuine flat/no-gap price is valid.
5. Strict gaps invalidate recursive continuity; finite windows may recover after a gap leaves their dependencies. New caller-declared epochs are explicit new initialization, never silent skipping or restart.
6. Volatility uses centered sample variance of simple consecutive returns, N>=2 and explicit scaling. DefaultA1is unannualized; alternative logarithmic/population/RMS conventions are not silently accepted. These choices are package definitions, not trading advice or universal market defaults.
7. Exact synthetic expectations and cutoff/gap/precision tests precede production API/backend/state work. No benchmark/third-party parity or provider admission is implied by recurrence references. Other products remain outside this library's scope; hosted automated review remains owner-deferred.
