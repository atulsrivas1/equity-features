# Separate market bounds from knowledge and reconstruction

EQ-006 chooses inclusive known-at cutoff and half-open ordinary market event bounds,
preserving EQ-002 auction and completed-interval exceptions. Causal mode requires
C<=E and K<=E for supplied decision time E and explicit knowledge evidence.
This admits delayed EOD knowledge only at a correspondingly later evaluation.
Retrospective reconstruction is a distinct
identity and never grants causal availability. Split adjustments conserve notional
only with a compatible reciprocal quantity basis; dividend reinvestment requires
an explicit supplied policy. No current reference, implicit factor, gap filling or
automatic adjustment engine is introduced. See TIMING_ADJUSTMENT_POLICY.md and
tools/verify_timing_examples.py. Production timing enforcement follows in contracts;
provider and real historical admission are separate later qualifications.
