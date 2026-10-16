"""Actual local SQLite transactions over owned synthetic fixtures; no process faults."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import equity_feature_agent_evidence as a
import equity_feature_agent_ledger as l
from test_pure import load, events, cp

class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='eq107-store-');self.root=Path(self.temp.name)
        self.connections=[];self.serial=0
    def tearDown(self):
        for c in reversed(self.connections):c.close()
        assert self.root.resolve().parent == Path(tempfile.gettempdir()).resolve()
        assert self.root.name.startswith('eq107-store-')
        self.temp.cleanup()
    def rejected(self,call,code):
        with self.assertRaises(l.LedgerError) as caught:call()
        self.assertEqual(caught.exception.code,code)
        self.assertEqual(caught.exception.args,('Agent ledger rejected: '+code,))
    def own(self,c):self.connections.append(c);return c
    def store(self,count=12,chain='demo:chain'):
        self.serial+=1;p=self.root/(str(self.serial)+'.sqlite');db=self.own(l.Ledger.create(str(p),chain))
        for e in events()[:count]:db.append(e,expected=db.head())
        return db,p
    def test_create_open_profile(self):
        db,p=self.store(0);self.assertEqual(db.head(),cp(0));self.assertEqual(db.verify().canonical_event_bytes,0)
        with self.own(sqlite3.connect(p)) as c:
            self.assertEqual(c.execute('PRAGMA journal_mode').fetchone(),('delete',))
            self.assertEqual(c.execute('PRAGMA application_id').fetchone(),(1161907249,))
        db.close();self.assertEqual(self.own(l.Ledger.open(str(p))).head(),cp(0))
    def test_existing_missing_paths(self):
        db,p=self.store(0);old=p.read_bytes();self.rejected(lambda:l.Ledger.create(str(p),'demo:chain'),'storage_error');self.assertEqual(p.read_bytes(),old)
        absent=self.root/'absent.sqlite';self.rejected(lambda:l.Ledger.open(str(absent)),'storage_error');self.assertFalse(absent.exists())
        self.rejected(lambda:l.Ledger.create('relative.sqlite','demo:chain'),'invalid_schema')
        self.rejected(lambda:l.Ledger.open(str(self.root)),'storage_error')
    def test_append_reopen_acknowledgment(self):
        db,p=self.store();self.assertEqual(db.head(),cp(12));self.assertEqual(db.verify(expected=cp(12)).anchor_status,l.AnchorStatus.MATCHED_TERMINAL)
        db.close();reopened=self.own(l.Ledger.open(str(p)));self.assertEqual(reopened.head(),cp(12))
        page=reopened.export_page(after=0,through=cp(12));self.assertEqual([a.encode_event(x) for x in page.events],[a.encode_event(x) for x in events()])
    def test_indexed_references(self):
        for c in load('CASES')['append_refusals']:
            with self.subTest(case=c['id']):
                db,p=self.store(c['initial_prefix']);e=a.decode_event(c['proposal_ascii'].encode('ascii'))
                self.rejected(lambda:db.append(e,expected=db.head()),c['expected']);self.assertEqual(db.head(),cp(c['initial_prefix']))
    def test_stale_cas(self):
        first,p=self.store(1);second=self.own(l.Ledger.open(str(p)));base=second.head()
        first.append(events()[1],expected=base)
        self.rejected(lambda:second.append(events()[1],expected=base),'stale_checkpoint');self.assertEqual(second.head(),cp(2))
    def test_actual_busy_lock(self):
        db,p=self.store(1);other=sqlite3.connect(p,isolation_level=None,timeout=0)
        try:
            other.execute('BEGIN IMMEDIATE');self.rejected(lambda:db.append(events()[1],expected=cp(1)),'busy')
        finally:other.execute('ROLLBACK');other.close()
        self.assertEqual(db.head(),cp(1));db.append(events()[1],expected=cp(1))
    def test_precommit_rollback(self):
        db,p=self.store(1);before=p.read_bytes()
        invalid=replace(events()[1],previous_hash='f'*64)
        self.rejected(lambda:db.append(invalid,expected=cp(1)),'inconsistent_chain')
        self.assertEqual(db.verify().head,cp(1));self.assertEqual(p.read_bytes(),before)
        db.append(events()[1],expected=cp(1))
    def test_unknown_commit_and_rollback_failure(self):
        class Proxy:
            def __init__(self,c,mode):self.c=c;self.mode=mode;self.calls=[]
            def __getattr__(self,name):return getattr(self.c,name)
            def execute(self,sql,*args):
                self.calls.append(sql)
                if self.mode=='rollback' and sql=='ROLLBACK':raise sqlite3.OperationalError('synthetic rollback failure')
                if self.mode in ('ended_commit','ended_rollback') and sql.startswith('UPDATE metadata'):
                    self.c.execute('COMMIT' if self.mode=='ended_commit' else 'ROLLBACK')
                    raise sqlite3.OperationalError('synthetic ended transaction before acknowledgment')
                result=self.c.execute(sql,*args)
                if self.mode=='commit' and sql=='COMMIT':raise sqlite3.OperationalError('synthetic lost acknowledgment')
                return result
        for mode in ['commit','rollback','ended_commit','ended_rollback']:
            db,p=self.store(1);proxy=Proxy(db._conn,mode);db._conn=proxy
            proposal=replace(events()[1],previous_hash='f'*64) if mode=='rollback' else events()[1]
            self.rejected(lambda:db.append(proposal,expected=cp(1)),'outcome_unknown')
            self.rejected(db.head,'closed');self.assertEqual(proxy.calls.count('COMMIT'),1 if mode=='commit' else 0)
            if mode=='ended_commit':
                # The proxy committed INSERT before metadata; this is actual corrupt fixture state,
                # not an alleged supported writer. Reopen must reject it, never silently repair.
                self.rejected(lambda:l.Ledger.open(str(p)),'inconsistent_chain')
            else:
                reopened=self.own(l.Ledger.open(str(p)));self.assertEqual(reopened.head(),cp(2 if mode=='commit' else 1))
                self.assertEqual(reopened.reconcile(events()[1],expected_before=cp(1)).status.value,'found_exact' if mode=='commit' else 'absent_at_unchanged_head')
    def test_reconciliation(self):
        for c in load('ORACLE')['reconciliation_cases']:
            with self.subTest(case=c['id']):
                prefix=c['stored_through'];db,p=self.store(2 if 'stored_canonical_sequence3_ascii' in c else prefix)
                if 'stored_canonical_sequence3_ascii' in c:db.append(a.decode_event(c['stored_canonical_sequence3_ascii'].encode('ascii')),expected=cp(2))
                result=db.reconcile(events()[c['proposal_sequence']-1],expected_before=cp(c['expected_before']))
                self.assertEqual(result.status.value,c['result']);self.assertEqual(result.head,db.head())
        for c in load('CASES')['reconcile_invalid_proposals']:
            db,p=self.store(c['store_prefix_count']);proposal=a.decode_event(c['canonical_event_bytes_ascii'].encode('ascii'))
            self.rejected(lambda:db.reconcile(proposal,expected_before=cp(c['expected_before_record'])),c['error'])
    def test_version_journal_schema(self):
        for c in load('CASES')['stored_mutations']:
            if c['id'] not in ['unsupported_version','wrong_application','unsupported_WAL','extra_table','extra_index','extra_trigger']:continue
            with self.subTest(case=c['id']):
                db,p=self.store();db.close()
                with self.own(sqlite3.connect(p,isolation_level=None)) as conn:
                    for sql in c['fixed_setup_sql']:conn.execute(sql)
                before=p.read_bytes();self.rejected(lambda:l.Ledger.open(str(p)),c['expected_open']);self.assertEqual(p.read_bytes(),before)
    def test_stored_corruption(self):
        for c in load('CASES')['stored_mutations']:
            if c['id'] in ['unsupported_version','wrong_application','unsupported_WAL','extra_table','extra_index','extra_trigger','valid_shortened_prefix']:continue
            with self.subTest(case=c['id']):
                db,p=self.store();db.close()
                params=tuple(bytes.fromhex(x['blob_hex']) if type(x) is dict else x for x in c['parameters'])
                with self.own(sqlite3.connect(p,isolation_level=None)) as conn:
                    for sql in c['fixed_setup_sql']:conn.execute(sql,params if '?' in sql else ())
                self.rejected(lambda:l.Ledger.open(str(p)),c['expected_open'])
    def test_anchored_suffix_loss(self):
        db,p=self.store();db.close();case=next(c for c in load('CASES')['stored_mutations'] if c['id']=='valid_shortened_prefix')
        with self.own(sqlite3.connect(p,isolation_level=None)) as conn:
            for sql in case['fixed_setup_sql']:conn.execute(sql,tuple(case['parameters']) if '?' in sql else ())
        reopened=self.own(l.Ledger.open(str(p)));self.assertEqual(reopened.verify().head,cp(11))
        self.assertEqual(reopened.verify(expected=cp(12)).anchor_status,l.AnchorStatus.NOT_COVERED)
    def test_anchored_replacement(self):
        db,p=self.store(0);e=events()[0];other=replace(e,subject=replace(e.subject,objective='replacement'))
        db.append(other,expected=cp(0));self.assertEqual(db.verify(expected=cp(1)).anchor_status,l.AnchorStatus.MISMATCH)
        self.assertEqual(db.verify().anchor_status,l.AnchorStatus.NOT_SUPPLIED)
    def test_correction_plaintext_retention(self):
        db,p=self.store();page=db.export_page(after=0,through=cp(12));raw=[a.encode_event(x) for x in page.events]
        self.assertEqual(raw,[a.encode_event(x) for x in events()]);self.assertEqual(len(raw),12)
        self.assertEqual(sum(x.kind is a.EventKind.CORRECTION for x in page.events),2)
    def test_fixed_terminal_pages(self):
        db,p=self.store(4);terminal=db.head();second=self.own(l.Ledger.open(str(p)))
        first=db.export_page(after=0,through=terminal,limit=2)
        second.append(events()[4],expected=terminal)
        last=db.export_page(after=first.after.sequence,through=terminal,limit=2)
        self.assertEqual(last.after,terminal);self.assertEqual([e.sequence for e in first.events+last.events],[1,2,3,4])
        self.assertTrue(l.verify_page(last,start=first.after,through=terminal,prior=first.events).reached_terminal)
    def boundary(self,kind):
        spec=load('CASES')['logical_'+kind+'_series'];self.serial+=1;p=self.root/(str(self.serial)+'.sqlite')
        chain='cap:records' if kind=='count' else 'cap:bytes';db=self.own(l.Ledger.create(str(p),chain));db.close()
        base=spec['template'];prev='0'*64;rows=[];total=0;count=spec['count']
        for n in range(1,count+2):
            obj=json.loads(json.dumps(base));obj['sequence']=n;obj['previous_hash']=prev;obj['event_id']='cap:e'+str(n)
            if kind=='byte' and n==1:obj=json.loads(spec['first_ascii'])
            raw=json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii');digest=hashlib.sha256(raw).hexdigest()
            if n==1:first_digest=digest
            if n<=count:rows.append((n,obj['event_id'],obj['subject']['kind'],prev,digest,raw,len(raw)));total+=len(raw);prev=digest
            else:next_raw=raw
        # Exact frozen expectations require using the independently frozen recipe unchanged.
        expected=load('CASES')['logical_'+kind+'_series']
        return db,p,chain,rows,total,prev,next_raw,expected
    def test_count_boundary(self):
        self.check_boundary('count',4096,2217818,'4a16d660d572f04163737bd7286ce7abdb7e8b71917e8410175bcad0408caf6b',542)
    def test_byte_boundary(self):
        self.check_boundary('byte',2241,33551262,'0275570c75623211f6e013f70b9a1c6e51b4310c56da26b2c23718da33199796',14979)
    def check_boundary(self,kind,count,total,head,next_len):
        db,p,chain,rows,actual,hash_,raw,_=self.boundary(kind)
        self.assertEqual((len(rows),actual,hash_,len(raw)),(count,total,head,next_len))
        with self.own(sqlite3.connect(p)) as conn:
            conn.executemany('INSERT INTO events VALUES (?,?,?,?,?,?,?)',rows)
            conn.execute('UPDATE metadata SET event_count=?,head_hash=?,canonical_bytes=?',(count,head,total))
        opened=self.own(l.Ledger.open(str(p)));self.assertEqual(opened.verify().canonical_event_bytes,total)
        self.rejected(lambda:opened.append(a.decode_event(raw),expected=opened.head()),'limit_exceeded')
        self.assertEqual(opened.head(),l.Checkpoint(chain,count,head))
    def test_close_poison_lifecycle(self):
        db,p=self.store();db.close();db.close();self.rejected(db.head,'closed');self.rejected(db.verify,'closed')
        self.assertTrue(p.exists());self.rejected(lambda:db.append(None,expected=None),'closed')
        class CloseProxy:
            def __init__(self,c):self.c=c;self.fail=True
            def __getattr__(self,name):return getattr(self.c,name)
            def close(self):
                if self.fail:self.fail=False;raise sqlite3.OperationalError('synthetic close failure')
                return self.c.close()
        db,p=self.store(0);db._conn=CloseProxy(db._conn)
        self.rejected(db.close,'storage_error');self.rejected(db.head,'closed');db.close();db.close()
        class ReadProxy:
            def __init__(self,c,ended=False):self.c=c;self.ended=ended
            def __getattr__(self,name):return getattr(self.c,name)
            def execute(self,sql,*args):
                if self.ended and sql=='PRAGMA application_id':
                    self.c.execute('ROLLBACK')
                    raise sqlite3.OperationalError('synthetic unexpectedly ended read')
                result=self.c.execute(sql,*args)
                if sql=='ROLLBACK':raise sqlite3.OperationalError('synthetic lost read rollback acknowledgment')
                return result
        for ended in [False,True]:
            db,p=self.store(0);db._conn=ReadProxy(db._conn,ended)
            self.rejected(db.head,'outcome_unknown');self.rejected(db.head,'closed');db.close()

if __name__=='__main__':unittest.main()
