# Start with Equity Features

Use this project when you already have equity observations and want explicit, typed calculations with documented timing, coverage and unavailable-result behavior. Data acquisition, credentials, orchestration and publication belong outside the calculation packages.

## Take the smallest useful path

1. Use the [minimal quickstart](QUICKSTART.md) for the exact delivered three-wheel path, prerequisites, independent expected output and explicit missing inputs. Then read the [supplied-input example catalog](EXAMPLES.md). No market-data account is needed.
2. Follow the matching [build and delivery instructions](BUILD_DELIVERY.md) and [extension installation guide](api/EXTENSIONS.md). Use the reviewed source revision and matching distribution versions. Current artifacts have finite retention; an expired artifact is unavailable evidence, not permission to substitute unrelated bytes.
3. Use the [public API](api/PUBLIC_API.md) for inputs, configuration, calculations and results. Add an optional companion only when your use case needs its responsibility.

CPython 3.12 x64 on Windows and Linux is the supported experimental platform. The [quickstart story](https://github.com/atulsrivas1/equity-features/issues/313) records actual current qualification and measured maintainer timing; source instructions alone do not establish five-minute novice usability.

## Choose a repository

| Repository | Responsibility | Start here |
| --- | --- | --- |
| [equity-features](https://github.com/atulsrivas1/equity-features) | Typed contracts and pure calculations over supplied data, with separately optional research/evidence packages. Canonical library scope, issues, release decisions and acceptance. | [Public API](api/PUBLIC_API.md), [package boundaries](PACKAGE_LAYOUT.md), [accepted release index](releases/R14/R14_RELEASE_PLAN.md). |
| [equity-feature-io](https://github.com/atulsrivas1/equity-feature-io) | Optional acquisition, normalization, adapters and publication components. It owns companion implementation and evidence; calculations remain independent. | Companion README and [I/O/worker architecture](IO_WORKER_ARCHITECTURE.md). |
| [equity-feature-workers](https://github.com/atulsrivas1/equity-feature-workers) | Optional task manifests, supervised orchestration and result sinks; separately optional client/service/MCP surfaces retain their own experimental limits. | Companion README and [scoped worker acceptance](releases/R5/R5_ACCEPTANCE.md). |
| [strategy-research](https://github.com/atulsrivas1/strategy-research) | Independent research questions, datasets/rights, methodology, trial budgets and scientific verdicts. Its owners and Project retain research implementation authority. | Research README, release plans and evidence receipts in that repository. |

Library planning remains in the [canonical Project](https://github.com/users/atulsrivas1/projects/2); companion repositories retain their component implementation. Linking research transfers no ownership or empirical budget. The optional strategies/labels distributions in this library do not mean the independent research program has established a winning strategy.

## Understand the evidence before relying on it

The [R14 release plan](releases/R14/R14_RELEASE_PLAN.md) links scoped accepted engineering receipts. Some older README and installation paragraphs are retained source-freeze history; use the live story's accepted delivery evidence and matching current channel, rather than treating an old pending checkpoint as current status.

Research M2 is partial/unreleased, M3 remains conditional/blocked and M5 remains open. Library-only R14 and [E21](https://github.com/atulsrivas1/equity-features/issues/428) can proceed under the explicit scope amendment; combined [C1/E20](https://github.com/atulsrivas1/equity-features/issues/311) remains open with its research requirements intact.

The [R13 local pilot](EVIDENCE_PILOT_GUIDE.md) supports only its documented local synthetic evidence and replay scope. Its sole evaluation failed final harness closure and remains diagnostic-only; recorded export timings did not meet the accepted limits. Correct replay does not authenticate an input source, establish human usefulness or demonstrate production readiness. Witness expansion remains deferred. No provider entitlement, trading profitability, independent trust or hard physical resource/deadline guarantee follows from the examples.

## Contribute or report a problem

Use [contribution guidance](../CONTRIBUTING.md), the [security policy](../SECURITY.md) and the relevant numbered library issue. Keep examples synthetic or explicitly licensed. Research proposals belong with the research owner; account/profile administration stays with the setup owner. Public data or code licensing does not grant market-data rights.
