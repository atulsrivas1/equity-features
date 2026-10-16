# Proposed continuous research API

EQ112 is the immutable mathematical specification. EQ113 contracts are accepted; EQ114 now implements the own pure batch API in continuous0.1.0a2. [Live kernel delivery](https://github.com/atulsrivas1/equity-features/issues/216) separates source checks, review, installed qualification and acceptance. Old core mathematics,39IDs and ConfigSpec1 remain unchanged; no state/worker/MCP or automatic old-registry integration.

## Preserved specification and review history

The following statements retain their original specification/preparation scopes, not current execution authority.

Specification only. EQ112 freezes mathematics and data; EQ113 will implement the optional data/config/codecs, EQ114 the calculations, and EQ115 the installed guides. These names are not present in the accepted core today. Initial separate package equity-feature-continuous0.1.0a1 depends only on unchanged equity-feature-contracts0.0.4a4. No automatic core registry, Arrow/state, worker/MCP or receipt integration.

The new immutable ContinuousInput contains a ContinuousConfig, continuous/reference Legs, and bounded supplied feed/conversion facts. Reuse exact old IntervalSpec,AvailabilitySpec,PriceUnit,SourceBinding,AdjustmentSpec,Coverage. Supported prices are positive int64 scaled supplied last trades, default raw adjustment only and same currency, with declared underlying/quantity identities. The caller supplies all events, schedules, original knowledge times, scope completeness and ratios; those assertions do not authenticate a market or economic entitlement.

Proposed public computation calls compute_basis(input),compute_freeze(input),compute_reopen(input) return the own ContinuousResult. Each validates the matching config.operation. Basis/premium are latest-known causal comparisons at an anchor. Freeze uses all observations in the supplied finite interval against an eligible fixed reference, count weighting only. Reopen uses last preRcontinuous and first at/afterRreference within complete declared scopes; unknown/late boundary rows block rather than skip. Results cannot be treated as earlier signals: available_at includes every consumed proof and the completed analysis end.

Own exact result metrics are ordered pairs for cross_venue.basis/premium,freeze_max_abs/freeze_mean_abs,reopen_gap/reopen_premium. Signed reduced Rational witnesses have strict numerator/denominator caps; zero0/1 is valid available data. Seven ordered quality roles, closed reasons, selected IDs and bounded topK/proof references preserve missing/incomplete/empty distinctions. Numeric fields are null when required readiness fails. Structured results are not old FeatureResult, and old serializers/compute callers must reject new types rather than silently coerce them.

Strict own envelopes use kinds continuous_config/continuous_input/continuous_result,schema_version1,complete closed payload fields and separate config/input/result SHA256 identities. Runtime admission and codecs reject malformed types/units/identities, unsupported modes, duplicate/unknown fields, boolean integers, noncanonical fractions, wrong kinds/versions and literal byte/collection bounds. Constructor normalization and strict wire representation are distinct. No pickle, class loading, callback, path or URL is accepted.

The normative schema and independently literal oracles in the EQ112 packet define examples and error outcomes before code. A minimal example has continuous120/reference100/unit ratio1:1: basis20,premium1/5. With continuous101 and ratio3/2, reference67: normalized202/3,basis1/3,premium1/201. During a supported freeze continuous101,98,102 versus100 yields max2,mean5/3,topK second then third observation. PreRcontinuous120 versus first eligible reference125 yields gap-5,premium-1/25 only when both prices and all consumed proofs are known. These are specified expectations, not claims that an installed new API has executed.

No interpolation, FX, adjusted-snapshot inference, duration weighting, streaming/checkpoint API, private/provider acquisition, clock/calendar discovery or source/sink work inside calculations. Existing core formulas,39IDs,ConfigSpec1 canonical digest and source-independent boundaries remain unchanged. Experimental artifact versions advance only with their own reviewed implementation/delivery; specification approval alone is not an installed release.

Normative packet: [mathematics](../stories/EQ112_MATHEMATICS.md), [decisions](../stories/EQ112_DECISIONS.md), [schemas](../stories/EQ112_SCHEMAS.json), [independent literal fixtures](../stories/EQ112_FIXTURES.json), and [delivery plan](../stories/EQ112_PLAN.md).

## EQ112 changing-ratios coverage correction

Actual public review at60345f0 found that the original changing-ratios criterion lacked admitted same-pair nonoverlapping conversion changes. The first97 literal records remain unchanged; two appended full-input/full-result examples now make99. Freeze101/98/102 against100 with1:1 before102 and2:1 from102 gives deviations1,-51,-49, max51 and observation mean101/3; topK c2,c3 binds conversion-2, and conversion proofs include both facts. At reopenR200, continuous199 still uses the old1:1 factor despite a2:1 factor effective atR; gap-5/premium-1/25 remains, only the old mapping is consumed, and the full input digest binds both facts. These are independent literal/data-tool expectations, not executed kernels. Earlier prepared/public approval missed this absence and is preserved with its exact97-record scope. EQ112 returned Code review to In progress before correction; renewed final working/public/current CI/main gates remain.


## EQ115 supplied consumer qualification

The [installed synthetic guide](../CONTINUOUS_SUPPLIED_WEEK.md) exercises the accepted public APIs with
twelve new complete independent supplied results. No equation, unit, schema,
package source/version or registry entry changes here. Own six descriptive batch
IDs remain separate from the old39-ID registry; update/merge/restore are unsupported.
Actual ConfigSpec JSON decoding and FeatureResult constructor type boundaries
are tested without inventing an old result decoder. File I/O stays in the external
consumer, not calculations. Full input identities include unused supplied facts;
original knowledge/quality is never refreshed by replay. Live217 records current
source, installed and final delivery evidence. Logical caps do not prove physical
resource containment or deadlines; no market/provider/trading claim follows.
