# R15 story433: Continuous quote example walkthrough

Issue[433](https://github.com/atulsrivas1/equity-features/issues/433), E22#439/milestone18; 2 provisional points, not days. [Published pre-code plan](https://github.com/atulsrivas1/equity-features/issues/433#issuecomment-6252885238); exact accepted base`7edf1f3c6d360d193ca8512a485cd73e9e734965`.

Explain synthetic100-112 interval categories3normal+4locked+2crossed+3invalid=12ns, valid7ns, unknown/expired0, mean spread6/7, mean bps60000/707; next-update/cutoff versus original expiry, full invalid replacement, valid-only denominator. Preserve formula/example source.

Run existing stdlib tools/verify_quote_examples.py once for this story; review actual fixture/example/formula and every prose/table cell. Verifier does not read the new prose or execute production calculations. Original three acceptance criteria, bounded edit target and source-preservation expectations remain unchanged. Companion continuity edits are documentation only. No package/API/math/version/dependency/workflow change.

[Actual bounded validation](STARTER-433_VALIDATION.json) is separate from exact final source review, required current docs checks, actual default-branch publication and independent fresh acceptance/readback. Those delivery gates remain pending at this freeze. Source receipt deliberately does not claim its own future acceptance.
