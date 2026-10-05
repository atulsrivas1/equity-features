# EQ-095 — External extensibility qualification

Issue [#150](https://github.com/atulsrivas1/equity-features/issues/150), R3/E06.
Backlog; no implementation. Estimate: 5 provisional points.

Start after EQ-093 registration, EQ-039 guide, EQ-040 examples, EQ-043 SDK and
EQ-045 install tooling. Inspect accepted APIs/artifacts, then implement a separately
packaged synthetic consumer with no editable install, private imports or repository
source fallback. Register/discover a versioned namespaced custom feature and use
an independently implemented synthetic adapter passing the public conformance kit.
Check typed values, units, quality, timing and provenance against hand-derived
expectations; verify built-ins and installed core source remain unchanged.

Resolve fixture location, supported execution modes, portable import-isolation
checks and artifact matrix when pulled. Routine implementation choices remain
autonomous. No providers, credentials, plugin discovery, remote execution or
extension security/resource/correctness certification.

Tests: clean supported Windows/Linux wheel and sdist installs, independent output,
discovery, registry isolation, collisions, invalid schema/units/results, missing
inputs, unsupported modes, incompatible versions and core-source integrity.
Supported configuration changes and changed feature meaning are shown separately.

Documentation: reproducible extension guide, consumer fixture, failure/capability
matrix, trusted-code limitations, issue/PR evidence, release notes and continuity.
EQ-048 includes acceptance. Done requires verified artifacts, clean installed tests
and publication; this story qualifies EQ-093/043, not duplicate implementation.
