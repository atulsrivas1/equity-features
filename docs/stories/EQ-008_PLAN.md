# EQ-008 execution plan

Story #10, E02/R0; confirmed **5 points**. EQ-007 source PR130 is reviewed/merged
at a333fa7af53fc8f33e2b95368a99716bee6658d5 with exact-head/main CI and17blob
verification; that story awaits EQ-009 artifacts. This prerequisite is source layout,
not a waived release gate. EQ-001–006 Done. First action: inspect local CPython and
primary NumPy/Arrow/setuptools documentation, choose bounded versions, test installs.

Acceptance maps runtime/platform/NumPy/Arrow → compatibility policy and CI matrix;
optional backend → explicit columnar extra with dependency-free core; development
environment → full pinned tool requirements and clean venv instructions. Design:
CPython3.12 x64 on Windows/Linux only; exact foundation dependency pins until a
broader compatibility matrix is evidenced. No Polars/native backend in R0.

Tests: clean environment editable install, stdlib-only core imports, optional NumPy
int64 and Arrow UTC-ns/null round trip, platform/runtime/version report; Linux and
Windows matrix CI on exact final head. Preserve123references and planning. Docs:
compatibility policy, decision rationale, install guide and continuity. Missing
setuptools in base environment is an inspected tooling limitation, not failed package
acceptance; build tools go only in isolated development venv. No global install.

Resolve versions empirically; record actual tool/backend versions rather than claim
latest. End: tested policy/documentation published and verified on main, with CI
evidence and issue acceptance. Foundation artifacts and EQ-007 delivery remain EQ-009.
