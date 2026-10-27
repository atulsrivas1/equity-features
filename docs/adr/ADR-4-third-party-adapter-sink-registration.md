# ADR-4: Third-party adapter and sink registration

Status: proposed (decided, pending owner review). Date: 2026-10-27.

## Context

`equity-feature-io-sdk` already has `SourceRegistry` and `SinkRegistry` (`factories.py`): `register(identifier, factory)` with identifier pattern `[a-z][a-z0-9_.-]{0,63}`, duplicate refusal, `protocol_version == "1"`, factories with `validate_config` and `create(config, credentials)`, and capability admission through `admit_source` and `admit_sink`. Config is deliberately inert: keys such as `module`, `import`, `class_path`, `callable`, `password` and `token` are refused, so config can never cause code import.

Missing: how a third-party distribution makes its factory known to a host. Today the host must import and call `register` by hand. There are no entry points anywhere in the three repos. Product model: open source, pluggable adapters and sinks, shipped providers optional.

## Decision

1. Discovery uses Python entry points (`importlib.metadata`) in two groups: `equity_feature.sources` and `equity_feature.sinks`. Entry point name is the registry identifier; value is `module:factory_object`, a ready `ComponentFactory`.
2. Discovery is explicit and opt-in. A new io-sdk helper `load_entry_points(registry, group, *, allow)` loads only identifiers in the host's allow-list. No load-everything default and no config-driven import (preserves the inert-config rule). The host (service, CLI, app) owns the allow-list, so installing a package never activates it.
3. Trust and safety: loading imports third-party code, so (a) the allow-list is mandatory; (b) every loaded factory still passes `register` checks and `admit_source` / `admit_sink` on resolve; (c) sinks must pass the existing `qualify_sink` conformance before a host marks them production-ready; (d) credentials only via `CredentialProvider`, never entry-point metadata; (e) load failures raise typed `FactoryError` naming the identifier, never a silent skip, and one failing plugin does not block the others. Third-party code runs with host privileges; docs say so plainly.
4. Namespacing: shipped providers use bare ids (`duckdb`, `files`); third parties use `vendor.name` (the pattern already allows dots). Duplicates are refused, never overridden.
5. Versioning: the contract is versioned by the existing `protocol_version "1"`; a new protocol uses new group names (`equity_feature.sources.v2`) so old hosts ignore it.
6. Out of scope: remote plugin download, sandboxing, any registry service.

## Existing guards that this decision reverses

The io repo currently enforces the absence of entry points. Adding entry points fails these until they are updated, so updating them is part of the migration:

- `equity-feature-io/tests/probe_foundation.py:43`: `assert not distribution(name).entry_points`.
- `equity-feature-io/tests/matrix/test_composition.py:116`: `assertFalse(distribution('equity-feature-workers').entry_points)`, alongside an exact `requires` list assertion.
- `equity-feature-io/tools/build_foundation.py:88`: build fails on any `entry_points.txt` in an archive.

## Migration and effort

0. Update the three guards first: change each to allow only the two named groups (`equity_feature.sources`, `equity_feature.sinks`) on the packages that declare them, and keep refusing entry points in every other group and on packages that do not declare any. Record the change in the PR so the reversal is explicit and reviewed.

1. Add `load_entry_points` and group constants to io-sdk, and extend the existing `examples/third_party` in the io repo to declare an entry point (small, about half a day).
2. Declare entry points in the shipped `duckdb`, `duckdb-sink`, `files` and `parquet` packages (small).
3. Wire the allow-list setting into the workers service config (small).
4. Docs: authoring guide section and trust notice (small).
5. Manual verification: fresh venv, install the example third-party package, show it absent until allow-listed and present after, and show a bad plugin yields a typed error.

Total about 2.5 days; additive, no breaking change.

## Consequences

Third parties publish a normal wheel and users enable it by name. Importing third-party code is a host-level trust decision. Rejected alternative: config-driven `module:class` strings, which breaks the inert-config invariant.
