"""Fixed reviewed qualification child, never an installed public fault API."""
import json
import os
from pathlib import Path
import sys
import time

def publish(path, obj, cap):
    raw=json.dumps(obj,sort_keys=True,separators=(',',':')).encode('ascii')
    if len(raw)>cap or path.exists():raise ValueError('fixed witness bound')
    temporary=path.with_suffix('.tmp')
    with temporary.open('xb') as stream:stream.write(raw)
    temporary.rename(path)

def main():
    if not sys.flags.isolated or len(sys.argv)!=3:raise ValueError('fixed isolated entry')
    root=Path(sys.argv[1]);mode=sys.argv[2]
    if not root.is_absolute() or root.is_symlink() or not root.is_dir() or len(str(root))>4096:raise ValueError('owned root')
    if mode not in ('before_BEGIN','after_INSERT','after_metadata','after_COMMIT'):raise ValueError('fixed mode')
    publish(root/'ready.json',{'pid':os.getpid(),'isolated':True},256)
    until=time.monotonic()+3
    while not (root/'GO').is_file():
        if time.monotonic()>=until:raise ValueError('fixed GO timeout')
        time.sleep(.005)
    if (root/'GO').read_bytes()!=b'go':raise ValueError('fixed GO')
    # Product imports occur after the parent has bound the actual entry identity.
    import equity_feature_agent_evidence as a
    import equity_feature_agent_ledger as l
    for module in (a,l):
        if 'site-packages' not in Path(module.__file__).resolve().parts:raise ValueError('installed source required')
    raw=(root/'proposal.json').read_bytes()
    if not raw or len(raw)>16384:raise ValueError('fixed proposal bound')
    proposal=a.decode_event(raw)
    if proposal.chain_id!='demo:chain' or proposal.sequence!=13 or proposal.event_id!='demo:new_model':raise ValueError('fixed proposal')
    store=l.Ledger.open(str(root/'events.sqlite'));base=store.head()
    if base.sequence!=12 or proposal.previous_hash!=base.head_hash:raise ValueError('fixed initial head')
    connection=store._conn
    def cut(boundary):
        witness={'mode':boundary,'pid':os.getpid(),'rows':connection.execute('SELECT count(*) FROM events').fetchone()[0],
                 'metadata':connection.execute('SELECT event_count FROM metadata').fetchone()[0],
                 'in_transaction':connection.in_transaction}
        publish(root/'phase.json',witness,1024)
        os._exit(91)
    class Proxy:
        def __getattr__(self,name):return getattr(connection,name)
        def execute(self,sql,*args):
            result=connection.execute(sql,*args)
            if mode=='after_INSERT' and sql=='INSERT INTO events (sequence,event_id,kind,previous_hash,digest,canonical,byte_length) VALUES (?,?,?,?,?,?,?)':cut(mode)
            if mode=='after_metadata' and sql=='UPDATE metadata SET event_count=?,head_hash=?,canonical_bytes=? WHERE singleton=1':cut(mode)
            if mode=='after_COMMIT' and sql=='COMMIT':cut(mode)
            return result
    store._conn=Proxy()
    if mode=='before_BEGIN':cut(mode)
    store.append(proposal,expected=base)
    raise ValueError('fixed cut point not reached')

if __name__=='__main__':main()
