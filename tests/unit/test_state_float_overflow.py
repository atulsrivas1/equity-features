"""BUG004: rehashed structural admission, typed rejection and exact finite resume."""
import json
import unittest
from equity_feature_contracts import ContractError, ErrorCode
from test_state import accumulator, changed, restore, quotes, quote_config
from test_incremental import chunk, certificate

class StateFloatOverflow(unittest.TestCase):
    def test_oversized_finite_hex_exponents_are_typed_and_atomic(self):
        a=accumulator('quotes',quotes(),quote_config());original=a.export_state()
        for value in ('0x1.0000000000000p+1024','-0x1.0000000000000p+1024','0x1.0000000000000p+999999999'):
            with self.subTest(value=value):
                envelope=changed(original,lambda d:d['quotes'].update(bps_sum={'binary64':value}))
                payload=envelope.payload
                with self.assertRaises(ContractError) as caught:restore(a,envelope)
                self.assertEqual(caught.exception.code,ErrorCode.INVALID_SCHEMA)
                self.assertIsInstance(caught.exception.__cause__,OverflowError)
                self.assertEqual(envelope.payload,payload);self.assertEqual(a.export_state(),original)

    def test_nonfinite_and_malformed_hex_remain_typed(self):
        a=accumulator('quotes',quotes(),quote_config());original=a.export_state()
        for value in ('inf','-inf','nan','not-a-hex-float'):
            with self.subTest(value=value):
                with self.assertRaises(ContractError) as caught:restore(a,changed(original,lambda d:d['quotes'].update(bps_sum={'binary64':value})))
                self.assertEqual(caught.exception.code,ErrorCode.INVALID_SCHEMA)
                self.assertEqual(a.export_state(),original)

    def test_valid_nonzero_finite_binary64_roundtrip_and_continuation(self):
        b=quotes();a=accumulator('quotes',b,quote_config());a.update(chunk(b,[0]),start_ordinal=0)
        state=a.export_state();hex_value=json.loads(state.payload)['quotes']['bps_sum']['binary64']
        self.assertGreater(float.fromhex(hex_value),0.)
        resumed=restore(a);self.assertEqual(resumed.export_state(),state)
        self.assertEqual(resumed._state.quotes.bps_sum.hex(),hex_value)
        for target in (a,resumed):target.update(chunk(b,list(range(1,b.row_count))),start_ordinal=1)
        self.assertEqual(a.finalize(certificate(b)),resumed.finalize(certificate(b)))
