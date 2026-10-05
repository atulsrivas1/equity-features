# Contributing

Start with a numbered EQ story and discuss scope before implementation. Keep formulas, units, availability and edge cases explicit.

Use the [two-distribution src layout](docs/PACKAGE_LAYOUT.md). Contracts owns types,
validation/discovery; features depends inward. Concrete sources and workers must
not enter either distribution. Run all reference verifiers and import smoke before
a PR; EQ-009 adds mandatory installed-artifact/type/boundary checks.

Use small linked pull requests. Numerical changes need independent expected fixtures; optimizations need parity and measurements. Use synthetic data and do not include credentials or code/data without redistribution rights.

Contributions are licensed under Apache-2.0. By submitting a contribution, confirm that you have the right to contribute it under this license.
