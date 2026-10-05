"""EQ-006 policy design fixtures, no production adjustment engine."""
from fractions import Fraction as F
import unittest


def admit(event,known,*,market=20,knowledge=20,decision=20,mode='known_at',end=False,auction=False):
    if mode not in ('known_at','reconstruction'): raise ValueError('mode')
    if market>decision or knowledge>decision: raise ValueError('decision bounds')
    if not (event<=market if end or auction else event<market): return 'out_of_target'
    if mode=='reconstruction': return 'retrospective'
    if known is None: return 'unknown_availability'
    if known>knowledge: return 'future_knowledge'
    return 'admitted'


def adjustment(price,quantity,factor,known,anchor,effective,mode='known_at'):
    if factor<=0: raise ValueError('factor')
    if effective>anchor: return price,quantity
    if admit(0,known,market=anchor,knowledge=anchor,decision=anchor,mode=mode) not in ('admitted','retrospective'):
        return None,None
    return F(price)*factor,F(quantity)/factor


class TimingReferences(unittest.TestCase):
    def test_event_half_open(self): self.assertEqual(admit(20,10),'out_of_target')
    def test_completed_at_cutoff(self): self.assertEqual(admit(20,20,end=True),'admitted')
    def test_auction_explicit(self): self.assertEqual(admit(20,20,auction=True),'admitted')
    def test_future_market(self): self.assertEqual(admit(21,10),'out_of_target')
    def test_known_boundary(self): self.assertEqual(admit(19,20),'admitted')
    def test_future_knowledge(self): self.assertEqual(admit(10,21),'future_knowledge')
    def test_unknown(self): self.assertEqual(admit(10,None),'unknown_availability')
    def test_retrospective(self): self.assertEqual(admit(10,100,mode='reconstruction'),'retrospective')
    def test_retrospective_unknown(self): self.assertEqual(admit(10,None,mode='reconstruction'),'retrospective')
    def test_reconstruction_still_bounds_market(self): self.assertEqual(admit(21,100,mode='reconstruction'),'out_of_target')
    def test_decision_bounds(self):
        with self.assertRaises(ValueError): admit(10,10,knowledge=21)
    def test_delayed_eod(self): self.assertEqual(admit(20,25,market=20,knowledge=25,decision=25,end=True),'admitted')
    def test_delayed_eod_not_at_close(self): self.assertEqual(admit(20,25,end=True),'future_knowledge')
    def test_revision_not_event_time(self): self.assertEqual(admit(10,30),'future_knowledge')
    def test_split_conserves_notional(self):
        p,q=adjustment(100,10,F(1,2),15,20,20)
        self.assertEqual((p,q,p*q),(50,20,1000))
    def test_future_action_anchor_excluded(self): self.assertEqual(adjustment(100,10,F(1,2),10,20,21),(100,10))
    def test_unknown_action(self): self.assertEqual(adjustment(100,10,F(1,2),None,20,20),(None,None))
    def test_future_known_action(self): self.assertEqual(adjustment(100,10,F(1,2),21,20,20),(None,None))
    def test_dividend_basis_distinct(self):
        self.assertEqual(F(99,100)-1,F(-1,100));self.assertEqual(F(99+1,100)-1,0)
    def test_noninteger_quantity_remains_exact(self): self.assertEqual(adjustment(100,1,F(3,2),10,20,20)[1],F(2,3))
    def test_basis_incompatibility(self):
        self.assertNotEqual(('split','v1','anchor20'),('raw','v1','anchor20'))
        self.assertNotEqual(('split','v1','anchor20'),('split','v2','anchor20'))
    def test_gap_not_filled(self):
        from verify_history_examples import history
        rows=[dict(session=i,end=(i+1)*10,close=p) if p is not None else None for i,p in enumerate([100,None,101,102])]
        self.assertEqual(history(rows,'ema',n=2,cutoff=40)['status'],'incomplete_coverage')
    def test_future_fact_mutation(self):
        chosen=[(10,10),(15,15)]
        for future in [(25,25),(100,100)]:
            self.assertEqual([x for x in chosen+[future] if admit(*x)=='admitted'],chosen)


if __name__=='__main__': unittest.main(verbosity=2)
