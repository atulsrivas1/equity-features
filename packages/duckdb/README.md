# Experimental DuckDB adapter

`equity-feature-duckdb`0.1.0a3 is optional and stays outside both pure packages.
It resolves bounded catalog metadata and maps owned retained-source columns into
canonical schema1. Bounded original-Parquet historical reads use caller-supplied
sessions, explicit coverage policies and exact UTCns predicates. R4 is incomplete.

Callers declare snapshot, units, price interpretation/rounding, source clock,
instrument/session identity and trade eligibility evidence. Missing/null/zero,
unknown known-at, substitutions and unverified admission stay explicit. Hashes
bind bytes; they do not establish provider truth, rights, completeness or PIT.

See repository docs/api/DUCKDB_RESOLVER.md, docs/api/DUCKDB_MAPPING.md and
docs/api/DUCKDB_READER.md. Installed synthetic reports distinguish whole-read
costs, mapping/copy phases and native lifetime peaks; no hard process cap.
No provider downloads, credentials, scheduling, publication or live feed.


EQ051 clean installation additionally pins NumPy2.2.6 in the optional adapter
runtime. DuckDB1.5.6 create_function requires NumPy in the observed fresh environment;
the development environment had masked this dependency. Install DuckDB1.5.6 and
NumPy2.2.6 explicitly before --no-deps project archive installation. Core runtime
dependencies remain unchanged; NumPy's existing upstream notice/hash provenance
is recorded in [release integrity](../../docs/RELEASE_INTEGRITY.md). Both native installed forms must verify
this exact runtime. Null timestamps pass through the parser and fail closed, following
[DuckDB UDF null semantics](https://www.duckdb.org/docs/current/clients/python/function).
