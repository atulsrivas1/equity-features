"""Fresh installed, fixed child-death controls; source review required before use."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import sys
import tempfile
import threading
import time
import unittest
import equity_feature_agent_evidence as a
import equity_feature_agent_ledger as l

ROOT=Path(__file__).resolve().parents[2]
FIXTURES=ROOT/'docs/stories'
HELPERS=ROOT/'tools/qualification'

def bounded_json(path,cap):
    with path.open('rb') as stream:raw=stream.read(cap+1)
    assert len(raw)<=cap
    return json.loads(raw)

def wait_inactive(child, *, clock=time.monotonic, sleep=time.sleep):
    """Observe zero accounting before reopen; expiry/query failure is failure."""
    deadline=clock()+4
    while True:
        count=child.active()
        if type(count) is not int or not 0<=count<=2:
            raise ValueError('invalid child accounting')
        # Even zero observed after the observation deadline does not qualify.
        if clock()>=deadline:
            raise TimeoutError('child accounting did not settle within observation bound')
        if count==0:return
        sleep(.01)

class CrashTests(unittest.TestCase):
    def exercise(self,mode):
        started=time.monotonic()
        assert sys.flags.isolated
        assert all('site-packages' in Path(module.__file__).resolve().parts for module in (a,l))
        parent=Path(tempfile.gettempdir()).resolve()
        root=Path(tempfile.mkdtemp(prefix='eq107-crash-',dir=parent)).resolve()
        assert root.parent==parent and root.name.startswith('eq107-crash-')
        child=None;readers=[];streams=[];errors=[];settled=False;body_ok=False;store=None
        try:
            fixture=json.loads((FIXTURES/'EQ-107_ORACLE.json').read_bytes())
            rows=fixture['records'];original=[x['canonical_bytes_ascii'].encode('ascii') for x in rows]
            store=l.Ledger.create(str(root/'events.sqlite'),'demo:chain')
            for raw in original:store.append(a.decode_event(raw),expected=store.head())
            before=store.head();self.assertEqual(before.sequence,12);store.close();store=None
            case=json.loads((FIXTURES/'EQ-107_CRASH_PROPOSAL.json').read_bytes())
            raw=case['canonical_bytes_ascii'].encode('ascii')
            self.assertEqual(hashlib.sha256(raw).hexdigest(),case['sha256'])
            (root/'proposal.json').write_bytes(raw);proposal=a.decode_event(raw)
            entry=(HELPERS/'eq107_crash_entry.py').resolve();source=entry.read_bytes();self.assertLessEqual(len(source),8192)
            owner_file=HELPERS/('eq107_windows_owner.py' if os.name=='nt' else 'eq107_linux_owner.py')
            owner=runpy.run_path(str(owner_file))['WindowsReferenceChild' if os.name=='nt' else 'LinuxReferenceChild']
            argv=[sys.executable,'-I',str(entry),str(root),mode]
            child=owner(argv,hashlib.sha256(source).hexdigest())
            for pipe in (child.stdout,child.stderr):
                bucket=[];streams.append(bucket)
                def read(pipe=pipe,bucket=bucket):
                    try:
                        raw=pipe.read(2049)
                        if len(raw)>2048:raise ValueError('bounded child output')
                        bucket.append(raw)
                    except BaseException as exc:bucket.append(exc)
                reader=threading.Thread(target=read,daemon=True);readers.append(reader);reader.start()
            until=time.monotonic()+4
            while not (root/'ready.json').exists():
                if time.monotonic()>=until or child.poll() is not None:raise ValueError('entry readiness failed')
                time.sleep(.005)
            ready=bounded_json(root/'ready.json',256)
            self.assertEqual(set(ready),{'pid','isolated'});self.assertIs(ready['isolated'],True)
            self.assertIs(type(ready['pid']),int);child.verify_entry(ready['pid'])
            self.assertFalse(child.entry_exited())
            with (root/'GO').open('xb') as stream:stream.write(b'go')
            self.assertEqual(child.wait(4),91);self.assertTrue(child.entry_exited())
            wait_inactive(child)
            phase=bounded_json(root/'phase.json',1024)
            expected={'mode':mode,'pid':ready['pid'],'rows':12 if mode=='before_BEGIN' else 13,
                      'metadata':13 if mode in ('after_metadata','after_COMMIT') else 12,
                      'in_transaction':mode in ('after_INSERT','after_metadata')}
            self.assertEqual(phase,expected);self.assertIs(type(phase['rows']),int);self.assertIs(type(phase['metadata']),int);self.assertIs(type(phase['in_transaction']),bool)
            reopened=l.Ledger.open(str(root/'events.sqlite'));store=reopened
            committed=mode=='after_COMMIT'
            terminal=reopened.head();self.assertEqual(terminal.sequence,13 if committed else 12)
            page=reopened.export_page(after=0,through=terminal)
            expected_raw=original+([raw] if committed else [])
            self.assertEqual([a.encode_event(x) for x in page.events],expected_raw)
            self.assertEqual(reopened.verify(expected=terminal).canonical_event_bytes,sum(map(len,expected_raw)))
            result=reopened.reconcile(proposal,expected_before=before)
            self.assertEqual(result.status,l.ReconciliationStatus.FOUND_EXACT if committed else l.ReconciliationStatus.ABSENT_AT_UNCHANGED_HEAD)
            if committed:
                # Explicit new valid append, not a replay of the uncertain proposal.
                obj=json.loads(raw);obj.update(sequence=14,event_id='demo:later_model',previous_hash=terminal.head_hash)
                later=a.decode_event(json.dumps(obj,sort_keys=True,separators=(',',':')).encode('ascii'))
                reopened.append(later,expected=terminal)
                self.assertEqual(reopened.reconcile(proposal,expected_before=before).status,l.ReconciliationStatus.FOUND_EXACT)
            body_ok=True
        finally:
            active_exception=sys.exc_info()[0] is not None
            if store is not None:
                try:store.close()
                except BaseException as exc:errors.append(exc)
            if child is not None:
                try:
                    child.close();settled=child.ownership_closed
                except BaseException as exc:errors.append(exc)
                for reader in readers:
                    try:
                        reader.join(4)
                        if reader.is_alive():raise ValueError('child reader not joined')
                    except BaseException as exc:errors.append(exc)
                for bucket in streams:
                    if len(bucket)!=1 or type(bucket[0]) is not bytes or bucket[0]:errors.append(ValueError('child output/reader failure'))
                for pipe in (child.stdin,child.stdout,child.stderr):
                    if pipe is None or not pipe.closed:errors.append(ValueError('pipe close unconfirmed'))
            if body_ok and time.monotonic()-started>20:
                errors.append(ValueError('diagnostic elapsed bound, not preemptive kernel deadline'))
            if body_ok and settled and not errors:
                assert root.parent==parent and root.name.startswith('eq107-crash-') and not root.is_symlink()
                shutil.rmtree(root);assert not root.exists()
            else:
                print('Retained owned crash qualification root:',root)
            # Failed/unknown tests retain the exact owned root, never auto-delete evidence.
            if errors and not active_exception:raise ValueError('owned crash cleanup failed') from errors[0]
        self.assertTrue(body_ok and settled and not errors)

    def test_before_begin(self):self.exercise('before_BEGIN')
    def test_after_insert(self):self.exercise('after_INSERT')
    def test_after_metadata(self):self.exercise('after_metadata')
    def test_after_commit(self):self.exercise('after_COMMIT')

if __name__=='__main__':unittest.main()
