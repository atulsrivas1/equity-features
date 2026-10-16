"""Closed first-version ASCII JSON; canonical identity is not authenticity."""
from __future__ import annotations

import json
from typing import NoReturn, TypeVar, cast
from enum import Enum
from equity_feature_contracts import AvailabilitySpec
from equity_feature_evidence import ContentFingerprint, InputFingerprint
from . import _model as m


def _time(v: m.TimeDeclaration) -> dict[str, object]:
    return {'at_ns': v.at_ns, 'clock_source': v.clock_source, 'uncertainty_ns': v.uncertainty_ns}


def _reference(v: m.EventReference) -> dict[str, object]:
    return {'chain_id': v.chain_id, 'sequence': v.sequence, 'event_id': v.event_id, 'kind': v.kind.value, 'digest': v.digest}


def _payload(v: m.PayloadReference) -> dict[str, object]:
    return {'kind': v.kind.value, 'digest': v.digest, 'retained_bytes': v.retained_bytes, 'full_bytes': v.full_bytes, 'state': v.state.value}


def _fingerprint(v: ContentFingerprint | None) -> dict[str, object] | None:
    if v is None: return None
    return {'domain': v.domain, 'digest': v.digest, 'byte_length': v.byte_length,
            'schema_version': v.schema_version, 'canonicalization': v.canonicalization, 'algorithm': v.algorithm}


def _context(v: m.DecisionContext | None) -> dict[str, object] | None:
    if v is None: return None
    a = v.availability
    return {'namespace': v.namespace, 'session_id': v.session_id,
            'availability': {'market_cutoff_ns': a.market_cutoff_ns, 'knowledge_cutoff_ns': a.knowledge_cutoff_ns,
                             'evaluation_ns': a.evaluation_ns, 'mode': a.mode, 'reconstruction_reason': a.reconstruction_reason}}


def _argument(v: m.Argument) -> dict[str, object]:
    kind = 'null' if v.value is None else 'bool' if type(v.value) is bool else 'int' if type(v.value) is int else 'text'
    return {'name': v.name, 'value': {'kind': kind, 'value': v.value}}


def _subject(v: m.Subject, kind: m.EventKind) -> dict[str, object]:
    d: dict[str, object] = {'kind': kind.value}
    if isinstance(v, m.RequestSubject):
        d.update(request_key=v.request_key, objective=v.objective, context=_context(v.context))
    elif isinstance(v, m.ModelSubject):
        d.update(provider=v.provider, model=v.model, version=v.version, identity_state=v.identity_state.value)
    elif isinstance(v, m.ToolCallSubject):
        d.update(request=_reference(v.request), tool_name=v.tool_name, tool_version=v.tool_version,
                 arguments={'state': v.arguments.state.value, 'total_count': v.arguments.total_count,
                            'entries': [_argument(x) for x in v.arguments.entries]})
    elif isinstance(v, m.ToolResultSubject):
        d.update(call=_reference(v.call), outcome=v.outcome.value, payload=_payload(v.payload))
    elif isinstance(v, m.FeatureReadSubject):
        d.update(result=_reference(v.result), receipt=_payload(v.receipt), configuration=_fingerprint(v.configuration),
                 inputs=[{'role': x.role, 'input_id': x.input_id, 'content': _fingerprint(x.content)} for x in v.inputs],
                 output=_fingerprint(v.output), feature_ids=list(v.feature_ids), context=_context(v.context))
    elif isinstance(v, m.DecisionSubject):
        d.update(request=_reference(v.request), feature_reads=[_reference(x) for x in v.feature_reads],
                 action=v.action.value, reason_code=v.reason_code)
    elif isinstance(v, m.HumanReviewSubject):
        d.update(decision=_reference(v.decision), verdict=v.verdict.value, review_key=v.review_key)
    elif isinstance(v, m.CancellationSubject):
        d.update(target=_reference(v.target), reason=v.reason.value)
    elif isinstance(v, m.ErrorSubject):
        d.update(target=None if v.target is None else _reference(v.target), code=v.code.value)
    else:
        d.update(target=_reference(v.target), operation=v.operation.value,
                 replacement=None if v.replacement is None else _reference(v.replacement), reason_code=v.reason_code)
    return d


def lexical_limits(data: str) -> None:
    """Iterative token budget before parsing; JSON syntax is checked separately."""
    nodes = depth = index = 0
    size = len(data)
    while index < size:
        c = data[index]
        if c == '"':
            nodes += 1; index += 1
            while index < size:
                if data[index] == '\\': index += 2
                elif data[index] == '"':
                    index += 1; break
                else: index += 1
        elif c in '{[':
            nodes += 1; depth += 1; index += 1
            m.require(depth <= m.MAX_EVENT_DEPTH, 'limit_exceeded')
        elif c in '}]':
            depth -= 1; index += 1
        elif c == '-' or c.isdigit():
            start = index; index += 1
            while index < size and data[index] in '0123456789.eE+-': index += 1
            token = data[start:index]
            if not any(x in token for x in '.eE'): m.require(len(token) <= 20, 'limit_exceeded')
            nodes += 1
        elif c.isalpha():
            nodes += 1; index += 1
            while index < size and data[index].isalpha(): index += 1
        else: index += 1
        m.require(nodes <= m.MAX_EVENT_NODES, 'limit_exceeded')


def encode_validated(v: m.EventRecord) -> bytes:
    """Internal projection after the constructor's closed-shape admission."""
    raw = {'actor': {'actor_id': v.actor.actor_id, 'kind': v.actor.kind.value},
           'canonicalization': m.CANONICALIZATION, 'chain_id': v.chain_id, 'domain': m.DOMAIN,
           'event_id': v.event_id, 'occurred': _time(v.occurred), 'previous_hash': v.previous_hash,
           'recorded': _time(v.recorded), 'schema_version': m.SCHEMA_VERSION,
           'sequence': v.sequence, 'subject': _subject(v.subject, v.kind)}
    data = json.dumps(raw, ensure_ascii=True, sort_keys=True, separators=(',', ':'), allow_nan=False)
    m.require(len(data) <= m.MAX_EVENT_BYTES, 'limit_exceeded')
    lexical_limits(data)
    return data.encode('ascii')


def encode_event(event: m.EventRecord) -> bytes:
    return encode_validated(m.copy_event(event))


def _shape(value: object, keys: tuple[str, ...]) -> dict[str, object]:
    m.require(type(value) is dict)
    d = cast(dict[str, object], value)
    m.require(set(d) == set(keys))
    return d


def _array(value: object, limit: int) -> list[object]:
    m.require(type(value) is list)
    result = cast(list[object], value)
    m.require(len(result) <= limit, 'limit_exceeded')
    return result


E = TypeVar('E', bound=Enum)


def _enum(cls: type[E], value: object) -> E:
    m.require(type(value) is str)
    for item in cls:
        if item.value == value: return item
    raise m.AgentEvidenceError()


def _s(v: object) -> str:
    m.require(type(v) is str); return cast(str, v)


def _so(v: object) -> str | None:
    return None if v is None else _s(v)


def _label(v: object) -> str:
    result = _s(v); m.label(result); return result


def _optional_label(v: object) -> str | None:
    return None if v is None else _label(v)


def _i(v: object) -> int:
    m.require(type(v) is int); return cast(int, v)


def _io(v: object) -> int | None:
    return None if v is None else _i(v)


def _integer(v: object, minimum: int = m.I64_MIN) -> int:
    result = _i(v); m.integer(result, minimum=minimum); return result


def _optional_integer(v: object, minimum: int = m.I64_MIN) -> int | None:
    return None if v is None else _integer(v, minimum)


def _read_time(v: object) -> m.TimeDeclaration:
    d = _shape(v, ('at_ns', 'clock_source', 'uncertainty_ns'))
    return m.TimeDeclaration(_optional_integer(d['at_ns']), _optional_label(d['clock_source']), _optional_integer(d['uncertainty_ns'], 0))


def _read_reference(v: object) -> m.EventReference:
    d = _shape(v, ('chain_id', 'sequence', 'event_id', 'kind', 'digest'))
    chain = _s(d['chain_id']); m.identity(chain)
    sequence = _integer(d['sequence'], 1)
    event = _s(d['event_id']); m.identity(event)
    kind = _enum(m.EventKind, d['kind'])
    digest = _s(d['digest']); m.digest(digest)
    return m.EventReference(chain, sequence, event, kind, digest)


def _read_payload(v: object) -> m.PayloadReference:
    d = _shape(v, ('kind', 'digest', 'retained_bytes', 'full_bytes', 'state'))
    kind = _enum(m.PayloadKind, d['kind'])
    digest = _so(d['digest'])
    if digest is not None: m.digest(digest)
    retained = _integer(d['retained_bytes'], 0); full = _optional_integer(d['full_bytes'], 0)
    return m.PayloadReference(kind, digest, retained, full, _enum(m.DisclosureState, d['state']))


def _read_fingerprint(v: object, domain: str) -> ContentFingerprint | None:
    if v is None: return None
    d = _shape(v, ('domain', 'digest', 'byte_length', 'schema_version', 'canonicalization', 'algorithm'))
    dom = _s(d['domain']); m.require(dom == domain)
    dg = _s(d['digest']); m.digest(dg)
    length = _i(d['byte_length']); m.integer(length, minimum=0)
    schema = _s(d['schema_version']); m.require(schema == '1', 'unsupported_version')
    canon = _s(d['canonicalization']); m.require(canon == 'typed-json-v1', 'unsupported_version')
    algorithm = _s(d['algorithm']); m.require(algorithm == 'sha256', 'unsupported_version')
    return ContentFingerprint(dom, dg, length, schema, canon, algorithm)


def _read_context(v: object) -> m.DecisionContext | None:
    if v is None: return None
    d = _shape(v, ('namespace', 'session_id', 'availability'))
    namespace = _s(d['namespace']); m.label(namespace)
    session = _s(d['session_id']); m.label(session)
    a = _shape(d['availability'], ('market_cutoff_ns', 'knowledge_cutoff_ns', 'evaluation_ns', 'mode', 'reconstruction_reason'))
    c = _i(a['market_cutoff_ns']); m.integer(c)
    k = _i(a['knowledge_cutoff_ns']); m.integer(k)
    e = _i(a['evaluation_ns']); m.integer(e)
    mode = _s(a['mode']); m.require(mode in ('known_at', 'reconstruction'))
    reason = _so(a['reconstruction_reason']); m.optional_label(reason)
    if mode == 'known_at': m.require(c <= e and k <= e and reason is None)
    else: m.require(reason is not None)
    return m.DecisionContext(namespace, session, AvailabilitySpec(c, k, e, mode, reason))


def _read_argument(v: object) -> m.Argument:
    d = _shape(v, ('name', 'value')); name = _s(d['name'])
    # Validate this earlier constructor parameter before visiting its value.
    m.Argument(name, None)
    value = _shape(d['value'], ('kind', 'value')); tag = _s(value['kind']); x = value['value']
    types = {'null': type(None), 'bool': bool, 'int': int, 'text': str}
    m.require(tag in types and type(x) is types[tag])
    return m.Argument(name, cast(None | bool | int | str, x))


def _read_arguments(v: object) -> m.ArgumentSet:
    d = _shape(v, ('state', 'total_count', 'entries'))
    state = _enum(m.DisclosureState, d['state']); total = _io(d['total_count'])
    if total is not None: m.integer(total, minimum=0)
    return m.ArgumentSet(state, total, [_read_argument(x) for x in _array(d['entries'], 16)])


def _read_inputs(v: object) -> list[InputFingerprint]:
    result = []
    for x in _array(v, 16):
        d = _shape(x, ('role', 'input_id', 'content'))
        role = _s(d['role']); m.label(role); identity = _s(d['input_id']); m.label(identity)
        content = _read_fingerprint(d['content'], 'canonical_batch'); m.require(content is not None)
        assert content is not None
        result.append(InputFingerprint(role, identity, content))
    m.require(len({x.role for x in result}) == len(result) and len({x.input_id for x in result}) == len(result), 'duplicate')
    return result


def _role(v: object, roles: tuple[m.EventKind, ...]) -> m.EventReference:
    return m.copy_reference(_read_reference(v), roles)


def _read_features(v: object) -> list[str]:
    result = [_label(x) for x in _array(v, 32)]
    m.require(len(set(result)) == len(result), 'duplicate')
    return result


def _read_reads(v: object) -> list[m.EventReference]:
    result = [_role(x, (m.EventKind.FEATURE_READ,)) for x in _array(v, 16)]
    m.require(len({x.event_id for x in result}) == len(result), 'duplicate')
    return result


def _read_receipt(v: object) -> m.PayloadReference:
    result = _read_payload(v)
    m.require(result.kind is m.PayloadKind.EXECUTION_RECEIPT)
    return result


_SUBJECT_FIELDS = {
    m.EventKind.REQUEST: ('kind', 'request_key', 'objective', 'context'),
    m.EventKind.MODEL_DECLARATION: ('kind', 'provider', 'model', 'version', 'identity_state'),
    m.EventKind.TOOL_CALL: ('kind', 'request', 'tool_name', 'tool_version', 'arguments'),
    m.EventKind.TOOL_RESULT: ('kind', 'call', 'outcome', 'payload'),
    m.EventKind.FEATURE_READ: ('kind', 'result', 'receipt', 'configuration', 'inputs', 'output', 'feature_ids', 'context'),
    m.EventKind.DECISION: ('kind', 'request', 'feature_reads', 'action', 'reason_code'),
    m.EventKind.HUMAN_REVIEW: ('kind', 'decision', 'verdict', 'review_key'),
    m.EventKind.CANCELLATION: ('kind', 'target', 'reason'),
    m.EventKind.ERROR: ('kind', 'target', 'code'),
    m.EventKind.CORRECTION: ('kind', 'target', 'operation', 'replacement', 'reason_code'),
}


def _subject_shape(v: object) -> tuple[dict[str, object], m.EventKind]:
    m.require(type(v) is dict)
    raw = cast(dict[str, object], v); m.require('kind' in raw)
    kind = _enum(m.EventKind, raw['kind'])
    return _shape(raw, _SUBJECT_FIELDS[kind]), kind


def _read_subject(v: object) -> m.Subject:
    raw, kind = _subject_shape(v)
    if kind is m.EventKind.REQUEST:
        d = _shape(raw, ('kind', 'request_key', 'objective', 'context'))
        return m.RequestSubject(_label(d['request_key']), _label(d['objective']), _read_context(d['context']))
    if kind is m.EventKind.MODEL_DECLARATION:
        d = _shape(raw, ('kind', 'provider', 'model', 'version', 'identity_state'))
        return m.ModelSubject(_optional_label(d['provider']), _optional_label(d['model']), _optional_label(d['version']), _enum(m.ModelIdentityState, d['identity_state']))
    if kind is m.EventKind.TOOL_CALL:
        d = _shape(raw, ('kind', 'request', 'tool_name', 'tool_version', 'arguments'))
        return m.ToolCallSubject(_role(d['request'], (m.EventKind.REQUEST,)), _label(d['tool_name']), _optional_label(d['tool_version']), _read_arguments(d['arguments']))
    if kind is m.EventKind.TOOL_RESULT:
        d = _shape(raw, ('kind', 'call', 'outcome', 'payload'))
        return m.ToolResultSubject(_role(d['call'], (m.EventKind.TOOL_CALL,)), _enum(m.ToolOutcome, d['outcome']), _read_payload(d['payload']))
    if kind is m.EventKind.FEATURE_READ:
        d = _shape(raw, ('kind', 'result', 'receipt', 'configuration', 'inputs', 'output', 'feature_ids', 'context'))
        return m.FeatureReadSubject(_role(d['result'], (m.EventKind.TOOL_RESULT,)), _read_receipt(d['receipt']), _read_fingerprint(d['configuration'], 'configuration'),
                                    _read_inputs(d['inputs']), _read_fingerprint(d['output'], 'feature_result'),
                                    _read_features(d['feature_ids']), _read_context(d['context']))
    if kind is m.EventKind.DECISION:
        d = _shape(raw, ('kind', 'request', 'feature_reads', 'action', 'reason_code'))
        return m.DecisionSubject(_role(d['request'], (m.EventKind.REQUEST,)), _read_reads(d['feature_reads']), _enum(m.DecisionAction, d['action']), _label(d['reason_code']))
    if kind is m.EventKind.HUMAN_REVIEW:
        d = _shape(raw, ('kind', 'decision', 'verdict', 'review_key'))
        return m.HumanReviewSubject(_role(d['decision'], (m.EventKind.DECISION,)), _enum(m.ReviewVerdict, d['verdict']), _label(d['review_key']))
    if kind is m.EventKind.CANCELLATION:
        d = _shape(raw, ('kind', 'target', 'reason'))
        return m.CancellationSubject(_role(d['target'], (m.EventKind.REQUEST, m.EventKind.TOOL_CALL, m.EventKind.DECISION)), _enum(m.CancellationReason, d['reason']))
    if kind is m.EventKind.ERROR:
        d = _shape(raw, ('kind', 'target', 'code'))
        return m.ErrorSubject(None if d['target'] is None else _read_reference(d['target']), _enum(m.EventErrorCode, d['code']))
    d = _shape(raw, ('kind', 'target', 'operation', 'replacement', 'reason_code'))
    target = _read_reference(d['target']); m.require(target.kind is not m.EventKind.CORRECTION, 'invalid_reference')
    return m.CorrectionSubject(target, _enum(m.CorrectionOperation, d['operation']),
                               None if d['replacement'] is None else _read_reference(d['replacement']), _label(d['reason_code']))


def _pairs(items: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in items:
        m.require(key not in result)
        result[key] = value
    return result


def _reject(value: str) -> NoReturn:
    raise m.AgentEvidenceError()


def decode_event(data: bytes) -> m.EventRecord:
    m.require(type(data) is bytes)
    m.require(len(data) <= m.MAX_EVENT_BYTES, 'limit_exceeded')
    m.require(data.isascii())
    text = data.decode('ascii'); lexical_limits(text)
    error = False
    raw: object = None
    try:
        raw = json.loads(text, object_pairs_hook=_pairs, parse_float=_reject, parse_constant=_reject)
    except (ValueError, RecursionError):
        error = True
    m.require(not error)
    d = _shape(raw, ('actor', 'canonicalization', 'chain_id', 'domain', 'event_id', 'occurred', 'previous_hash', 'recorded', 'schema_version', 'sequence', 'subject'))
    m.require(type(d['domain']) is str and d['domain'] == m.DOMAIN)
    m.require(_s(d['schema_version']) == m.SCHEMA_VERSION, 'unsupported_version')
    m.require(_s(d['canonicalization']) == m.CANONICALIZATION, 'unsupported_version')
    _subject_shape(d['subject'])
    chain = _s(d['chain_id']); m.identity(chain)
    seq = _i(d['sequence']); m.integer(seq, minimum=1)
    identity = _s(d['event_id']); m.identity(identity)
    actor = _shape(d['actor'], ('actor_id', 'kind'))
    declared_actor = m.ActorDeclaration(_optional_label(actor['actor_id']), _enum(m.ActorKind, actor['kind']))
    occurred = _read_time(d['occurred']); recorded = _read_time(d['recorded'])
    previous = _s(d['previous_hash']); m.digest(previous)
    m.require(seq != 1 or previous == m.GENESIS, 'invalid_reference')
    event = m.EventRecord(chain, seq, identity, declared_actor, occurred, recorded, previous, _read_subject(d['subject']))
    m.require(encode_validated(event) == data)
    return event
