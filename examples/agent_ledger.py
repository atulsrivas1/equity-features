"""Small synthetic local ledger with an externally retained terminal checkpoint."""
from pathlib import Path
import tempfile
import equity_feature_agent_evidence as a
import equity_feature_agent_ledger as l

def demonstrate() -> l.Checkpoint:
    missing = a.TimeDeclaration(None, None, None)
    event = a.EventRecord('demo:ledger', 1, 'demo:request',
                          a.ActorDeclaration(None, a.ActorKind.UNKNOWN), missing, missing,
                          '0'*64, a.RequestSubject('r1', 'synthetic research', None))
    with tempfile.TemporaryDirectory(prefix='eq107-example-') as folder:
        root=Path(folder).resolve()
        assert root.parent == Path(tempfile.gettempdir()).resolve()
        assert root.name.startswith('eq107-example-')
        path=str(root/'events.sqlite')
        store=l.Ledger.create(path,'demo:ledger')
        try: terminal=store.append(event,expected=store.head())
        finally:store.close()
        reopened=l.Ledger.open(path)
        try:
            assert reopened.verify(expected=terminal).anchor_status is l.AnchorStatus.MATCHED_TERMINAL
            assert reopened.reconcile(event,expected_before=l.Checkpoint('demo:ledger',0,'0'*64)).status is l.ReconciliationStatus.FOUND_EXACT
        finally:reopened.close()
    return terminal

if __name__=='__main__':demonstrate()
