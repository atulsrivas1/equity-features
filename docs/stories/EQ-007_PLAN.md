# EQ-007 execution plan

Story #9, E02/R0; confirmed **5 points**. EQ-001–006 and E01 are Done; PR129
delivered timing policy at 5c8edf56392ac319483669c7f8890597b489ff68, all123
design cases and main CI pass. Public governance/license/contribution files already
exist and are preserved. Problem: reusable code needs explicit distribution ownership.
First action: add two independent src-layout pyprojects and import-only packages.

Acceptance: contracts/features layout and no outward dependencies → package metadata,
import smoke and layout guide; contribution/continuity → existing docs extended;
review/evidence → linked PR and final-head CI. Design: contracts owns semantic types,
validation/registry/protocol metadata; features depends inward on contracts. No stub
calculator modules pretend to implement R1/R2. Both include py.typed and Apache-2.0
license. Experimental version0.0.1a0 is an artifact identifier, not a stable promise.

Runtime/dependency qualification remains EQ-008; skeleton declares Python3.12 only
and uses stdlib imports. Clean build/installation/type enforcement and retained
artifact delivery belong to EQ-009. Tests: isolated package import with optional
source/backend modules denied, version/dependency direction, metadata/py.typed.
All123references/planning/diff checks remain mandatory; no performance claim.

Docs: layout/contribution/README capability statement, plan and continuity. Open
decision resolved: src layout prevents accidentally importing repository tools as
distribution APIs; optional backends are absent until explicitly qualified. End:
source reviewed/CI green and main bytes verified, **Ready to release awaiting EQ-009
foundation artifacts**. This explicit delivery dependency is not waived. Pull EQ-008
after source gates pass; no second active implementation story. Close only after
the declared artifact channel is actually verified.
