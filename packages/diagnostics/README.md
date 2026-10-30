# Experimental point-in-time diagnostics

Pure supplied-record checks for market/knowledge/context, historical membership,
revision, adjustment and explicit freshness. Requires Python3.12 and exact contracts
0.0.4a6/evidence0.1.0a4. No calculator, adapter or worker imports.

The public `evaluate_diagnostics(context, policy, checks)` preserves observed failures
alongside missing prerequisites. `unknown` is not an assertion of safety. Strict
admission is a separately selected caller policy. Supplied content/source/history
declarations are not authenticated, and a cited fact is not proof of actual consumption.

See `docs/api/POINT_IN_TIME_DIAGNOSTICS.md` in the repository for the versioned contract,
literal bounds, reasons and limitations. No diagnostic wire format or source acquisition
is provided. Caller owns access, licensing and retention of supplied evidence.
