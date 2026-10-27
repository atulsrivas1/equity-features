# ADR-3: Capability matrix tracking

Status: proposed (decided, pending owner review). Date: 2026-10-27.

## Context

`.gitignore` lists `work/`, so `work/matrix/` (the dependency and calculation matrices, for example `MASTER_MATRIX.json`, `FEATURE_DEPENDENCY_MATRIX.md`, `CALCULATION_CATALOG.json`) is neither versioned nor reviewable. `git check-ignore -v work/matrix` confirms the ignore, and no file under `work/` is tracked. Meanwhile `docs/` tracks derived artifacts (`EQUITY_EXPANSION_ROADMAP.json`, `FUTURE_LIVE_INTRADAY_INPUTS.json`), so authoritative matrix state is split between ignored scratch and tracked summaries.

The project rule requires every feature to define its data-capability matrix. The current files do not state it in one place.

## Decision

1. `work/` stays ignored scratch. The authoritative matrix moves to a tracked location, `docs/matrix/`:
   - `CAPABILITY_MATRIX.json` (machine source of truth) and `CAPABILITY_MATRIX.md` (rendered, reviewed table);
   - `schema.json` for validation;
   - large generated artifacts (HTML, PNG, review checkpoints) stay in `work/` and are referenced by content hash recorded in the JSON, not copied.
2. Required fields per feature row:
   - `feature_id`, `catalog_ref`, `status` (unverified | verified | not_supported).
   - Data needed: `data_needed`, a list of capability ids from a closed vocabulary (for example `bars_1d`, `bars_1m`, `trades`, `quotes_l1`, `quotes_l2`, `corporate_actions`, `calendar`, `known_at_clock`), each with `history_depth` and `latency_class` (batch | intraday_delayed | realtime).
   - Where it computes: `compute_location` = `client`, `server` or `either`, with a one-line reason (state size, licence, latency).
   - Per source: `per_source`, a map of source id (`platform_feed`, `byok:<provider>`, `files`, `duckdb`, ...) to `supported | degraded | unsupported`, with `degrades_to` when degraded, plus `licence_note` and `verified_on`. All cells start `unverified` until provider terms are checked.
3. Review: changes go by PR; the independent reviewer checks no row lacks the three field groups. `tools/check_matrix.py` (manual run) validates against `schema.json` and cross-checks `feature_id` against the discovery catalogue.
4. Feature docs link to or embed their row. The matrix is the source; docs must not state a different value.

## Migration and effort

1. Convert the current dependency matrix into the new schema with every per-source cell `unverified` (medium, one to two days for the full catalogue; start with the 39 core IDs).
2. Add schema and manual checker (small).
3. Mark `work/` matrix files as derived, non-authoritative. Nothing is deleted.

## Consequences

Provider terms become an auditable column instead of tribal knowledge, and unverified cells are visible. Cost: one maintained file and a checker. Large binaries stay out of git.
