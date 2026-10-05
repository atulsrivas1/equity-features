# R0 review repair plan — 2026-10-05

Owner requests fixes for two independently reproduced P2 review findings before R1.
Reopen EQ-009#11 and EQ-013#16 and R0; return EQ-017 to Backlog with these blockers.
Use one bounded two-story repair group/PR: one author, two small contracts/CI fixes,
one post-release artifact set and shared review/test gates. This is the recorded
capacity reason for temporarily having two In progress stories, not parallel agents.
Original points and scope remain; this is corrective rework, not new feature scope.

Result admission: share the market-boundary predicate for consumed evidence and
FUTURE_MARKET exclusions. Ordinary trades/quotes at C are outside; bar/daily endpoints
at C and explicit trade closing-auction at C remain admissible. Reject contradictory
reasons and incompatible boundary/kind markers. No math policy/version changes.
Independent trade/quote cases cover before/at/after C, consumed versus excluded,
completed bar/daily/reference endpoints and explicit auction markers.

Boundary policy: replace open NumPy/PyArrow namespace access with reviewed API paths
used by the current copied in-memory bridges. Resolve imports and simple name/attribute
aliases conservatively; reject unreviewed backend imports/accesses, namespace escapes,
wildcards and reported read APIs (including aliased imports). Preserve reviewed type,
array/schema/table conversion calls. Negative/positive development fixtures execute
scanner only, never I/O. The AST guard remains a development policy, not a sandbox.

Version both distributions0.0.1a6.post1. Update API/build/acceptance/continuity docs
in the repair PR, preserve historical alpha6 evidence and deferred PR120/EQ093.
Author self-review, independent regressions,170baseline units/123math references,
strict types/isolation/licensing/compatibility, boundary fixtures, repeated archives
and installed examples; all six exact-head/main checks and all published Git blobs.
Download/hash/inspect both actual main OS bundles and four fresh pair installations
before Released/Done. Then restore E02/R0 acceptance and EQ017 Ready without R1 code.
Publish final delivery identities/expiry/hashes and exact next steps. No independent
review, registry publication, provider/private data or performance claim.
