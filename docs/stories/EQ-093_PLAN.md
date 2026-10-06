# EQ-093 pre-code plan

Owner resumes bounded R3 autonomous delivery on October 6, 2026, after accepted R2. [Issue113](https://github.com/atulsrivas1/equity-features/issues/113); E03; milestone4; provisional8points. Both repairs and EQ013/015 are Done. Current corrected main7333d34 is the starting source; no old ancestry is merged.

## Contract before implementation

Add immutable caller-owned CustomRegistry with explicitly supplied trusted batch callable registrations. Keep FeatureDefinition/Registry and all39 built-in definitions unchanged. CustomDefinition wraps schema1 definition metadata (without built-in execution claims), implementation ID/version, configuration parameter types, and truthful batch-only capabilities. Inputs initially support declared canonical:1 roles/kinds/fields, with supplied ConfigSpec/EntityKey. Other schemas and update/restore/merge reject before invoking a callback; further modes require separate qualified implementations.

A registration has exactly one result column, identified by the namespaced custom feature ID and algorithm version, with declared dtype/unit/nullability. Canonical input roles, configuration identity/algorithm/parameter types, entity/session and output ResultMetadata bindings are checked. Existing FeatureResult admission retains finite value, quality/null and evidence invariants. Configuration digest, C/K/E, inputs, implementation ID/version and result schema must equal the exact execution request. No executable serialization or source discovery. Metadata export is discovery only and cannot restore execution.

Independent example mathematics: two supplied bars O100 H103 L99 C102 and O102 H104 L101 C103 give session O100 H104 L99 C103. Built-in range/close=5/103; custom range/open=5/100=0.05 (dimensionless fraction). Missing inputs/zero denominator are unavailable with explicit quality; temporal admission remains governed by supplied market and knowledge cutoffs. Trusted calculators own their equation/readiness and tests; contract checks certify no mathematical correctness, sandbox, source truth, purity or resource bound.

## Acceptance mapping and tests

Explicit immutable registration/discovery, namespace/built-in collision and duplicate rejection, no global mutation; definition metadata and parameter contracts; exact request/result binding; independent custom/built-in goldens; malformed units/schema/version/entity/config/input/implementation outputs; non-nullable output; unsupported modes and schemas; separate registries and metadata-only export; separately packaged public-API synthetic consumer. Tests execute real public APIs, including zero/missing/timing boundaries, and unchanged built-in catalog identity.

## Documentation and delivery

Add api/CUSTOM_FEATURES.md, external consumer package and runnable commands, changelog/version pair0.0.4a1; update design, examples/build qualification, continuity and knowledge. EQ039 final guide/EQ040 full examples/EQ044 compatibility/EQ095 whole consumer qualification/EQ048 final acceptance follow, without a dependency cycle. Full current numerical/reference/type/boundary checks, repeated builds, bothOS CI and actual clean wheel/sdist installed consumer validation remain gates.

Open draft PR before code; Code review requires completed separate final-head Codex review. Hosted activation remains unverified. Existing local alternative is R2-bounded; R3 owner alternative choice is pending. Do not merge before policy is satisfied. Observable Done requires review, final head/main checks, published source and actual experimental bundle qualification, issue evidence and Project lifecycle. No stable/PyPI/tag or R4 work.
