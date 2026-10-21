# Supplied clock mathematics

Let the actual regular session be `[O,X)`, supplied scheduled close be `S`, and query cutoff be `C`. All are UTC int64 nanoseconds. Require `O<X<=S` and actual SessionSpec `early_close=(X<S)`. No exchange-calendar lookup or market-status inference occurs.

Compute duration `D=X-O`, elapsed `E=min(max(C-O,0),D)`, remaining `R=D-E`, and fraction `E/D`. Wide exact integer subtraction precedes checked int64 duration/elapsed/remaining publication; overflow raises the canonical typed error. Fraction uses an exact rational followed by one float conversion. Early close is the supplied, identity-checked Boolean. Halts do not subtract regular clock time.

Phase is the supplied disjoint half-open segment containing `C`, or `closed` when none contains it. Each phase is at most one premarket, regular or postmarket segment in that order. Missing optional phases and gaps are explicit schedule definitions. A causal complete calendar-provenance row is required even for `closed`; unavailable evidence never becomes inferred closure. Its finite interval covers all supplied sessions/segments and its hash includes scheduled-close and early-close declarations.

Independent C01 arithmetic uses premarket[0,10), regular[10,30), postmarket[30,40), scheduled40 and early-close true; actual proof scope[0,40), known-at5. At C10 phase is regular and `(E,R,f)=(0,20,0)`; C15 gives `(5,15,0.25)`; C20 gives `(10,10,0.5)`; C30 is postmarket with `(20,0,1)`; C40 is closed with `(20,0,1)`. Proof known exactly at knowledge cutoff is admitted. Unknown or future proof knowledge nulls every output. Independently supplied UTC schedules can represent DST changes without a runtime timezone dependency.

Calendar proof requires original nonnull known-at no later than the requested knowledge cutoff in every availability mode. Explicit reconstruction does not waive that causal proof requirement; requested availability metadata remains intact. Omitted/null and future known-at yield canonical `unknown_availability` and `future_knowledge` reasons respectively, while equality is admitted.

The authored clock fixtures cover these values, literal frozen C01 C/K/E tuples, causal equality, omitted/null/future/equal known-at under explicit reconstruction, original bindings, empty/missing/incomplete evidence, entire-schedule proof bounds, identity/hash/revision errors, explicit early-close equality, supplied UTC offsets and overflow. No execution or numerical acceptance is claimed by source authoring. Status/history, periods and other EF1 producers are outside this slice.
