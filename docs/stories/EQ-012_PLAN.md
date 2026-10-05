# EQ-012 execution plan

Story #15, E03/R0;8points confirmed on pull. Prerequisites: EQ-001–006
mathematics/timing and delivered EQ-011 schema1 canonical inputs. Inspect live
issue/Project and clean main before implementation. First action: map supplied
session/interval bounds, early close, C/K/E and governed windows to EQ-006 rules.

Acceptance: immutable SessionSpec/IntervalSpec carry supplied IDs, namespace,
UTCns, timezone label, actual/scheduled close and auction inclusion. WindowSpec
counts ordered caller-governed sessions, with explicit prior-only/completed-EOD
anchor and target; missing input does not remove a governed slot. AvailabilitySpec
carries market C/knowledge K/evaluation E and known_at/reconstruction identity;
causal C<=E/K<=E, unknown knowledge preserved, reconstruction reason mandatory.
No calendar/timezone discovery, wall clock or numerical calculation.

Configuration: frozen tuple parameters with supported scalar types and unique
names; canonical version1 JSON serializes metadata only. Explicit float64 encoding
preserves finite binary value and signed zero, excludes NaN/infinity. Complete
session/window/timing/adjustment/config identities contribute to SHA256; canonical
ordering makes parameter insertion order irrelevant, unknown fields/versions fail.
Round-trip parsing revalidates bounds/types/identities, never deserializes code.
Experimental alpha0.0.1a2 for both distributions and pinned inward dependency.

Tests: exact ns/int64 endpoints, half-open/closing-auction/quote distinctions,
early-close intervals, causal equality/future/unknown knowledge, reconstruction,
prior-only/completed windows and governed gaps, deep ownership/duplicate keys,
canonical JSON/digest fixture and mutations of every identity, unsupported version,
unknown keys/NaN/infinity. All123references/28prior unit cases, strict types,
core isolation/boundary, repeat builds, fresh wheel/sdist examples, exact-head
Linux/Windows CI, publication bytes and actual main artifacts precede Done.
Docs: contracts/SPECS.md, executable synthetic example, plan, version/build notes
and continuity; author self-review only. E03 stays open for R3 EQ-093. Results,
semantic normalization, registry/protocols remain EQ-013–016; no R1 kernels.
