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

EF3 total before the Sonnet E workers rework: 3,839k. Median Total per unit including fix rounds (excluding the failed run and the amendment): about 436k; median build-plus-review without fix rounds: about 429k (retrospective section 8 uses 429k).


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


Added at EF4 close (cumulative context k from the EF4 coordinator's per-agent usage lines, not auditable from the repo; coordinator not measured). Bases: 'first line' = the first usage line of the agent; 'total' = all unique usage lines including resumed follow-ups; 'Review total' includes follow-ups. The per-unit build-plus-review median (about 439k) uses Build first line plus Review first line over the 12 I/O, library and workers units.

| Release | Unit | Model | Build k (first line) | Build total k | Review total k | Review first line k |
|---|---|---|---|---|---|---|
| EF4 | G contract | Sonnet | 328 | 1067 | - | - |
| EF4 | G I/O | Haiku | 319 | 1002 | 318 | 156 |
| EF4 | G library | Sonnet | 320 | 1630 | 487 | 242 |
| EF4 | G workers | Sonnet | 269 | 552 | 146 | 146 |
| EF4 | H contract | Sonnet | 270 | 961 | 363 | 165 |
| EF4 | H I/O | Haiku | 285 | 582 | 145 | 145 |
| EF4 | H library | Sonnet | 339 | 1399 | 429 | 211 |
| EF4 | H workers | Sonnet | 208 | 423 | 105 | 105 |
| EF4 | I1 contract | Sonnet | 412 | 1417 | 340 | 160 |
| EF4 | I1 I/O | Haiku | 238 | 479 | 141 | 141 |
| EF4 | I1 library | Sonnet | 293 | 898 | 338 | 165 |
| EF4 | I1 workers | Sonnet | 203 | 407 | 112 | 112 |
| EF4 | I2 contract | Sonnet | - | - | 369 (review only) | 177 |
| EF4 | I2 I/O | Haiku | 321 | 2477 | 271 | 127 |
| EF4 | I2 library | Sonnet | 392 | 1214 | 624 | 308 |
| EF4 | I2 workers | Sonnet | 242 | 486 | 138 | 138 |
| EF4 | Vendored fixture expanders | Haiku | 86 | 172 | - | - |

EF4 total from these rows: 19,492k (build totals 15,166k plus review totals 4,326k), about 19.5M. The source notes state 19,913k (about 19.9M); 421k is unattributed. The rows are the basis used in the retrospective. EF3 for comparison: about 5.3M.
