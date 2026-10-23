# Token ledger (subagent usage per unit)

Source: usage lines on agent completion (cumulative context tokens, tool uses, minutes). Relative measure only; not billed tokens or price. Coordinator tokens are not captured here. Append one row per unit per release.

| Release | Unit | Build model | Build k | Review k | Fix/merge k | Total k | Build tools | Build min | Review verdict |
|---|---|---|---|---|---|---|---|---|---|
| EF3 | D I/O | Haiku | 247 | 144 | 3 | 394 | 56 | 8 | approve with fixes |
| EF3 | D workers | Haiku | 270 | 113 | 7 | 390 | 81 | 26 | approve |
| EF3 | E library | Sonnet | 358 | 259 | 1 | 618 | 86 | 19 | approve |
| EF3 | E I/O | Haiku | 319 | 164 | 21 | 504 | 65 | 13 | approve with fixes |
| EF3 | F library | Sonnet | 372 | 219 | 1 | 592 | 72 | 21 | approve |
| EF3 | F I/O | Haiku | 292 | 137 | 7 | 436 | 60 | 10 | block (hash), fixed |
| EF3 | F workers | Haiku | 215 | 195 | 8 | 418 | 76 | 44 | approve with fixes |
| EF3 | Shared amendment | Sonnet | 123 | 86 | 2 | 211 | 25 | 3 | approve with fixes |
| EF3 | E workers (Haiku, failed) | Haiku | 276 | - | - | 276 | 67 | 42 | not reviewed; reworked by Sonnet |

EF3 total before the Sonnet E workers rework: 3,839k. Median build-plus-review unit (excluding the failed run and the amendment): about 436k.


Added at EF3 close (cumulative context k; coordinator not measured):

| Release | Unit | Model | Build k | Review k | Total k |
|---|---|---|---|---|---|
| EF3 | E workers rework | Sonnet | 145 | 133 | 278 |
| EF3 | Tools (contract pack, quiet batch) | Sonnet | 172 | 96 + 105 (+105 re-check) | 478 |
| EF3 | Windows qualification | Sonnet | 131 | 109 | 240 |
| EF3 | Evidence package | Sonnet | 110 | 90 | 200 |
| EF3 | Browser demo preparation | Sonnet | 90 | - | 90 |
| EF3 | Retrospective and token-doc reviews | Sonnet/Haiku | - | 74 + 71 | 145 |

EF3 total with these rows: about 5.3M subagent tokens (3,839k in the first table plus 1,431k here).
