# Experimental DuckDB adapter

`equity-feature-duckdb`0.1.0a2 is optional and stays outside both pure packages.
It resolves bounded catalog metadata and maps owned retained-source columns into
canonical schema1. Historical row acquisition remains EQ051. R4 is incomplete.

Callers declare snapshot, units, price interpretation/rounding, source clock,
instrument/session identity and trade eligibility evidence. Missing/null/zero,
unknown known-at, substitutions and unverified admission stay explicit. Hashes
bind bytes; they do not establish provider truth, rights, completeness or PIT.

See repository docs/api/DUCKDB_RESOLVER.md and docs/api/DUCKDB_MAPPING.md.
No provider downloads, credentials, scheduling, publication or live feed.
