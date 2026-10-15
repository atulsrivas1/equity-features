# equity-feature-evidence

Experimental optional pure receipt contracts, Python3.12. Required dependency:
equity-feature-contracts0.0.4a4. Core calculations do not import this package.

`make_receipt` binds supplied fingerprints/declarations to an accepted FeatureResult's
metadata, feature versions and retained evidence count. `encode_receipt`,
`decode_receipt` and `receipt_digest` provide the closed receipt-json-v1 envelope.
Receipt consistency does not verify external content, source truth, execution,
authenticity, licensing, mathematics or compliance. Fingerprint computation is
separate EQ097 work; bundle I/O/replay and explanations are separate capabilities.

No file/network/clock/credential access, installation, code loading or publication
occurs here. All environment and execution facts are caller declarations. See
docs/stories/EQ-096_PLAN.md in the repository for exact schema/bounds and review.
