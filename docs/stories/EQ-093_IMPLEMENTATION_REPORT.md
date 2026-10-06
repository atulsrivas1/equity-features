# EQ093 historical a1 implementation qualification (not release acceptance)

This a1 report is superseded by separate-review corrections and qualified pair0.0.4a3. See [current delivery](EQ-093_DELIVERY.md). Original observations below remain history, not corrected acceptance.

[Issue113](https://github.com/atulsrivas1/equity-features/issues/113), [PR237](https://github.com/atulsrivas1/equity-features/pull/237), source289ac946d96807ec5f653b155cf878013e5c9358; pair0.0.4a1. Owner resumes R3 on October6 after accepted R2. Current stage Code review. No separate completed review, main merge, main experimental publication or Done is claimed.

## Executed qualification

Baseline588units passed. Frozen implementation passes600units, including12 custom fixtures: independent equation/discovery/isolation; duplicate/reserved/namespace; rejected modes; malformed definitions; request/config identity and types; implementation/input/config/C-K-E/math/evidence result bindings; column unit/dtype/algorithm/entity; nullability/callback exceptions; price-unit mismatch; malformed null OHLC; incomplete coverage; future/unknown operand quality. Five independent reference suites pass123cases. Strict typing passes44files, including the separately packaged consumer. Import/compatibility/registry/license and purity38negative/10positive fixtures pass.

Local Windows CPython3.12.10 repeated wheel/sdist builds reproduce all four core archive hashes and pass archive/license/typing inspection. TWO fresh isolated pairs (wheel and sdist) each pass600units and22 existing runnable examples, plus a separately built/installed external wheel. Isolated consumer import locations are installed site-packages, AST imports use public APIs, and core package file hashes remain unchanged across execution. Independent custom range/open5/100 and unchanged built-in range/close5/103 pass. This is local Windows execution; Linux CI is separately cited.

[PR-head bothOS compatibility run](https://github.com/atulsrivas1/equity-features/actions/runs/37465188770) passes Linux and Windows; [documentation run](https://github.com/atulsrivas1/equity-features/actions/runs/37465188730) passes. This source qualification precedes this report-only commit: final-head checks still need completion, and a completed separate review must cover the actual final head. Hosted review requested on PR237; no response/activation is claimed. Existing alternative authorization is bounded to R2; R3 owner choice is pending.

## Artifacts built locally at source289ac94

- `equity_feature_contracts-0.0.4a1-py3-none-any.whl` SHA256 `db9382cf12f456f53476333a388c1be4b1e4c13bfca2a5dce81b3c084c151be9`
- `equity_feature_contracts-0.0.4a1.tar.gz` SHA256 `7b3d982b6b565e7fcbb2fce38dab88c4ad4a0afa3c89f00045b3a4a3abb8606e`
- `equity_features-0.0.4a1-py3-none-any.whl` SHA256 `72cbba9061ab565c446df425bd61bf6ab50fc9e9388b6543daa372a7fac5d865`
- `equity_features-0.0.4a1.tar.gz` SHA256 `1445a7827b538731ea4f11e341128e14dc0f1239ec603f238a7b619bcfe75705`

## Remaining acceptance and exact resume steps

1. Obtain completed separate final-head Codex review (hosted or explicit owner-authorized R3 local alternative); record reviewer identity, coverage, findings/disposition and limitations. No self-review or CI substitution.
2. Pass actual final-head checks and formal Test acceptance; mark Ready to release only when required evidence is complete.
3. Merge using owner attribution, then verify changed public source and bothOS main CI/actual clean manifests, checksums, package content and fresh installed pairs. Record real experimental publication and postrelease acceptance.
4. Update issue acceptance/evidence and tracked receipt/handoff through Released/Done; close E03 only with its actual child gate. Pull EQ043 SDK next. R3 remains twelve stories, eleven unstarted; no R4/stable/PyPI/tag work.

Earlier fixture/build failures are preserved in SESSION_HANDOFF.md and superseded by this frozen qualification. Callable checks establish contracts only; no sandbox, financial/source truth, custom purity, determinism or resource certification. Complete installed adapter/combined-consumer qualification belongs to EQ043/EQ095 and final R3 acceptance.
