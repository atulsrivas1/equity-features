# Experimental DuckDB adapter

`equity-feature-duckdb` is an optional distribution outside both pure core packages.
Version0.1.0a1 resolves bounded catalog metadata with explicit generation selection
and caller receipt pins. It does not yet deliver canonical rows or calculate features.
Installable/publication acceptance is tracked on EQ049 issue56; R4 is incomplete.

The caller supplies an absolute local catalog path, one curated/prepared snapshot,
dataset/source schema and concrete partition dates. Missing partitions, declared
empty partitions, substitutions and unverified admission remain distinct. Content
hashes bind bytes; they do not establish provider truth, rights, completeness or PIT.

See the repository's `docs/api/DUCKDB_RESOLVER.md` for the public API and limits.
No provider downloads, credentials, scheduling, output publication or live feed.
