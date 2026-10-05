# EQ-003 quote semantics decisions

Accepted mathematical baseline for EQ-003, subject to story review/publication. Definition version1; synthetic examples only. See [formula contract](../features/QUOTE_FORMULAS.md) and [execution plan](../stories/EQ-003_PLAN.md).

1. Keep trade-associated samples and continuous updates distinct. Equal-observation summaries describe their own source population; only explicitly complete continuous state updates support duration weighting. Dense trade samples are not proof of a continuous quote stream.
2. Locked quotes are valid with0spread. Crossed quotes are counted separately, with signed optional diagnostics, and excluded from spread means. Null/nonpositive sides are invalid market observations; malformed numeric representations are schema errors. Using abs(ask-bid) would conceal crossed state.
3. Define midpoint-bps at each observation then average. Averaging prices first changes the result and is not this feature. No trade-size weights or quantiles are introduced.
4. Time weighting requires positive explicit max_age and original-age carry. No default age is valid for every source/market. Known invalid/crossed/expired time is excluded and reported; the mean describes valid duration only. Delivery coverage is independent of valid-time fraction.
5. Unknown left boundary blocks a complete time-weighted feature. Known inactive is an explicit supplied fact, not a guess from missing seed. Pre-open seed initializes state without becoming a sample or restarting freshness. A quote at cutoff is outside the half-open target.
6. Last admitted tied update governs subsequent time; earlier tied observations have0duration but remain samples. Replacements/corrections are normalized outside the library; invalid updates break valid carry. Bounded carry is a required implementation contract, not a current implementation claim.

EQ-006 supplies availability/adjustment policy. EQ-011–016 encodes schemas/config/results without changing formulas; EQ-021 implements quote calculations and EQ-023–026 qualifies incremental state/parity. Source adapters must establish complete delivery and normalized states independently. Provider support, actual quote-age policy and legal/source admission remain deployment decisions. Exact signed integer/ratio fixture calculations do not justify unmeasured performance claims.
