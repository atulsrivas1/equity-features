# BUG-004 pre-code plan

Issue #163, R3/E06, confirmed2points. Independent rehashed empty-quote reproduction
at afee24e and again on pair0.0.2a10 raises OverflowError; original state is unchanged.
BUG003 qualified implementation and final receipt publication are prerequisites.

Normalize OverflowError from bounded saved-state payload decoding to
ContractError(INVALID_SCHEMA) through the existing restore exception boundary,
retaining the original exception cause. No calculator is returned on rejection.
No formula, result schema, state field or contract-version change. State remains
schema2; both packages0.0.2a11 and restore still requires exact implementation version,
so older experimental states need replay rather than an implicit migration.

Rehash positive/negative oversized finite exponents (1024 and a much larger exponent),
plus inf/nan/malformed syntax, exercising structural admission instead of checksum
failure. Assert typed code, original state/envelope unchanged and OverflowError cause
for overflow. Verify nonzero finite state exact hex roundtrip and continued results;
retain existing corruption/binding/version/unit tests. Run full units/123refs/strict
26files/purity38negative10positive/import/registry/compatibility/license/planning/
UTF8/links; repeat four archives, local fresh wheel+sdist, six exact-head CI, published
main checks/bytes, both actual OS bundle checks and four fresh pair installs.

Update public result-error/state docs, changelog, receipt, continuity and issue/PR.
Author self-review+CI under deferred GOV005. Observable Done is verified experimental
main artifact delivery and published evidence; owner override then stops this chat.
No R2 implementation or R3 feature work. No stable/PyPI/tag/account changes.
