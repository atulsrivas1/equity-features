# EQ088 whole-pipeline readiness proposal

Local preparation only, October14,2026. [EQ088 #99](https://github.com/atulsrivas1/equity-features/issues/99), E11#95, R8 milestone9; provisional eight complexity points. No implementation, benchmark, independent review, Ready or acceptance. The live issue requires end-to-end throughput/capacity/spill/query-pruning evidence and correctness; more workers require measured benefit. Neither a codec microbenchmark nor a no-change native decision alone satisfies this story.

## Admitted source and first hypothesis

Accepted [EQ085 analysis](EQ-085_ANALYSIS.md) identifies repeated Unicode surrogate validation and materialization/orchestration costs without proving exclusive pipeline savings. Read-only source at accepted I/O19aa266b9debb92a6c5eb707baafeb9ae7a82942 has codec.py:_string scanning every character via ord/any. The bounded candidate hypothesis is an ASCII fast path that retains the complete existing rejection path for non-ASCII strings. No implementation is written or approved by this packet.

The I/O SDK owns codec behavior, workers own scheduling/measurement and canonical docs own the story. Live worker main95aa9ad25e3b095a7ea523140ce0f98fcad4d531 build_foundation still pins core20c08c7370581d03c8a0404579667f68d67ac88b and I/O19aa266. The clean old worker clone28bc095 is not current main. Select current clean implementation branches before component edits and bind every baseline/candidate build to actual source/archive/install identities. A candidate I/O pin update changes a real dependency qualification input, even if public definitions remain the same.

Before Ready, explicitly reconcile any codec work in #99 as a measured whole-pipeline experiment accompanying the required scheduling/output evidence. Do not silently replace the issue's original acceptance. If reconciliation changes owner scope or public commitments, prepare the concrete alternative and obtain that decision. No acceptance box is checked now.

## Baseline and candidate comparison

Reuse all six accepted owned-synthetic workloads (small16, large4096, skew2528; Parquet and DuckDB) with exact task/input/output definitions, complete independent goldens and encoded result/status/quality/evidence/input parity. Baseline and candidate run on the same admitted interpreter/dependency/backend configuration, fresh installed origins and one host. Both use fresh output roots and the same source facts. Keep sequential1/backendthread1 as the baseline. Do not compare old EQ085 samples to a new candidate as a controlled experiment.

Proposed primary comparison: one untimed correctness/warm call per case, five unprofiled runs per baseline/candidate per case, alternating baseline/candidate order and reversing order on the next repetition. Retain all sixty elapsed samples, raw start/order/identity facts, median/min/max, output bytes and failures. Distinct owned output roots, unchanged publisher/receipt/readback/catalog/close boundaries. Requested/effective thread controls, GC/cache/background limits and timeouts are explicit. Diagnostics are separate runs; no profile-frame arithmetic or process-lifetime high-water is relabeled exclusive allocation.

Proposed adoption criterion to freeze before runs: no parity or invalid-input behavior difference; median pipeline elapsed at least 10% lower on both large and skew populations for each sink, with no >10% small-case median regression. Five shared-host observations are descriptive, not a statistical or hardware-independent speed guarantee. If timings overlap materially or a supported comparison is incomplete, record inconclusive/negative and retain baseline. This is a decision rule proposal, not a claimed result or mandated optimization.

## Required scheduling, capacity, spill and pruning matrix

Before Ready, bind a finite synthetic scale-up matrix to the actual supported worker/source/sink APIs and host budgets. Record exact task/row/output sizes, query predicates, supported worker modes, backend memory/spill options, hard sample deadline and owned disk/RAM/thread ceilings in the published packet. Unknown sizes or unsupported knobs prevent this matrix being Ready; they do not authorize an open-ended load test or assumed hard RSS enforcement.

For each admitted scale, compare sequential baseline with supported bounded 2/4-worker modes only when combined worker/backend budgets and source/sink ownership permit. Preserve serialized sink publication, immutable identity/receipt validation, bounded queues, cancellation/restart/ownership and catalog selection. Throughput uses rows or completed tasks per whole pipeline elapsed; capacity is only the largest tested completed configuration within the declared limits. No default increase without full parity, measured whole-pipeline benefit and no unbounded resource claim. Preserve a losing parallel outcome as evidence.

For actual spill-capable backends, compare a declared constrained-memory case with a matching nonspill control, verifying complete output parity and measured spill-file/backend facts. A configured memory limit or a slower call does not prove spill occurred. If the selected backend/API cannot expose reliable spill evidence, record unsupported/unobserved and reconcile the unmet criterion publicly; do not invent a spill pass.

For actual partition/file layout and DuckDB pruning cases, freeze selective and unselective supplied queries over identical logical data, capture planner/operator/scanned-row-or-byte evidence where supported and verify independent selected-result equality. A shorter query or fewer returned rows is not proof of skipped physical reads. Any candidate layout changes preserve partition/query identities, precision, nulls, available timing, generation and receipt consistency. Do not introduce an unmeasured default layout or arbitrary cache.

## Independent codec and integration fixtures

If the codec candidate is selected, freeze valid empty/ASCII/non-ASCII/control text, BMP/non-BMP Unicode, combining sequences, lone high/low surrogates and paired surrogate codepoints in Python strings. Preserve valid actual Unicode scalar text and existing canonical ASCII JSON bytes; both surrogate codepoints remain invalid even when adjacent. Existing scalar/record/schema/identity denial, int64/ns/Decimal/null/Float64 exactness, input ownership/mutation, result/producer/sink/receipt/catalog identity and publication/adversarial tests remain mandatory. An ASCII shortcut may optimize character admission only; it cannot skip content validation, change cache/locks or infer authenticity.

Fixtures and expected canonical bytes/errors must be independently specified, not generated by the candidate. Timing tests do not assert shared-host speed rank. All failed parity, timeout, cleanup and rework attempts are preserved; rerun only changed/corrected inputs with explicit source identities.

## Documentation, release and real next actions

Publish current scope/points, owning repositories, actual finite matrix and admission limits, independent fixture identities and success criteria before implementation. Separate authorized review covers the final plans/source/protocol and affected callers. The initial implementation is one active story, not parallel component work without ownership. Same-story issue/PR, public API/no-impact decisions, full raw measurements, analysis, changelog, scoped lesson and handoff are required.

Changed I/O/worker/build inputs require relevant numerical/boundary/typing/docs, fresh supported Windows/Linux wheel/sdist installs with source-tree fallback rejected, current artifacts/source/RECORD/sdist maps and final exact-head review. Actual default-branch checks/artifact/source and public UTF8/Atul attribution readback precede Released/Done. EQ085 receipts stay frozen history. No registry-stable publishing, private/provider data, admin, live service, spending, R7 replay or automated reminder.

Current remaining preparation: resolve the concrete finite scheduling/spill/pruning matrix and codec-scope reconciliation, then independent plan review, verified Atul Project access, public Ready packet and lifecycle pull. No performance or capacity result exists for this proposal.
