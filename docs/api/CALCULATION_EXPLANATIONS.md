# Experimental bounded calculation explanations — EQ099

Optional `equity-feature-explanations==0.1.0a1`, Python>=3.12,<3.13, requires exactly
contracts0.0.4a4/evidence0.1.0a2. It is a separate pure distribution so accepted
receipt/content/bundle versions and numerical source remain unchanged. No
calculator, acquisition, filesystem, clock, credential, transport or resolver is
imported. The [pre-code schema/limits/oracles](../stories/EQ-099_PLAN.md) are normative.

```python
from equity_feature_explanations import explain_result, encode_explanation
summary = explain_result(result, receipt, configuration, entity=entity,
    feature_id="session.trade.count", inputs=(("trades", batch),), evidence_limit=16)
payload = encode_explanation(summary)
```

The caller supplies immutable accepted objects. Complete result/configuration
content and receipt/formula/disclosure bindings are checked, including actual
configuration digest, namespace, session and C/K/E context. An independently
reissued receipt cannot excuse a different configuration context. Every supplied
input must match its complete fingerprint and result input metadata. An omitted
batch leaves its typed input declaration present with content_verified=False;
the package does not fetch it. Supported result columns use the fixed accepted
39 built-in catalog/schema1/algorithmv1/mathv1/python-exact0.0.4a4 declarations.
Every result column must match its catalog output type and unit, including columns outside the focus. Custom registry/callback execution and unknown versions are refused.

Public frozen records: InputSummary(binding,content,content_verified),
EvidenceReference(index,row), ExplanationFinding(code,role=None,evidence_index=None),
and Explanation. Explanation retains the entire typed receipt, focused
entity/feature/formula/version/document, actual QualityRow, input summaries,
reported reference prefix, selected_retained_count and display_limit. Its
receipt_digest, displayed_count, omitted_retained_count and findings are derived.
source_authenticated and execution_verified are fixed false. Detached direct
construction is a declaration; explain_result performs actual supplied-content
validation. There is no decoder or implicit environment installation.

Quality reasons, expected/observed counts and exclusion rows are copied from the
validated result. An explanation does not rerun the formula, infer a missing
population, allocate global evidence loss to an entity, or prove actual historical
consumption. Formula text is the descriptive accepted catalog definition. Matching
hashes do not authenticate source facts/rights, original execution, environment,
mathematical correctness, profitability or regulatory compliance.

The four global disclosure states remain explicit:

| State | Global facts retained |
| --- | --- |
| retained_complete | total_count equals retained_count, including zero |
| truncated | total_count known and greater than retained_count |
| not_supplied | retained_count0, total_count unknown |
| unknown | total_count unknown; retained_count may be positive |

The focused selected_retained_count counts only supplied reported rows for the
selected pair. Display retains the first min(limit,selected) in original order;
omitted_retained_count=selected-displayed. A zero display limit can omit existing
detail; it does not turn that detail into missing proof. Zero focused retained
rows do not certify that no original observations were consumed. A truncated
global3/8 does not establish the focused unretained count. Conflicts/duplicate
logical row identity and unbound references are checked across the complete
result before focus or display filtering.

Reference identity is contextual `(receipt_digest, original_output_index)` with
the complete output content fingerprint. Nested row JSON preserves all11fields,
including exact integer UTCns, nullable known/effective times, use/reason/boundary
strings and entity. These are reported references, not proof of actual input row
membership or consumption. No path, URL, service TTL, storage lifetime, retrieval
promise or rights grant is implied. The caller owns persistence/access/retention.

Derived typed finding codes are input_content_unverified (role),
reported_exclusion (displayed original index), retained_detail_omitted,
global_evidence_truncated/global_evidence_not_supplied/global_evidence_unknown,
and result_unavailable. Findings have no free-form narrative. Their deterministic
order and exact subject/null rules are frozen in the plan. Existing typed
quality reasons remain unchanged; no new leakage/safety verdict is generated.

Limits:64 input declarations,256 result columns,10000 aggregate output entities
and quality rows,4096 full retained references,64 displayed references and131
derived findings. Exact nonbool display_limit0..64. Full-content root/aggregate
controls use accepted typed content bounds; a next rejected root can still be
traversed within its own32MiB bound. Caller-owned input graphs already exist.
Receipt validation is bounded1MiB; output explanation is at most262144bytes,
16384key/value nodes and20container levels. Encoding is sorted compact ASCII
escaped UTF8/no newline, exact integers and allow_nanFalse. Consumers must retain
integer precision beyond2^53. A larger valid receipt may be refused by the smaller
summary limit. Identifiers/formulas/quality are never silently truncated.

Payload-free ExplanationError codes: invalid_schema, unsupported_version,
inconsistent_binding, duplicate, limit_exceeded. There is no returned rejected
prefix, automatic retry or physical memory/deadline guarantee. This is bounded
in-memory application work, separate from operating-system enforcement.

The [actual synthetic example](../../examples/evidence_explanation.py) preserves
3 trades/10 shares/notional1011/vwap101.1/mean_size10/3. The nonempty wire oracle
uses independently hand-reported evidence, not actual producer retention. Corrected
source validation passed27methods and typing; current source-candidate Windows/Linux fresh wheel/sdist archives/maps passed independent audit in [validation](../stories/EQ-099_VALIDATION.json). Final documentation-head/current actual-main publication and acceptance remain separate gates; see [issue199](https://github.com/atulsrivas1/equity-features/issues/199) for subsequent outcomes. Experimental
channel is reviewed GitHub source/current finite-retention CI artifacts; no stable
registry availability is promised. Future schema/catalog/dependency extensions
need explicit versioning and renewed fixtures/qualification.
