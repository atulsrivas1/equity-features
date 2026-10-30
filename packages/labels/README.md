# Equity Feature Labels

Experimental `equity-feature-labels==0.1.0a1` for CPython 3.12. Pure immutable
elapsed-horizon price-return labels with explicit origin, supplied raw/split basis,
knowledge cutoffs and pending/incomplete/mature states. Requires only
`equity-feature-contracts==0.0.4a6`; strategies and features are independently optional.

`evaluate_label(LabelRequest(...))` computes endpoint price ratio minus one only
after maturity. No interpolation, calendar, dividends, fetching or adjustment
calculation. A supplied basis is a caller assertion. Label objects cannot be signal
features. See the repository's `docs/research/FORWARD_LABELS.md`, normative contract
and `examples/research_labels.py` for admission, exact failures and explicit as-of
joins. Delivery uses reviewed Windows/Linux GitHub artifacts, not a stable registry.
