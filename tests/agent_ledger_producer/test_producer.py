"""Actual public producer retains original config/input/result/quality/source/receipt."""
from pathlib import Path
import runpy
import unittest
import equity_feature_agent_evidence as a

class ProducerTests(unittest.TestCase):
    def test_actual_public_producer_ledger_roundtrip(self):
        root=Path(__file__).resolve().parents[2]
        sample=runpy.run_path(str(root/'examples/agent_ledger_producer.py'))
        terminal,original=sample['demonstrate']()
        self.assertEqual(terminal.sequence,4)
        accepted=runpy.run_path(str(root/'examples/agent_event_producer.py'))
        event,receipt=accepted['demonstrate']()
        self.assertEqual(receipt,original[3]);self.assertEqual(event.chain_id,terminal.chain_id)
        self.assertEqual(a.event_digest(event),terminal.head_hash)

if __name__=='__main__':unittest.main()
