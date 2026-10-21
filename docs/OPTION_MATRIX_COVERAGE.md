# Option matrix coverage accounting

Pinned matrix source commit: `a7cde58fc05166c9818c9107ed52269186d16afa`. Detailed source-derived identities, formulas and command paths remain local under existing rights restrictions. Public rows below report aggregate planning ownership; counts overlap and are not unique formulas. [Plan](OPTION_DELIVERY_REPLAN.md), [machine-readable allocation](plans/option-delivery-replan.json).

The private reconciliation assigns all 2497 frozen finite catalogue identities and 296 command roles. The 26 named option feature declarations are mapped individually, including references/liquidity, activity, flow, IV/surface/history, moves, Greeks, chain, quote coverage and equity/watchlist consumers. Each identity has one primary planning owner; compatible shared producers remain explicitly reusable. Purely equity-owned identities retain their existing stories.

Strategies/profiles, context scores, component weights/gates, watchlists, scanner generations, exposure filters and volatility policies are retained. Configuration variants, state fields and adapters are distinguished from mathematical primitives. Not every strategy is option-only: mixed definitions require existing equity producers under their original ownership. Candidate assignment to a qualification story is not a completed semantic audit or delivered numerical coverage.

| Catalogue namespace | Kind | Records | Library or layer owner | Planning story |
| --- | --- | ---: | --- | --- |
| context_evidence | context_value | 576 | strategy-context | EQ-216 |
| context_normalized | component | 84 | strategy-context | EQ-216 |
| context_profile | context_score | 60 | strategy-context | EQ-216 |
| context_tape_summary | tape_summary | 12 | strategy-context | EQ-216 |
| context_tape_window | window_score | 32 | strategy-context | EQ-216 |
| context_weight | configuration_weight | 280 | strategy-context | EQ-216 |
| equity_confirmation | confirmation_rule | 6 | signal-lifecycle | EQ-178 |
| equity_confirmation | eod_tag | 22 | signal-lifecycle | EQ-178 |
| equity_confirmation | realtime_tag | 32 | signal-lifecycle | EQ-178 |
| equity_digest | method_profile | 10 | strategy-context | EQ-177 |
| equity_eod | scanner | 357 | market-screeners | EQ-176 |
| equity_lineage | membership_seed | 5 | signal-lifecycle | EQ-178 |
| equity_realtime | scanner_family | 43 | market-screeners | EQ-176 |
| equity_watchlist | watchlist | 25 | market-screeners | EQ-176 |
| flow | screen | 11 | market-screeners | EQ-207 |
| heatseeker | entrypoint_contract | 18 | exposure-features | EQ-201 |
| heatseeker | metric_output | 8 | exposure-features | EQ-202 |
| heatseeker | node_filter | 8 | market-screeners | EQ-208 |
| heatseeker | producer_adapter_contract | 1 | exposure-features | EQ-202 |
| heatseeker | resource_kind | 3 | market-screeners | EQ-208 |
| heatseeker | resource_output_family | 5 | market-screeners | EQ-208 |
| high_extension_compact_v2 | dictionary_feature | 21 | strategy-context | EQ-177 |
| intraday_registration | component | 18 | equity-feature-workers | EQ-180 |
| option_p1 | request_kind | 13 | option-feature-workers | EQ-218 |
| option_v1 | feature | 1 | equity-features | EQ-177 |
| option_v1 | feature | 3 | market-microstructure | EQ-189 |
| option_v1 | feature | 1 | market-microstructure | EQ-215 |
| option_v1 | feature | 2 | market-screeners | EQ-207 |
| option_v1 | feature | 2 | option-features | EQ-183 |
| option_v1 | feature | 1 | option-features | EQ-184 |
| option_v1 | feature | 6 | option-features | EQ-214 |
| option_v1 | feature | 2 | option-features | EQ-215 |
| option_v1 | feature | 1 | outcome-labels | EQ-219 |
| option_v1 | feature | 1 | volatility-features | EQ-195 |
| option_v1 | feature | 4 | volatility-features | EQ-196 |
| option_v1 | feature | 2 | volatility-features | EQ-197 |
| option_v1 | scanner | 111 | market-screeners | EQ-207 |
| option_v1 | watchlist | 12 | market-screeners | EQ-207 |
| option_v2 | scanner | 25 | market-screeners | EQ-207 |
| strategy_eod | profile_direction_expiry | 240 | strategy-context | EQ-216 |
| strategy_intraday | strategy | 11 | strategy-context | EQ-216 |
| strategy_intraday_map | component_or_gate | 217 | strategy-context | EQ-216 |
| strategy_meta | manifest | 1 | strategy-context | EQ-216 |
| strategy_meta | meta_score | 5 | strategy-context | EQ-216 |
| tempest | calendar_tenor | 5 | volatility-features | EQ-196 |
| tempest | comparable_history_selector | 30 | volatility-features | EQ-197 |
| tempest | component_admission | 13 | market-screeners | EQ-209 |
| tempest | covered_group_tenor | 3 | volatility-features | EQ-197 |
| tempest | daily_rv_window | 5 | equity-features | EQ-154 |
| tempest | entrypoint_contract | 48 | volatility-features | EQ-194 |
| tempest | history_change_lag | 5 | volatility-features | EQ-197 |
| tempest | intraday_rv_window | 3 | equity-features | EQ-154 |
| tempest | move_target | 5 | volatility-features | EQ-196 |
| tempest | preset_scan | 14 | market-screeners | EQ-209 |
| tempest | pressure_constituent | 3 | market-screeners | EQ-209 |
| tempest | pricing_anomaly | 4 | market-screeners | EQ-209 |
| tempest | producer_adapter_contract | 29 | option-feature-io | EQ-198 |
| tempest | relative_comparison | 15 | volatility-features | EQ-197 |
| tempest | scan_field | 17 | market-screeners | EQ-209 |

## Coverage closure

Before declaring a release ready, reconcile its exact identity manifest to original formulas/contracts, direct producer/consumer edges, units, clocks, revisions, coverage and independent fixtures. Record aliases, shared inputs, supplied facts and non-calculation support explicitly. All16 source product/library crosswalk findings must have dispositions, including equity-owned RV and future-outcome consumers. Retain unresolved dynamic dispatch, typed writes, decoder paths and coarse family unions as qualification work; the finite-catalogue assignment does not settle them.

EQ182 owns foundation reconciliation; EQ188/194/201 own domain qualification; EQ207-209/216 own consumer identities and policy rights; EQ211 audits cumulative complete coverage and numbered residuals. A capability with unresolved rights, semantics or producer binding remains blocked and cannot count as delivered coverage. An explicit deferred disposition explains the remaining gap; it does not satisfy an unqualified promise to cover the entire matrix.
