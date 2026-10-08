# Explicit acquisition controls (EQ068)

Canonical [story77](https://github.com/atulsrivas1/equity-features/issues/77),
[plan](../stories/EQ-068_PLAN.md), [componentPR12](https://github.com/atulsrivas1/equity-feature-io/pull/12),
[canonicalPR343](https://github.com/atulsrivas1/equity-features/pull/343).
Experimental `equity-feature-acquisition==0.1.0a0` lives in equity-feature-io;
the [public API and limitations](https://github.com/atulsrivas1/equity-feature-io/blob/main/packages/acquisition/README.md)
and [synthetic third-party client](https://github.com/atulsrivas1/equity-feature-io/blob/main/examples/acquisition_consumer.py)
are part of the same story. Reviewed runtime source is published with native installed qualification;
[actual source and release evidence](../stories/EQ-068_DELIVERY.md) retains all
failures/limits. Final documentation/current-main acceptance remains required. Live Project/issue records actual status.

`AcquisitionScope` wraps the existing canonical `AcquisitionRequest` and explicit
provider/dataset/endpoint/mode/source/mapping revision. `DownloadApproval` binds
that exact scope, opaque authorization identity, absolute monotonic expiry and
finite `AcquisitionLimits`. Missing/mismatched consent fails before credential
lookup or transport. Credentials/feature selection/account credit never imply
permission. A caller must obtain explicit user approval for provider downloads
and charges; only free qualification dependencies/artifacts are currently approved.
Unknown cost fails; a zero ceiling admits only a declared conservative zero upper
bound. Integer USD millionths are reserved before every attempt with no refund.

`AcquisitionController.execute` invokes an injected cooperative `Transport` with
the secret for that call and `AttemptBudget` (deadline/remaining rows/bytes/ordinal).
Every explicit page shares the same finite cumulative ledger. `RetryPolicy` permits
typed TRANSPORT/RATE_LIMIT retries only for explicit idempotent reads, finite
attempts and max(capped exponential backoff, Retry-After). A wait reaching the
deadline rejects without sleeping/retrying; sliced waits check cancellation.
Untyped errors terminate. Failed bytes and successful rows/payload bytes consume
budgets. Late/excess results are rejected without claiming completeness. Stable
canonical public errors discard raw exception messages/cause/context. Caller clocks,
credential providers and transports remain trusted; logical bounds cannot preempt
arbitrary callbacks or guarantee network/RSS/billing limits.

`ImmutableCache` defaults disabled. Enabling requires finite payload/entry/TTL policy
and explicit `RetentionApproval` for immutable revision/local use on every access.
Keys bind complete scope/authorization partition/page key; expiry is strict and
does not slide, FIFO eviction is deterministic. Mutable/live/expired use rejects.
Idle expiry schedules no erasure: the caller owns clearing at session/rights expiry;
the cache purges expired entries on enabled operations. No cache hit authorizes a
new download or certifies historical knowledge or data/derived-publication rights.

No calculation formula/units/schema/math version, mandatory pure dependencies,
factory protocol, SDK/contracts0.1.0a2, sink or workers0.1.0a12 change. Independent
owned synthetic schedules precede code; clean Windows/Linux wheel/sdist consumers
must verify public extension, secret-safe failures, exact integer scope, cache
boundaries, strict typing, repeat archives and unchanged core files. This shared
support qualification establishes no provider access, SDK normalization, market
truth, entitlement or data rights. EQ069/070 must separately prove those gates
under explicit scope/download/cost/terms authorization. No registry/stable delivery.
