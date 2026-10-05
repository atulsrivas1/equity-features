# BUG-003 pre-code plan

Issue [#162](https://github.com/atulsrivas1/equity-features/issues/162), R3/E06. Confirm estimate5 points. Prerequisites: accepted R1 APIs and published GOV009 handoff. Independent baseline reproduction on afee24e: restored first-window volume200 and both aggregate statuses Available after contradictory re-certification;370 baseline units pass. BUG004 separately reproduced as OverflowError, remains next story.

## Design and acceptance mapping

Retain an immutable tuple of Boolean known omissions, one per configured structure window. A closed-window certificate with expected>observed records a permanent omission; incomplete chunk-local interval declarations do likewise before publication so legal merges can preserve them. No row history or growing certificate log. Whole-target known_gap includes any window omission. Any subsequent complete whole or affected-window certificate rejects INCONSISTENT_IDENTITY, and lowering/removing expected while keeping incomplete cannot erase the omission. Unaffected independently certified windows remain available with whole coverage incomplete; shares remain unavailable because the denominator is incomplete. No correction API: rebuild/replay from supplied complete facts.

Validate all certificates and construct output on a candidate before committing. Check fixed population interval expected counts against prefix certificates when present. Unknown expected without a known omission may still become complete. Merge ORs flags window-by-window; existing unpublished/nonoverlap restrictions remain. Restore validates exact Boolean tuple length and gap consistency; sealed contradictory certificates reject. State schema2 makes the added fields explicit; reject schema1 and previous implementation versions without migration. Experimental pair0.0.2a10; formula IDs/equations unchanged.

## Independent checks and documentation

Direct/restored original reproduction must reject atomically; incomplete changed/omitted certificate preserves gap; unaffected last window volume300 remains ready; complete whole with missing window rejects; initial same-call whole contradiction rejects; malformed flags and old schema reject; known chunk omission survives legal adjacent merge and restoration; valid no-gap merge unchanged. Goldens200/300 volumes and unavailable shares are hand-derived. Full units,123 references, strict typing, boundary/import/registry/compatibility/release checks, repeat builds, six exact-head checks, main checks, published bytes, actual OS bundles and four fresh pair installs required.

Update incremental/structure/input state and coverage docs, changelog, delivery receipt, continuity and linked issue/PR. Author self-review+CI under deferred GOV005 policy. Done requires verified experimental main delivery, not editable installation or merge. R1 reports remain dated historical evidence; R2 work remains unauthorized.
