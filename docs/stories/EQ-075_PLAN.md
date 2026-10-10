# EQ075 pre-code plan — October 9, 2026

[Story #85](https://github.com/atulsrivas1/equity-features/issues/85), [E10 #84](https://github.com/atulsrivas1/equity-features/issues/84), R7 milestone8. Owner requests R7 start after accepted R5/R5.1 and revised R6 closure. First pull is this access/entitlement policy story, one active story. Five provisional complexity points describe design scope, not days.

## Outcome and admission

Define service users/principals, server-approved operations/datasets/components, rights/redistribution decisions, authorization/grant expiry/revocation, quota/retention/cache/audit boundaries before external exposure. This story delivers a reviewed policy document, not an HTTP server, client, MCP endpoint, deployment, provider request or numerical change. Accepted R4.1/R5/R5.1 and R6 research/shared controls/local files/runner provide the architecture prerequisites. Deferred EQ069/070/072/074 do not block a source-independent access policy; actual provider-backed operations remain unavailable until their relevant acceptance and rights pass.

Initial qualification uses owned synthetic fixtures and explicit test principals. Private files/databases and provider data are not approved hosted datasets merely because their adapters work or credentials exist. A real deployment/identity issuer/dataset admission belongs to its actual later story and explicit operational rights; this policy grants no external exposure or paid hosting permission. Transport/schema detail is EQ076, authentication enforcement/slices EQ077, jobs EQ078, delivery EQ079, quota/cache/audit enforcement EQ080, client/MCP EQ081/082 and end-to-end/hosted operations EQ083/084. All ten R7 criteria stay intact.

## Definitions to freeze before runtime

1. Authorization uses a verified opaque principal, named action, immutable dataset/snapshot/mapping/algorithm/config, exact instrument/session/time/feature scope, active rights/grant/policy revision and finite limits. Client fields cannot create grants or select arbitrary imports, paths, SQL or destinations.
2. Rights distinguish raw slice, derived result, retention/cache and redistribution. Public fixtures are owned synthetic; unverified private/provider permissions deny. Local calculation permission is not hosted distribution permission.
3. C/K/E and numerical availability remain supplied facts; access control never manufactures known-at, coverage, session/population compatibility or an exact witness. Wire representation remains EQ076; pure calculations remain unchanged.
4. Limits are exact integer maxima with inclusive count/byte caps and half-open time/expiry intervals. Per-principal and global accounting cover queued/running work, retries/failures and cached/downloaded results. Limits are logical admission bounds, not demonstrated RSS isolation or an SLO.
5. Authorization is rechecked at enqueue, execution, publication/visibility and each fetch; grant revision/expiry/revocation partitions cache/result visibility. Idempotency belongs to principal plus exact command identity, not client job ID alone. Accepted receipt/writer/foreign-completion semantics remain unchanged.

## Independent policy vectors and validation

Freeze a decision table before enforcement: approved synthetic grant; anonymous request; foreign principal; missing dataset/revision/feature permission; expired/revoked grant; derived-only versus raw export; provider credential without rights; raw permission without retention; quota at cap versus one above; revoked cache/result fetch; duplicate exact request versus changed command; arbitrary SQL/path/uploaded callable; unavailable clock; and truthful numerical unknown/future knowledge. Expected authorization decisions are policy requirements, not executed endpoint/security-test evidence. Later runtime stories must execute their actual adversarial/cross-user/install/native cases.

Self-check the policy against existing architecture/acquisition/worker/timing contracts, retained story acceptance, local Markdown links, UTF-8/planning inventory, diff and no runtime/package/core change. Separate final-head semantic review is mandatory; the owner explicitly authorized bounded R7 local review on October 9 after the concrete policy PR was published. Do not infer it or claim review completion. Current native/docs CI, guarded publication, exact tree/author/readback and issue acceptance precede Released/Done; no irrelevant kernel benchmark or provider test is invented for a documentation-only story.

## Exact accepted end state and next step

EQ075 is Done only after published policy covers its two acceptance items, separate actual final-head review/findings disposition and applicable CI/publication/readback. E10 becomes In progress while this work is active; all other R7 children remain Backlog until their own decisions/inputs/readiness. No full R7 completion or automatic remote deployment. After acceptance, the highest dependent candidate is EQ076 transport/schema planning; do not silently start a different release, deferred provider, private generation, stable/registry or recurring work.
