## EQ109 external consumer example — in development

[Research consumer](AGENT_RESEARCH.md) uses these unchanged event APIs outside calculations/handlers. Each actual public tool response text is separately retained from assembled evidence; every call/chunk is a distinct call/result pair. Unknown model/times and DEFER/REJECT are declarations, not actor authentication or trading permission. Independent exact wire/digest/previous-link expectations precede append. No event API/schema/version change; native/installed qualification remains pending.

# Agent event evidence API (experimental 0.1.0a1)

EQ106 implements the optional pure `equity-feature-agent-evidence` package. Current
delivery/qualification status is the linked [story206](https://github.com/atulsrivas1/equity-features/issues/206).
Source implementation does not establish released/installed qualification.
The [exact contract](stories/EQ-106_CONTRACT.md) specifies every constructor,
wire field, enum value, required null, bound and error precedence. Public enum
members use uppercase names for their documented lowercase wire values, for
example `EventKind.REQUEST` and `DisclosureState.NOT_SUPPLIED`.

```python
import equity_feature_agent_evidence as a

event = a.EventRecord(
    'demo:research', 1, 'demo:request',
    a.ActorDeclaration(None, a.ActorKind.UNKNOWN),
    a.TimeDeclaration(None, None, None),
    a.TimeDeclaration(100, 'caller-declared', 0), '0' * 64,
    a.RequestSubject('request-1', 'synthetic research', None))
wire = a.encode_event(event)
assert a.decode_event(wire) == event
identity = a.event_reference(event)
```

Exact builtin lists and tuples are accepted at documented collection inputs;
retained/output fields are detached tuples. Frozen nested accepted contract and
fingerprint wrappers are reconstructed from validated public scalars. Each
encoding/identity/check entry revalidates supplied records; there is no global
cache. Python freezing is an application ownership rule, not protection against
an attacker controlling the process or `object.__setattr__` on the retained data.

`encode_event`, `decode_event`, `event_digest`, `event_reference`,
`check_references` and `verify_payload` are the public operations. Payload checks
return `PayloadCheck` with `MATCHED_RETAINED` or `UNAVAILABLE`; matched truncated
bytes never verify omitted bytes. Reference checks return ordered verified and
unresolved tuples. A missing target is unresolved; a retained ID/sequence/kind/hash
conflict refuses. Empty references are vacuously resolved, not proof of history.
At most 64 context events are accepted; this is not a persisted ledger search.

Use [pure supplied examples](../examples/agent_events.py),
[strict public consumer](../examples/agent_events_typed.py) and the
[actual public producer composition](../examples/agent_event_producer.py).
Outer examples and tests come from the exact Git source snapshot, while their
library imports in qualification come from fresh selected wheels/sdists. The
producer example loads one fixed accepted synthetic R9 example and preserves its
full configuration/input/result/quality/source/receipt bytes. It does not fetch
data or invent a native HTTP receipt transport.

## Authority, privacy and retention

Caller actor/model/clock/approval/result labels are declarations. They do not
authenticate a person/model, establish rights, prove source consumption or
execute an approval/cancellation. No hidden chain-of-thought is recorded or
required. The library captures no prompts, tools, arguments, environment or
credentials automatically. Callers must supply public/synthetic values or choose
explicit redacted/not-supplied/unknown/truncated states. An innocent-looking
label can still contain private data; this API promises no secret detector.

Occurrence, recording order/time and simulated C/K/E have distinct meanings.
Late recording may carry earlier occurrence time. No clock read, causal source
reconstruction or source-truth assertion occurs. Hashes verify supplied retained
bytes and declared identity consistency, not authenticity or a complete original
history. Valid prefix truncation/replacement needs separately trusted external
anchors to detect; this package neither stores nor supplies them. Corrections
append references and preserve originals; retention, deletion, global uniqueness,
transactions, crash recovery and replay belong to EQ107's external ledger.

## Compatibility and limits

This is a new optional alpha; existing calculation, result, quality, receipt and
R9 fingerprint schemas and versions are unchanged. No migration of accepted
R9/R10 data is required. Unsupported new event versions/canonicalization refuse;
unknown fields/tags do not silently round trip. Future migrations require a new
explicit contract and retained original evidence. No I/O/model/database/worker/
service/MCP dependency enters the pure package, and calculators do not import it.

Application caps (16 KiB encoded event, 4096 lexical nodes, depth12, bounded
collections and payload/context checks) limit admitted data. They are not physical
RAM/storage/CPU quotas, wall-clock deadlines, process containment or cleanup
guarantees. No source truth, performance speedup, profitability, compliance,
trading execution or new hosted service is certified. Qualification and actual
release evidence must satisfy the [story plan](stories/EQ-106_PLAN.md).
