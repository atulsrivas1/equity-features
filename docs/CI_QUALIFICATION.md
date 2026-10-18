# R16 qualification reader and controlled probes

CI003#446 follows accepted CI002#445. The implementation is a standalone data
reader, not a library API or a replacement package builder. Its reviewed source
is in [CI-003_QUALIFIER.txt](stories/CI-003_QUALIFIER.txt), with
[synthetic controls](stories/CI-003_QUALIFIER_TESTS.txt) and
[sealed source/layout rules](stories/CI-003_SOURCE_RULES.json).

Copy exact Git blob bytes into a new owned directory as `qualifier.py` and
`test_qualifier.py`. Verify the source digests before execution. Use the existing
trusted Python and scoped GitHub CLI access; never import or install downloaded
payloads. Run the synthetic controls before collecting a selected case.

The reader accepts a closed `equity-features.ci003-input.v1` JSON object with
`case`, `roots`, `reader_head`, `contract_path`, `contract_sha256`,
`source_rules_path` and `source_rules_sha256`. `roots` supplies existing local
canonical, I/O and worker Git repositories. The reader binds its own copied bytes
and both input documents to the immutable `reader_head`; companion commits are
fixed in source. It requires a new output directory:

```text
python qualifier.py reviewed-input.json NEW-owned-output-directory
```

A case has exactly `kind`, `run_id`, `attempt`, `event`, `api_head`,
`checkout_head`, `base` and `ref`. Only FULL, reader-only DOCS, source-negative
and docs-negative observations are admitted. Runtime IDs and PR merge checkouts
must come from the separately reviewed publication/outer collector, not an
arbitrary PASS receipt. A source-copy check is not protection against an
authorized author replacing source and its selected revision.

The source/layout rules retain both operating systems' actual accepted-CI002
artifact inventories and selected source sets. Existing builder/tool/workflow
bytes are sealed, and current project archive bytes must retain their accepted
per-OS identities. This release changes qualification documentation assets and
continuity, outside those original selected-source globs. An unknown layout,
source selection or builder change denies admission instead of weakening the
audit. Independent review must confirm those selection sets against the actual
immutable consumers; a producer's declared subset is insufficient.

The audit joins exact run/attempt/event/head, final complete jobs and critical
steps, registered workflow, current artifact metadata and downloaded bytes.
It checks every outer member and declared project wheel/SDist in memory,
including aliases, local ZIP framing, bounded GZIP/TAR/PAX, RECORD, source,
metadata, generated SDist transitions and original installed proof fields.
Quickstart retains its original accepted foundation fixture and complete
synthetic output. Declared dependency wheels absent from the uploaded artifact
remain metadata/existing installed-qualification evidence, explicitly not an
independent byte or source-binary audit of those unuploaded payloads.

Intentional failures remain failed aggregate runs. A negative observation needs
its exact expected full vector and specific failing step; another fault is
diagnostic-only. Reader-only skipped package calls are NOT QUALIFIED. Cancellation
requests and cancelled/superseded runs are never PASS or physical-cleanup proof.
No probe branch is merged. Close the observed reader probe PR unmerged before
release-branch publication, preserving its immutable merge/source/readback.

Job/step elapsed times describe observed gross work, not CPU usage, queue time,
universal speedup or a service commitment. These reader limits and source checks
do not attest the host, interpreter, kernel, hardware, third-party binaries or
physical resource cleanup. Existing package checks and all deferred scope remain
unchanged. Initial source publication is not executed qualification: exact source
review, synthetic controls, actual cases, final current candidate/main artifacts
and independent acceptance remain mandatory.

The corrected reader inspects TAR name/prefix bytes before normalization, refuses hidden link fields and unsafe PAX placeholders, and bounds each Git blob before reading its body. Installed maps require nested file identities; continuous typing/week/absence proofs bind the accepted deterministic per-form records. Quickstart binds all 27 retained sanitized logs and fixed commands independently of raw-private byte counts. Redacted raw logs are unavailable; no original path/output recovery is claimed. Four physical ZIP descriptor encodings have independent synthetic fixture sources. These source corrections are unexecuted pending renewed exact-source review.

Only explicit USTAR magic/version is admitted for the declared USTAR/PAX framing; unknown interpretations are rejected. Descriptor controls cover signed/unsigned32/64 framing and bad CRC, truncated and wrong-width forms. Corrected documentation restores the exact historical UTF8 suffixes from74cdf after a preparer default-encoding mistake; that rejected192e source remains preserved.
