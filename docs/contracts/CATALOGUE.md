# Where clients find input and output contracts

Clients looking up the input and output contracts of each feature producer should use the generated catalogue, not these core files directly:

- Python module: `equity_feature_io_contracts.catalogue` (package `equity-feature-io-contracts`, repo `equity-feature-io`; lookups `producers()`, `by_feature_id(feature_id)`, `version()`).
- Docs copy: `docs/contracts/catalogue/` in the `equity-feature-io` repo (same bytes as the packaged data, held equal by a drift gate).

Core remains the authority. The frozen core contracts in this repo are the source of truth; the catalogue is generated from them, and on any conflict core wins and the catalogue gate fails.

Status: internal, synthetic, pre-release. Story RL-01-07 delivers the catalogue module; until it merges in `equity-feature-io`, this pointer names a planned location. Rulings: [PO rulings, contract catalogue](../plans/records/po-rulings-contract-catalogue-2026-10-29.md).
