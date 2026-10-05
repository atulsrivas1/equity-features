"""Exact synthetic EQ-005 design references, not production calculators."""
from fractions import Fraction as F
import unittest


def baseline(grid, target, n=3):
    if type(n) is not int or n<1: raise ValueError('window')
    if grid is None: return 'missing_input', None
    if target<n: return 'insufficient_history', None
    values=grid[target-n:target]
    if len(values)!=n or any(x is None for x in values):
        return 'incomplete_coverage', None
    if any(type(x) is not int or x<0 or x>2**63-1 for x in values):
        raise ValueError('volume')
    return 'available',F(sum(values),n)


def ratio(v,b):
    if v is None or b is None: return 'missing_input',None
    if v<0 or b<0: raise ValueError('volume')
    return ('not_applicable',None) if b==0 else ('available',F(v)/b)


def bucket(volumes,ends,start=0,end=10):
    if start>=end or len(volumes)!=len(ends): raise ValueError('grid')
    admitted=[v if close>=end else None for v,close in zip(volumes,ends)]
    return baseline(admitted,len(admitted),len(admitted)),sum(v is not None for v in admitted)


def relative(a,b,identity_a,identity_b,membership=True):
    if identity_a!=identity_b: raise ValueError('alignment')
    if a is None or b is None or not membership: return 'missing_input',None
    return 'available',a-b


def breadth(universe,values,mode='direction'):
    if universe is None: return 'missing_input',None
    if len(set(universe))!=len(universe) or set(values)-set(universe):
        raise ValueError('members')
    if not universe: return 'not_applicable',None
    admitted=[values[x] for x in universe if values.get(x) is not None]
    e,m=len(admitted),len(universe)
    status='available' if e==m else 'incomplete_coverage'
    if not e: return status,dict(value=None,eligible=0,expected=m,coverage=F(0))
    if mode=='direction':
        value=tuple(sum(v>0 if k==0 else v<0 if k==1 else v==0 for v in admitted) for k in range(3))
    else: value=F(sum(close>sma for close,sma in admitted),e)
    return status,dict(value=value,eligible=e,expected=m,coverage=F(e,m))


class ContextReferences(unittest.TestCase):
    def test_daily_hand_calculated(self): self.assertEqual(baseline([100,200,300,500],3),('available',F(200)))
    def test_target_exclusion(self): self.assertEqual(baseline([100,200,300,9000],3)[1],200)
    def test_future_mutation(self): self.assertEqual(baseline([100,200,300,500,99999],3)[1],200)
    def test_relative_volume(self): self.assertEqual(ratio(500,200),('available',F(5,2)))
    def test_zero_baseline(self): self.assertEqual(baseline([0,0,0],3),('available',0))
    def test_zero_denominator(self): self.assertEqual(ratio(0,0),('not_applicable',None))
    def test_missing_dataset(self): self.assertEqual(baseline(None,3)[0],'missing_input')
    def test_empty_dataset(self): self.assertEqual(baseline([],0)[0],'insufficient_history')
    def test_missing_slot(self): self.assertEqual(baseline([100,None,300],3)[0],'incomplete_coverage')
    def test_negative_volume(self):
        with self.assertRaises(ValueError): baseline([100,-1,300],3)
    def test_bool_volume(self):
        with self.assertRaises(ValueError): baseline([100,True,300],3)
    def test_wide_sum(self): self.assertEqual(baseline([2**63-1]*3,3)[1],2**63-1)
    def test_bucket(self): self.assertEqual(bucket([10,20,30],[10,10,10]),(('available',F(20)),3))
    def test_early_close(self): self.assertEqual(bucket([10,20,30],[10,5,10]),(('incomplete_coverage',None),2))
    def test_bucket_bounds(self):
        with self.assertRaises(ValueError): bucket([1],[10],10,10)
    def test_relative_difference(self): self.assertEqual(relative(F(1,10),F(1,20),'same','same')[1],F(1,20))
    def test_alignment_dimensions(self):
        identity=('s0','s1',1,60,'completed','USD','split-v1','known_at')
        for i in range(len(identity)):
            changed=list(identity);changed[i]='different'
            with self.subTest(i=i),self.assertRaises(ValueError): relative(F(0),F(0),identity,tuple(changed))
    def test_missing_sector(self): self.assertEqual(relative(1,0,'same','same',False)[0],'missing_input')
    def test_partial_direction(self):
        self.assertEqual(breadth('abcd',dict(a=F(1,10),b=F(-1,20),c=0)),('incomplete_coverage',dict(value=(1,1,1),eligible=3,expected=4,coverage=F(3,4))))
    def test_complete_direction(self): self.assertEqual(breadth('abc',dict(a=1,b=-1,c=0))[0],'available')
    def test_above_strict_equality(self):
        self.assertEqual(breadth('abcd',dict(a=(11,10),b=(9,10),c=(10,10)),mode='above')[1]['value'],F(1,3))
    def test_no_eligible(self): self.assertEqual(breadth('abc',{})[1],dict(value=None,eligible=0,expected=3,coverage=F(0)))
    def test_empty_universe(self): self.assertEqual(breadth([],{}),('not_applicable',None))
    def test_absent_universe(self): self.assertEqual(breadth(None,{}),('missing_input',None))
    def test_duplicate_members(self):
        with self.assertRaises(ValueError): breadth('aa',dict(a=1))
    def test_extra_members(self):
        with self.assertRaises(ValueError): breadth('a',dict(a=1,b=2))


if __name__=='__main__': unittest.main(verbosity=2)
