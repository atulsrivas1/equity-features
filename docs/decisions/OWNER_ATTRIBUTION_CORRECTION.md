# Owner attribution correction

Owner-authorized October 5, 2026. All 67 existing main commits were reconstructed with owner author/committer identity; 20 Codex co-author trailers were removed. Every original-to-corrected commit tree was verified equal. Author/committer timestamps and commit topology were retained. Invalidated GitHub signatures were removed from 66 reconstructed commits; corrected commits are unsigned. This establishes metadata/tree parity, not new numerical testing or CI acceptance.

Original main: `14ea19457b324c052bc48a770bae7c2172cbb7c9`. Corrected main: `97133497915bf6bb0b96b31f13122ec230f8b9bf`. The original history is retained in a local bundle. Main force-push permission was temporarily enabled for an exact-SHA leased update, then restored to false. Existing PR and CI requirements were preserved.

[Commit mapping](OWNER_ATTRIBUTION_MAPPING.json) preserves original release/receipt provenance. Old receipts are historical evidence; they are not newly run final-head checks. Existing checkouts must fetch and rebase/cherry-pick unmerged work onto corrected main, preserving local work. Never merge the original main ancestry back. No active development checkout was reset.
