"""Original synthetic mathematical fixtures; no production imports."""
from decimal import Decimal, Context, localcontext, ROUND_HALF_EVEN
from fractions import Fraction
from math import isqrt
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).parent
CASES=[
 ('exact_lower_zero',[1,7],0,Fraction(4,3)),
 ('exact_position_zero',[7,1],0,Fraction(1)),
 ('flat',[7,7,7],0,Fraction(2)),
 ('negative_lower',[1,9],0,Fraction(2)),
 ('negative_position',[9,9,1],0,Fraction(1)),
 ('position_above_one',[1,1,9],0,Fraction(1)),
 ('wide_offset',[2**60-1,2**60,2**60+1],0,Fraction(2)),
 ('scale18',[2**60-1,2**60,2**60+1],18,Fraction(2)),
 ('int64_limit',[2**63-3,2**63-2,2**63-1],0,Fraction(2)),
 ('near_lower_zero_positive',[1,7],0,Fraction(999999,750000)),
 ('near_lower_zero_negative',[1,7],0,Fraction(1000000,749999)),
 ('small_multiplier',[1,7],18,Fraction(1,1000000)),
 ('large_multiplier',[1,7],0,Fraction(1000000)),
]
def f(x):return str(x.numerator)+'/'+str(x.denominator)
def dec(x):return Decimal(x.numerator)/Decimal(x.denominator)
results=[]
with localcontext(Context(prec=240,rounding=ROUND_HALF_EVEN,Emin=-999999,Emax=999999)):
 for label,prices,scale,k in CASES:
  n=len(prices);values=[Fraction(x,10**scale) for x in prices]
  # Independent pairwise sum identity; no prepared/production mean-square path.
  mu=sum(values,Fraction())/n
  variance=sum(((a-b)**2 for a in values for b in values),Fraction())/(2*n*n)
  radius2=k*k*variance
  rn,rd=isqrt(radius2.numerator),isqrt(radius2.denominator)
  radius_exact=Fraction(rn,rd) if rn*rn==radius2.numerator and rd*rd==radius2.denominator else None
  radius=dec(radius_exact) if radius_exact is not None else dec(radius2).sqrt()
  if radius_exact is not None:
   middle=mu;upper=mu+radius_exact;lower=mu-radius_exact
   width=2*radius_exact/mu
   position=None if variance==0 else (values[-1]-(mu-radius_exact))/(2*radius_exact)
   exact=[middle,upper,lower,width,position]
   outputs=[None if v is None else (0.0 if v==0 else float(dec(v))) for v in exact]
   exact_labels=[None if v is None else f(v) for v in exact]
  else:
   # Independent direct lower/normalized-position evaluation at 240digits;
   # does not share production's planned 120digit rationalized expression.
   m=dec(mu); c=dec(values[-1])
   outputs=[float(m),float(m+radius),float(m-radius),float(2*radius/m),float((c-(m-radius))/(2*radius))]
   exact_labels=None
  results.append({'id':label,'prices':prices,'scale':scale,'period':n,'k':f(k),'mean':f(mu),'variance':f(variance),'radius_squared':f(radius2),'exact_outputs':exact_labels,'outputs_middle_upper_lower_width_position':outputs})
byid={x['id']:x for x in results}
assert byid['exact_lower_zero']['outputs_middle_upper_lower_width_position'][2]==0
assert byid['exact_position_zero']['outputs_middle_upper_lower_width_position'][4]==0
assert byid['negative_lower']['outputs_middle_upper_lower_width_position'][2]<0
assert byid['negative_position']['outputs_middle_upper_lower_width_position'][4]<0
assert byid['position_above_one']['outputs_middle_upper_lower_width_position'][4]>1
w=byid['wide_offset']['outputs_middle_upper_lower_width_position'];assert w[1]==w[2] and w[3]>0
assert byid['flat']['outputs_middle_upper_lower_width_position'][3:]==[0.0,None]
packet={'scope':'Original independent mathematical goldens; not installed, performance or release qualification.','generator_sha256_lf':hashlib.sha256(Path(__file__).read_bytes().replace(b'\r\n',b'\n')).hexdigest(),'oracle':'Independent exact pairwise variance; exact rational-square paths, otherwise Decimal240 direct expressions.','cases':results}
out=ROOT/'GOLDENS.json';out.write_text(json.dumps(packet,indent=2)+'\n',encoding='utf-8',newline='\n');print('13 original mathematical fixtures; exactzero/negative/outside/largeoffset assertions passed. SHA256',hashlib.sha256(out.read_bytes()).hexdigest())
