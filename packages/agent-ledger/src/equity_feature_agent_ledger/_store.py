"""Local rollback-journal storage. No application repair, retry or replay."""
from __future__ import annotations
from contextlib import contextmanager
import os
from pathlib import Path
import sqlite3
import stat
from typing import Iterator, Any, cast
from urllib.parse import quote
from equity_feature_agent_evidence import EventRecord, EventReference, encode_event, decode_event, event_reference, AgentEvidenceError
from . import _model as m
from ._schema import DC_PROFILE, TABLE_COLUMNS, INDEX_COLUMNS
from ._verify import scan, references

_ROW = 'sequence,event_id,kind,previous_hash,digest,canonical,byte_length'
_INSERT = 'INSERT INTO events (' + _ROW + ') VALUES (?,?,?,?,?,?,?)'
_UPDATE = 'UPDATE metadata SET event_count=?,head_hash=?,canonical_bytes=? WHERE singleton=1'


def _path(path: str) -> str:
    m.require(type(path) is str and bool(path) and '\0' not in path)
    m.require(len(path) <= 4096, 'limit_exceeded')
    m.require(os.path.isabs(path))
    return path


def _regular(path: str) -> None:
    m.require(stat.S_ISREG(os.lstat(path).st_mode), 'storage_error')


def _connect(path: str) -> sqlite3.Connection:
    return sqlite3.connect('file:' + quote(Path(path).as_posix(), safe='/:') + '?mode=rw',
                           uri=True, timeout=0.0, isolation_level=None,
                           # Older type stubs omit the documented legacy int sentinel.
                           # cast changes only static typing, never its runtime value.
                           autocommit=cast(bool, sqlite3.LEGACY_TRANSACTION_CONTROL))


def _error(exc: BaseException) -> m.LedgerError:
    if isinstance(exc, m.LedgerError): return exc
    if isinstance(exc, sqlite3.Error):
        code = getattr(exc, 'sqlite_errorcode', 0)
        return m.LedgerError('busy' if code & 255 in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED) else 'storage_error')
    return m.LedgerError('storage_error')


class Ledger:
    """One connection to one chain. Use create/open; separate writers use connections."""
    _conn: sqlite3.Connection
    _closed: bool
    _poisoned: bool
    def __init__(self) -> None:
        raise m.LedgerError()

    @classmethod
    def _owned(cls, conn: sqlite3.Connection) -> Ledger:
        value = object.__new__(cls)
        value._conn = conn
        value._closed = False
        value._poisoned = False
        return value

    @classmethod
    def create(cls, path: str, chain_id: str) -> Ledger:
        path = _path(path); m.namespace(chain_id)
        conn = None
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(fd); _regular(path)
            conn = _connect(path)
            conn.execute('PRAGMA journal_mode=DELETE')
            value = cls._owned(conn); value._configure()
            conn.execute('BEGIN IMMEDIATE')
            conn.execute('PRAGMA application_id=1161907249')
            conn.execute('PRAGMA user_version=1')
            for ddl in DC_PROFILE: conn.execute(ddl)
            conn.execute('INSERT INTO metadata VALUES (1,?,?,?,?,?)', ('1', chain_id, 0, m.GENESIS, 0))
            conn.execute('COMMIT')
            value.verify()
            return value
        except BaseException as exc:
            if conn is not None:
                try: conn.close()
                except BaseException: pass
            raise _error(exc) from exc

    @classmethod
    def open(cls, path: str) -> Ledger:
        path = _path(path); conn = None
        try:
            _regular(path); conn = _connect(path)
            value = cls._owned(conn); value._configure(); value.verify()
            return value
        except BaseException as exc:
            if conn is not None:
                try: conn.close()
                except BaseException: pass
            raise _error(exc) from exc

    def _configure(self) -> None:
        c = self._conn
        m.require(c.execute('PRAGMA journal_mode').fetchone() == ('delete',), 'unsupported_version')
        # These settings are connection-local. Opening never converts stored journal/version.
        for name, value in [('synchronous', 2), ('foreign_keys', 1), ('trusted_schema', 0), ('busy_timeout', 0)]:
            c.execute('PRAGMA ' + name + '=' + str(value))
            m.require(c.execute('PRAGMA ' + name).fetchone() == (value,), 'storage_error')
        c.enable_load_extension(False)

    def _live(self) -> None:
        m.require(not self._closed and not self._poisoned, 'closed')

    def _poison(self) -> None:
        self._poisoned = True
        try:
            self._conn.close(); self._closed = True
        except BaseException:
            # Keep the connection reference so explicit close may retry. Never claim cleanup.
            pass

    def _rollback(self, exc: BaseException, started: bool = False) -> None:
        try:
            active = self._conn.in_transaction
            if active:
                self._conn.execute('ROLLBACK')
        except BaseException as rollback:
            self._poison(); raise m.LedgerError('outcome_unknown') from rollback
        if started and not active:
            self._poison(); raise m.LedgerError('outcome_unknown') from exc
        if isinstance(exc, m.LedgerError): raise exc
        raise _error(exc) from exc

    @contextmanager
    def _read(self) -> Iterator[None]:
        self._live()
        started = False
        try:
            self._conn.execute('BEGIN')
            started = True
            yield
        except BaseException as exc:
            self._rollback(exc, started)
        else:
            try: self._conn.execute('ROLLBACK')
            except BaseException as exc:
                self._poison(); raise m.LedgerError('outcome_unknown') from exc

    def _schema(self) -> None:
        c = self._conn
        m.require(c.execute('PRAGMA application_id').fetchone() == (1161907249,) and c.execute('PRAGMA user_version').fetchone() == (1,), 'unsupported_version')
        rows = c.execute('SELECT type,name,tbl_name,sql FROM sqlite_schema ORDER BY name').fetchall()
        expected = [('table', 'events', 'events', DC_PROFILE[1]),
                    ('table', 'metadata', 'metadata', DC_PROFILE[0]),
                    ('index', 'sqlite_autoindex_events_1', 'events', None)]
        m.require(rows == expected, 'inconsistent_chain')
        for table, columns in TABLE_COLUMNS.items():
            m.require(c.execute('PRAGMA table_xinfo(' + table + ')').fetchall() == [tuple(x) for x in columns], 'inconsistent_chain')
        m.require(c.execute('PRAGMA index_list(events)').fetchall() == [(0, 'sqlite_autoindex_events_1', 1, 'u', 0)], 'inconsistent_chain')
        m.require(c.execute('PRAGMA index_list(metadata)').fetchall() == [], 'inconsistent_chain')
        m.require(c.execute('PRAGMA index_xinfo(sqlite_autoindex_events_1)').fetchall() == [tuple(x) for x in INDEX_COLUMNS], 'inconsistent_chain')

    def _metadata(self) -> tuple[m.Checkpoint, int]:
        rows = self._conn.execute('SELECT singleton,schema_version,chain_id,event_count,head_hash,canonical_bytes FROM metadata').fetchmany(2)
        m.require(len(rows) == 1, 'inconsistent_chain')
        row = rows[0]; m.require(row[0] == 1 and row[1] == '1', 'inconsistent_chain')
        try:
            head = m.Checkpoint(row[2], row[3], row[4]); m.integer(row[5], m.MAX_BYTES)
        except m.LedgerError as exc:
            raise m.LedgerError('inconsistent_chain') from exc
        m.require((head.sequence == 0 and row[5] == 0) or (head.sequence > 0 and head.sequence <= row[5] <= min(head.sequence * 16384, m.MAX_BYTES)), 'inconsistent_chain')
        return head, row[5]

    def _decode_row(self, row: tuple[Any, ...]) -> EventRecord:
        try:
            m.require(len(row) == 7 and type(row[0]) is int and type(row[5]) is bytes and type(row[6]) is int, 'inconsistent_chain')
            value = decode_event(row[5]); ref = event_reference(value)
            m.require(row == (value.sequence, value.event_id, value.kind.value, value.previous_hash, ref.digest, row[5], len(row[5])), 'inconsistent_chain')
            return value
        except (AgentEvidenceError, m.LedgerError) as exc:
            raise m.LedgerError('inconsistent_chain') from exc

    def _by_seq(self, sequence: int) -> EventRecord | None:
        row = self._conn.execute('SELECT ' + _ROW + ' FROM events WHERE sequence=?', (sequence,)).fetchone()
        return None if row is None else self._decode_row(row)

    def _by_id(self, identity: str) -> EventRecord | None:
        row = self._conn.execute('SELECT ' + _ROW + ' FROM events WHERE event_id=?', (identity,)).fetchone()
        return None if row is None else self._decode_row(row)

    def _head(self) -> tuple[m.Checkpoint, int]:
        head, total = self._metadata()
        last = self._by_seq(head.sequence)
        if head.sequence == 0:
            m.require(last is None and self._conn.execute('SELECT sequence FROM events LIMIT 1').fetchone() is None, 'inconsistent_chain')
        else:
            m.require(last is not None and last.chain_id == head.chain_id and event_reference(last).digest == head.head_hash, 'inconsistent_chain')
            m.require(self._conn.execute('SELECT sequence FROM events WHERE sequence>? LIMIT 1', (head.sequence,)).fetchone() is None, 'inconsistent_chain')
        return head, total

    def _verify(self, expected: m.Checkpoint | None = None) -> m.Verification:
        self._schema()
        m.require(self._conn.execute('PRAGMA quick_check').fetchall() == [('ok',)] and not self._conn.execute('PRAGMA foreign_key_check').fetchall(), 'inconsistent_chain')
        head, total = self._metadata()
        cursor = self._conn.execute('SELECT ' + _ROW + ' FROM events ORDER BY sequence')
        try:
            checked = scan((self._decode_row(row) for row in cursor), head.chain_id, expected)
        except m.LedgerError as exc:
            raise m.LedgerError('inconsistent_chain') from exc
        finally: cursor.close()
        m.require(checked.head == head and checked.canonical_event_bytes == total, 'inconsistent_chain')
        return checked

    def head(self) -> m.Checkpoint:
        with self._read():
            self._schema(); return self._head()[0]

    def verify(self, *, expected: m.Checkpoint | None = None) -> m.Verification:
        self._live()
        if expected is not None: expected = m.checkpoint(expected)
        with self._read(): return self._verify(expected)

    def append(self, event: EventRecord, *, expected: m.Checkpoint) -> m.Checkpoint:
        self._live(); value = m.event(event); expected = m.checkpoint(expected)
        raw = encode_event(value); ref = event_reference(value)
        started = False
        try:
            self._conn.execute('BEGIN IMMEDIATE')
            started = True
            self._schema(); head, total = self._head()
            m.require(head == expected, 'stale_checkpoint')
            m.require(value.chain_id == head.chain_id and value.sequence == head.sequence + 1 and value.previous_hash == head.head_hash, 'inconsistent_chain')
            m.require(self._by_id(value.event_id) is None, 'duplicate')
            for target in references(value):
                first, second = self._by_id(target.event_id), self._by_seq(target.sequence)
                m.require(first is not None and second is not None and event_reference(first) == event_reference(second) == target, 'inconsistent_reference')
            m.require(head.sequence < m.MAX_EVENTS and total + len(raw) <= m.MAX_BYTES, 'limit_exceeded')
            self._conn.execute(_INSERT, (value.sequence, value.event_id, value.kind.value, value.previous_hash, ref.digest, raw, len(raw)))
            self._conn.execute(_UPDATE, (value.sequence, ref.digest, total + len(raw)))
        except BaseException as exc:
            self._rollback(exc, started)
        try:
            self._conn.execute('COMMIT')
        except BaseException as exc:
            self._poison(); raise m.LedgerError('outcome_unknown') from exc
        return m.Checkpoint(value.chain_id, value.sequence, ref.digest)

    def export_page(self, *, after: int, through: m.Checkpoint, limit: int = 64) -> m.Page:
        self._live(); m.integer(after, m.MAX_EVENTS); through = m.checkpoint(through)
        m.integer(limit, 64); m.require(limit >= 1)
        with self._read():
            self._schema(); head, _ = self._head()
            m.require(through.chain_id == head.chain_id and after <= through.sequence <= head.sequence, 'inconsistent_chain')
            terminal = self._by_seq(through.sequence)
            m.require((through.sequence == 0 and through.head_hash == m.GENESIS) or (terminal is not None and terminal.chain_id == through.chain_id and event_reference(terminal).digest == through.head_hash), 'inconsistent_chain')
            before_event = self._by_seq(after)
            m.require(after == 0 or before_event is not None, 'inconsistent_chain')
            before = m.Checkpoint(head.chain_id, after, m.GENESIS if before_event is None else event_reference(before_event).digest)
            rows = self._conn.execute('SELECT ' + _ROW + ' FROM events WHERE sequence>? AND sequence<=? ORDER BY sequence LIMIT ?', (after, through.sequence, limit)).fetchall()
            values = tuple(self._decode_row(row) for row in rows)
            end = before if not values else m.Checkpoint(head.chain_id, values[-1].sequence, event_reference(values[-1]).digest)
            page = m.Page(before, end, through, values)
            from ._verify import verify_page
            verify_page(page, start=before, through=through)
            return page

    def reconcile(self, event: EventRecord, *, expected_before: m.Checkpoint) -> m.Reconciliation:
        self._live(); value = m.event(event); base = m.checkpoint(expected_before)
        m.require(value.chain_id == base.chain_id, 'inconsistent_chain')
        m.require(value.sequence == base.sequence + 1, 'inconsistent_chain')
        m.require(value.previous_hash == base.head_hash, 'inconsistent_chain')
        status = m.ReconciliationStatus
        with self._read():
            head = self._verify().head
            if base.chain_id != head.chain_id: return m.Reconciliation(status.CONFLICT, head)
            if base.sequence > head.sequence: return m.Reconciliation(status.BASE_NOT_COVERED, head)
            old = self._by_seq(base.sequence)
            digest = m.GENESIS if base.sequence == 0 else event_reference(old).digest if old is not None else None
            if digest != base.head_hash: return m.Reconciliation(status.CONFLICT, head)
            by_id, next_event = self._by_id(value.event_id), self._by_seq(value.sequence)
            if by_id is not None and next_event is not None and encode_event(by_id) == encode_event(next_event) == encode_event(value):
                return m.Reconciliation(status.FOUND_EXACT, head, event_reference(by_id))
            observed = by_id if by_id is not None else next_event
            if observed is not None: return m.Reconciliation(status.CONFLICT, head, event_reference(observed))
            m.require(head == base, 'inconsistent_chain')
            return m.Reconciliation(status.ABSENT_AT_UNCHANGED_HEAD, head)

    def close(self) -> None:
        if self._closed: return
        self._poisoned = True
        try:
            self._conn.close()
        except BaseException as exc:
            raise m.LedgerError('storage_error') from exc
        self._closed = True
