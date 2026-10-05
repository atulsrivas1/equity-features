# EQ-009 execution plan

Story #11, E02/R0; confirmed **8 points**. Prerequisites: reviewed EQ-007 source
layout (awaiting this artifact channel), tested EQ-008 policy PR131/main86321207
and complete formula suite. Start only after EQ-008 main matrix acceptance. Problem:
source-only merges do not deliver usable distributions or enforce pure boundaries.
First action: build both wheel/sdist pairs using pinned isolated tools, inspect
contents and prove repeat builds; then clean-install them outside the checkout.

Acceptance mapping: wheels/sdists → repeatable build/inspection tool; types/tests →
strict mypy and unittest/import/reference checks; pure boundary → allowlisted imports
and denied I/O/clock/process calls with negative fixtures; artifact delivery →
main CI upload, checksum/provenance manifest and actual download/clean install.
Design: fixed SOURCE_DATE_EPOCH, canonical sdist archive headers; explicit build
tool pins, no public registry push. GitHub Actions retained artifacts are the internal
channel (downloadable under repository access, experimental).30-day retention,
commit/OS/run identity and SHA256; immutable archived bundles and reproducible rebuild
commands. Public repository artifacts contain only authorized synthetic/code content.

Tests: exact byte repeat-build parity for four artifacts, archive path/metadata/license
and py.typed inspection; wheel and sdist clean environments; installed import/version
smoke; strict public source typing; negative forbidden alias/dynamic import/open/clock
examples;123reference/planning cases and Linux/Windows final-head/main CI.
No boundary checker proves arbitrary future third-party code purity; state its limits.

Docs: build/channel/retention/rebuild guide, boundary rationale, README/continuity,
release evidence and issue/epic links. End: both distributions genuinely downloaded,
hash/commit verified and clean-installed; only then EQ-009 and waiting EQ-007 can
be Released/Done. PR120 stays deferred; author self-review/CI only. Next EQ-010.
