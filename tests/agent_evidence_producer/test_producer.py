"""Actual public producer parity, separate from declaration-only methods."""
from pathlib import Path
import runpy
import unittest
import equity_feature_agent_evidence as a


class ProducerTests(unittest.TestCase):
    def test_actual_public_producer_and_retained_receipt(self):
        path = Path(__file__).resolve().parents[2] / 'examples/agent_event_producer.py'
        example = runpy.run_path(str(path))
        event, receipt = example['demonstrate']()
        self.assertEqual(event.kind, a.EventKind.FEATURE_READ)
        self.assertTrue(a.verify_payload(event.subject.receipt, receipt).retained_matched)
        with self.assertRaises(a.AgentEvidenceError) as c:
            a.verify_payload(event.subject.receipt, receipt[:-1] + b' ')
        self.assertEqual(c.exception.code, 'inconsistent_content')


if __name__ == '__main__': unittest.main()
