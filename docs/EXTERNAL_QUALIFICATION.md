# Installed external consumer qualification

EQ095 qualifies separately packaged equity-feature-demo0.4.0 through public APIs; corepair0.0.4a4, all39 built-ins, math versions, schema1/state2 and execution modes are unchanged. Custom demo:range_over_open retains algorithmv2; the new qualification command changes only consumer implementation identity.

Two supplied bars have session open100, high104, low99, close103, volume500 and actual notional51200. Independent rational goldens are range/open=5/100=0.05 fraction and built-in range/close=5/103. EntityA/S, session100..200, availability C/K/E=200/210/210, complete2/2 coverage, USDscale0 and actual source/config/implementation bindings are checked. Complete output has no extra evidence rows; metadata and typed quality remain explicit. A supported eligibility policy/config digest change preserves equation/v2; changed feature meaning uses a distinct ID/version, as the custom and built-in goldens demonstrate.

Nonpositive OHLC is rejected by canonical admission before callback execution. Initial probe incorrectly expected a zero-denominator output; corrected to actual invalid_schema. A valid zero-volume interval must have null OHLC/zero notional and does not replace the next price-bearing open. The unavailable fixture instead supplies unknown known_at for both rows and propagates missing_input/unknown_availability without fabrication. The defensive zero-denominator branch is not an accepted valid-input fixture.

Run `python -I -m equity_feature_demo.qualification` after installing the retained consumer artifact alongside matching corewheel/sdist, as described in [installation](INSTALLING.md). Builder executes installed consumer imports, walkthrough and qualification; the qualification subprocess uses isolated Python and a fresh environment cwd. PEP561 checks discover the installed package by name from a separate cwd. Core module and distribution metadata fingerprints are equal before installation, after installation and after all consumer execution, excluding bytecache. The report records actual producer version, hand goldens, before/after built-in catalog digests and typed actual outcomes. A deliberately wrong but contract-valid0.06 callback is rejected by the independent golden check.

`external-qualification1` is nested in each `consumer-install1` report alongside exact source, system, actual installed archive name/SHA and core fingerprints. Its43 cases comprise13 positive,23 contract errors and7 source errors. The adapter's10 finite conformance cases include actual whole/chunk/missing deliveries and seven captured acquisition errors. These reports are evidence of these synthetic cases, not a universal extension certification.

| Case | Group | Expected actual outcome |
| --- | --- | --- |
| custom_hand_golden | positive | pass |
| distinct_builtin_hand_golden | positive | pass |
| discovery_and_registry_isolation | positive | pass |
| typed_identity_unit_quality | positive | pass |
| config_input_implementation_binding | positive | pass |
| explicit_empty_complete_evidence | positive | pass |
| supported_config_identity_change | positive | pass |
| nonpositive_bar_input | contract_error | invalid_schema |
| unavailable_input_quality | positive | pass |
| duplicate_registration | contract_error | duplicate |
| namespace_mismatch | contract_error | inconsistent_identity |
| reserved_builtin_collision | contract_error | duplicate |
| missing_role | contract_error | invalid_schema |
| incompatible_algorithm | contract_error | incompatible_version |
| incompatible_config_identity | contract_error | incompatible_version |
| invalid_parameter_type | contract_error | invalid_config |
| unsupported_definition_mode | contract_error | unsupported_capability |
| unsupported_input_schema | contract_error | unsupported_capability |
| unsupported_update | contract_error | unsupported_capability |
| unsupported_restore | contract_error | unsupported_capability |
| unsupported_merge | contract_error | unsupported_capability |
| unknown_mode | contract_error | invalid_config |
| unknown_feature | contract_error | unknown_feature |
| bad_output_unit | contract_error | invalid_schema |
| bad_output_type | contract_error | invalid_schema |
| bad_output_algorithm | contract_error | inconsistent_identity |
| incompatible_callback_implementation | contract_error | inconsistent_identity |
| bad_result_config_binding | contract_error | inconsistent_identity |
| bad_result_input_binding | contract_error | inconsistent_identity |
| bad_result_schema | contract_error | invalid_schema |
| bad_result_entity | contract_error | inconsistent_identity |
| adapter_custom_binding_and_golden | positive | pass |
| actual_bounded_chunks | positive | pass |
| missing_source_not_fabricated | positive | pass |
| adapter_snapshot_mismatch | source_error | unsupported_capability |
| adapter_row_limit | source_error | resource_limit |
| adapter_chunk_limit | source_error | resource_limit |
| adapter_cancel_before | source_error | cancelled |
| adapter_source_binding_mismatch | source_error | schema_mismatch |
| adapter_malformed_ohlc | source_error | schema_mismatch |
| adapter_source_bounds | source_error | schema_mismatch |
| actual_adapter_conformance | positive | pass |
| request_and_builtin_invariance | positive | pass |

Qualification tests are external drivers, excluded from the fixed619/593 guarded calculation cohort. Two meaningful driver tests bring current fullsuite633. Acquisition adapters remain separate; custom callbacks are trusted local Python. No arbitrary callback correctness, purity, sandbox, native/resource/security, source truth or rights certification; no provider/file/credential/worker/plugin discovery/remote upload support.

Source/tool/test changes require reviewed frozen head, repeat allsix archives/TWO fresh pairs, bothOS head/main CI, actual published blobs/archives/current reports and FOUR actual source pairs locally on Windows (native Linux proof from CI), then reviewed delivery receipt/final archive equality/current provenance/Released readback before Done. [Plan](stories/EQ-095_PLAN.md) and [issue150](https://github.com/atulsrivas1/equity-features/issues/150) record current acceptance; implementation alone does not complete R3.
