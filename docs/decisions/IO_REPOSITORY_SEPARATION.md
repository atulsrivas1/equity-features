# Separate calculation, I/O and worker repositories

Decision: October 6, 2026, owner direction in
[GOV-014](https://github.com/atulsrivas1/equity-features/issues/275).

The earlier roadmap placed optional adapter delivery in the calculation repository.
R4 delivered and qualified that package without making calculations depend on it.
The owner now requires separate repository responsibilities before worker delivery.

Keep `equity-features` for pure canonical contracts and calculations. Create
`equity-feature-io` for separately installable input adapters/output sinks and their
SDK/contracts; create `equity-feature-workers` for orchestration. Preserve the
existing dependency-light input protocol imports and published calculation APIs.
New sink/factory interfaces depend inward on canonical contracts. No circular
dependency, source fetching, credentials or output writes enter calculations.

Consumers inject instances or use explicit factory registries. Sinks convert
standard results to storage formats; workers own task lifecycle and scheduling.
Initial sinks are Parquet and DuckDB; other backend implementations remain later
or consumer-owned scope. Keep adapter acquisition separate from sink publication.

Add R4.1 before R5, with E18/E19 and EQ-121–130. R4 acceptance/history remains
intact; migration qualifies behavior and artifacts rather than changing formulas.
R5 reuses publication types and keeps its task/supervisor/catalog stories. R6
implements providers/files in the I/O repository. No companion repository or
runtime is created by this documentation change.

Consequences: independent installation/testing/release ownership and a compatibility
matrix become required. Version skew, migration and cross-repository traceability
are explicit work, not ignored costs. One companion repository for sources/sinks
avoids extra repositories per interface while keeping independently installable
backend dependencies. Core input protocols remain in place for compatibility.

Normative design and unresolved protocol details:
[IO_WORKER_ARCHITECTURE.md](../IO_WORKER_ARCHITECTURE.md).
