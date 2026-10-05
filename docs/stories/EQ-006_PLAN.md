# EQ-006 execution plan

Story #7, E01/R0; confirmed **8 points**. Prerequisites EQ-001–005 delivered,
including PR128 on main b3a39a4209580e95ebe7f953d63b81f839901dfe with 100
passing reference cases, final-head CI and exact GitHub blob verification.
Problem: mathematically computable history may still contain unavailable facts.
First action: reconcile cutoff language across all four formula specifications.

Acceptance mapping: event/market/reference cutoffs and EOD/intraday → timing policy;
known-at/reconstruction → separate admission modes; split/dividend → explicit basis
and action evidence; gaps → strict existing readiness and replay rules; tested
evidence → timing design references/CI and decision note. No adjustment engine,
source admission or production data verification is included.

Design: half-open ordinary events, completed intervals at end<=market cutoff;
knowledge admission includes known_at==reference cutoff. Unknown known_at cannot
enter causal mode. Reconstruction remains explicitly retrospective, never a causal
claim. Accept supplied raw/split/total-return bases with immutable identity and
effective/known-at action evidence; conversions are caller responsibility.
Resolve routine policy details in writing; no provider-specific default.

Tests: cutoff equality and auction exception; future/unknown reference knowledge;
revised source facts; 2:1 split price/quantity/notional invariance; dividend price
return versus declared reinvestment basis; mixed basis/action versions; unavailable
action and history gaps. Preserve all 100 existing cases and planning checks.
Docs: timing/adjustment policy, decision, fixtures guide, formula links, continuity,
GitHub issue/epic evidence and PR. Author self-review, exact final-head CI, main blob
verification and post-delivery checks precede Released/Done. Next EQ-007 can be Ready.
Decision time bounds both market and reference cutoffs; delayed EOD knowledge is
valid only for an evaluation at or after that known-at time.
