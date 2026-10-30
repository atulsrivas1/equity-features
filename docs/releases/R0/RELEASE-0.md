# Release 0 (planning) - exit criteria

> Working document, not a decision. PO, 2026-10-30. Internal, synthetic, pre-release. Release 0 here is an audit and gap-fill: most planning material already exists (`STATUS.md`, `DECISIONS.md`, `docs/BACKLOG.md`, `docs/plans/`, replan and roadmap, `docs/qa/`, `docs/adr/`). Older `R0_ACCEPTANCE.md` in this folder is a historical release and is unrelated. Checklist from `docs/playbook/LIFECYCLE.md` section 1.

| # | Exit criterion | Closer | Status | Evidence |
|---|---|---|---|---|
| 1 | Requirements digest (index of owner rules) | PO | Written; merged (PR 766) | `docs/planning/REQUIREMENTS-DIGEST.md` |
| 2 | Definitions of Ready and Done | PO | Written; merged (PR 766) | `docs/planning/DEFINITIONS.md` |
| 3 | Release map and next-release stories, Ready/Blocked | PO | Written; merged (PR 766), later edits via PR | `docs/planning/RELEASE-MAP.md` |
| 4 | System design (components, ports/adapters, mock adapter per port, data placement) | Architect | Written; PO accepted (PR 765 merged) | `docs/architecture/SYSTEM-DESIGN.md` |
| 5 | Audit of existing system against RL-01 stories | Architect | Written (PR 765, merged); PO accepted | `docs/architecture/EXISTING-SYSTEM-AUDIT.md` |
| 6 | First-release Ready set meets buffer (10) or PO states why short | PO | Not met until core #761 merges (9 Ready, target 10; 11 then) | RELEASE-MAP, Ready buffer |
| 7 | Contracts the release reads exist | Architect | Exist; Architect rulings merged (PR 767, 094a613), PO decided; freeze is RL-01-06 | `docs/dv1/`, `docs/plans/` |
| 8 | Owner-level items named with closer and provisional reading | PO | Done | RELEASE-MAP, owner items |
| 9 | Charter and three-review rule written | Coordinator | Done (adopted 2026-10-30) | `docs/playbook/`, `docs/COORDINATOR_WORKING_AGREEMENT.md` |
| 10 | Missing tools stated | PO | No backlog generator (hand-kept table until about 20 stories); story files for the nine Ready stories written (blocked stories get theirs when Ready) | `docs/releases/RL-01/STORIES.md`, RELEASE-MAP |
| 11 | Checks pass (`python tools/pre_merge_check.py`) | Developer | Not run by the PO | PR Checks section |
| 12 | Documents read by someone other than the author | Coordinator | Done for PRs 765-767; later PRs pending their own reviews | PR Review tables |
| 13 | Owner review held once | Owner | Not held; guide written | [`REVIEW-GUIDE.md`](REVIEW-GUIDE.md); "approve" is a complete answer |

Defaults chosen are logged in `DECISIONS.md` (decided, pending owner review). Builders do not start new feature work before 4-5 and 12-13 close and the team meeting is held.
