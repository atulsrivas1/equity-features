# Context denominator and alignment decisions

EQ-005 resolves routine mathematical choices within the frozen eight-ID scope.
Full prior windows preserve a comparable population and causality; missing sessions
are not compressed. Early-close buckets preserve explicit excluded coverage rather
than creating synthetic zero volume. Relative volume on zero baseline is undefined.
Relative returns require identical endpoints/basis and use arithmetic difference.
Breadth publishes eligible-member values alongside expected-universe coverage;
missing members never mean unchanged or below-SMA. Empty declared universe is
not_applicable. These choices are tested by exact synthetic examples in
tools/verify_context_examples.py. R2 implements calculators; EQ-006 admits timing
and action evidence. No future provider-dependent defaults are assumed here.
