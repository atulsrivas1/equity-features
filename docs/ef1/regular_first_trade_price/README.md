# Regular first eligible trade price: proposed public packet

PROPOSED, UNFROZEN, NOT IMPLEMENTED. This packet is a source-safe synthetic
candidate for EQ166/#506, with conversion under EQ212/#570 and orchestration
under EQ213/#571. Independent mathematical and complete literal review passed;
actual whole generic evidence acceptance and a separate packet freeze/source
grant remain pending. Historical generic run1 failed at N154; oracle V3 records
that actual constructor correction, with all inputs/numerical expectations unchanged.
No producer runtime or release acceptance is claimed.

- [Normative proposed contract V2](REGULAR_FIRST_TRADE_PRICE_CONTRACT_V2.md)
- [Closed API boundary](API_BOUNDARY.json) and [existing DTO fields](EXISTING_DTO_FIELDS.json)
- [Full synthetic oracle](REGULAR_FIRST_TRADE_PRICE_ORACLE.json):122 complete
  results,159 isolated input refusals,17 separate result/worker controls
- [Case coverage plan](CASE_COVERAGE_PLAN_V2.json): intent rows, not fixture counts
- [Layer handoffs and acceptance checklist](LAYER_HANDOFFS.md)
- [Synthetic sample request](examples/SAMPLE_REQUEST.json) and
  [whole expected result](examples/SAMPLE_EXPECTED_RESULT.json)
- [Unexecuted SDK-only literal example](examples/SDK_LITERAL_EXAMPLE.py)
- [Preparation status](PREPARATION_STATUS.json),
  [evidence precedence](STATUS_AND_EVIDENCE_PRECEDENCE.md), and
  [source identity and limits](SOURCE_IDENTITY_AND_LIMITS.json)
- [Pending actual generic evidence template](GENERIC_PROBE_ADDENDUM_TEMPLATE.json)
  and [addendum rules](GENERIC_PROBE_ADDENDUM_TEMPLATE.md)
- [Closed candidate manifest](FINAL_PUBLIC_CANDIDATE_MANIFEST.json)

The example carries an independently authored expected FeatureResult through
the existing SDK; it does not call or implement the proposed producer. No
private dataset, provider path, original proprietary specification or private
authoring/review script is included. All sample observations and identities
are explicitly synthetic; original source rights and known-at are unqualified.
