"""No implicit output/state support or change to the accepted core catalog."""
from dataclasses import FrozenInstanceError
import unittest
from equity_feature_contracts import ContractError, ErrorCode, Status, builtin_registry
from equity_features_intraday import (
    compute_intraday, describe_intraday, intraday_catalog_digest, require_intraday_capability,
)
from test_context import context, config


class CapabilityTests(unittest.TestCase):
    def test_own_eight_sorted_ids_do_not_extend_core_registry(self):
        before=builtin_registry().to_json()
        entries=describe_intraday()
        self.assertEqual(len(entries),8)
        self.assertEqual([e.feature_id for e in entries],sorted(e.feature_id for e in entries))
        self.assertEqual(builtin_registry().to_json(),before)
        self.assertEqual(len(builtin_registry().list_features()),40)
        self.assertEqual(len(intraday_catalog_digest()),64)
        self.assertEqual(intraday_catalog_digest(),intraday_catalog_digest())

    def test_exact_eight_batch_and_no_state_capabilities_claimed(self):
        for entry in describe_intraday():
            for cap in ('batch','update','restore','merge','replay'):
                if cap == 'batch':
                    require_intraday_capability(entry.feature_id,cap)
                    self.assertTrue(entry.supports_batch)
                    continue
                with self.subTest(feature=entry.feature_id,cap=cap),self.assertRaises(ContractError) as caught:
                    require_intraday_capability(entry.feature_id,cap)
                self.assertEqual(caught.exception.code,ErrorCode.UNSUPPORTED_CAPABILITY)
        with self.assertRaises(FrozenInstanceError):describe_intraday()[0].supports_batch=True

    def test_all_batch_outputs_admit_missing_input_and_unknown_is_rejected(self):
        result=compute_intraday(None,context(),config(),features=tuple(e.feature_id for e in describe_intraday()))
        self.assertEqual(len(result.values),8)
        self.assertTrue(all(row.status==Status.MISSING_INPUT for row in result.quality))
        with self.assertRaises(ContractError) as caught:
            compute_intraday(None,context(),config(),features=('invented',))
        self.assertEqual(caught.exception.code,ErrorCode.UNKNOWN_FEATURE)


if __name__=='__main__':unittest.main()
