"""Fixed EQ117 operation boundaries, including nested selected API calls.

Counts are semantic Python/API/stream calls, not instructions, SQL internals,
syscalls, physical I/O or human debugging steps. No outcome-dependent mapping.
"""
from __future__ import annotations
import hashlib
import io
import json
import sys
from typing import Any

OPERATIONS = ('file_read', 'file_write', 'file_close', 'json_decode', 'json_encode',
    'hash_verify', 'event_decode', 'chain_verify', 'ledger_open', 'ledger_append',
    'ledger_verify', 'ledger_export', 'ledger_close', 'bundle_read', 'payload_verify',
    'assessment', 'replay_entry', 'calculator_call')
MAX_EVENTS = 1000000
MAX_RUNS = 4096


class TraceLimitError(ValueError):
    pass


class OperationTrace:
    def __init__(self) -> None:
        import equity_feature_agent_evidence as event
        import equity_feature_agent_ledger as ledger
        import equity_feature_bundles as bundles
        import equity_feature_bundles.replay as replay
        import equity_feature_diagnostics as diagnostics
        import equity_features.session as session
        import evidence_evaluation_observer as observer
        self.functions: dict[Any, tuple[str, str]] = {}
        selected = [
            ('json_decode', 'json.loads', json.loads), ('json_encode', 'json.dumps', json.dumps),
            ('hash_verify', 'observer.hash_verify', observer.hash_verify),
            ('event_decode', 'events.decode_event', event.decode_event),
            ('chain_verify', 'ledger.verify_events', ledger.verify_events),
            ('chain_verify', 'ledger.verify_page', ledger.verify_page),
            ('ledger_open', 'Ledger.create', ledger.Ledger.create.__func__),
            ('ledger_open', 'Ledger.open', ledger.Ledger.open.__func__),
            ('ledger_append', 'Ledger.append', ledger.Ledger.append),
            ('ledger_verify', 'Ledger.verify', ledger.Ledger.verify),
            ('ledger_export', 'Ledger.export_page', ledger.Ledger.export_page),
            ('ledger_close', 'Ledger.close', ledger.Ledger.close),
            ('bundle_read', 'bundles.read_bundle', bundles.read_bundle),
            ('payload_verify', 'events.verify_payload', event.verify_payload),
            ('assessment', 'diagnostics.evaluate_diagnostics', diagnostics.evaluate_diagnostics),
            ('assessment', 'observer.assessment', observer.assessment),
            ('replay_entry', 'replay.replay_bundle', replay.replay_bundle),
            ('calculator_call', 'session.compute_trades', session.compute_trades)]
        for category, name, function in selected:
            assert function.__code__ not in self.functions
            self.functions[function.__code__] = (category, name)
        self.counts = dict.fromkeys(OPERATIONS, 0)
        self.api_counts = dict.fromkeys([name for _, name in self.functions.values()] + ['io.read', 'io.write', 'io.close'], 0)
        self.names = sorted(self.api_counts)
        self.sequence: list[list[int]] = []
        self.event_count = 0
        self.active = False

    def _add(self, category: str, name: str) -> None:
        if self.event_count >= MAX_EVENTS:
            raise TraceLimitError('operation_trace_limit')
        key = [OPERATIONS.index(category), self.names.index(name)]
        same = bool(self.sequence and self.sequence[-1][:2] == key)
        if not same and len(self.sequence)>=MAX_RUNS:
            raise TraceLimitError('operation_trace_runs_limit')
        self.event_count += 1
        self.counts[category] += 1
        self.api_counts[name] += 1
        if same:
            self.sequence[-1][2] += 1
        else:
            self.sequence.append(key + [1])

    def _profile(self, frame: Any, event: str, value: Any) -> None:
        if event == 'call':
            selected = self.functions.get(frame.f_code)
            if selected is not None:
                self._add(*selected)
        elif event == 'c_call':
            stream = getattr(value, '__self__', None)
            if isinstance(stream, io.IOBase):
                name = getattr(value, '__name__', '')
                if name in ('read', 'read1', 'readinto', 'readline', 'readlines'):
                    self._add('file_read', 'io.read')
                elif name in ('write', 'writelines'):
                    self._add('file_write', 'io.write')
                elif name in ('close', '__exit__') and not stream.closed:
                    self._add('file_close', 'io.close')

    def start(self) -> None:
        if self.active or sys.getprofile() is not None:
            raise TraceLimitError('existing_profile')
        self.active = True
        sys.setprofile(self._profile)

    def stop(self) -> None:
        sys.setprofile(None)
        self.active = False

    def summary(self) -> dict[str, Any]:
        assert not self.active and sum(self.counts.values()) == self.event_count == sum(self.api_counts.values())
        raw = json.dumps(self.sequence, separators=(',', ':')).encode('ascii')
        return dict(counts=self.counts, total=self.event_count, api_calls=self.api_counts,
            cli_invocations=1, sequence_sha256=hashlib.sha256(raw).hexdigest(),
            api_name_order=self.names, sequence_encoding='category-index,api-index,positive-repeat-count',
            boundary_scope='selected nested Python APIs and io.IOBase stream calls; not C-internal SQL or OS I/O')
