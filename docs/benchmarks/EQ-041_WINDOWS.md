# EQ041 measured Windows baseline

October6,2026; [raw samples/provenance](EQ-041_WINDOWS.json), [methodology](../BENCHMARKS.md), [plan](../stories/EQ-041_PLAN.md). Measured clean source `efa8af7101e571a66a22aa9892ba9aa96b590075`; this later results publication changes only documentation, not harness/runtime/test/build bytes. Canonical LF harness SHA256 `a481f45163d3a0061de24920357a168a57d08690aa47394b0e7e288177b12579`.

Actual published a4Windows wheels were independently installed in a dedicated environment with pinnedNumPy2.2.6/PyArrow20.0.0, CPython3.12.10, Windows11/AMD64. CPU identifier Intel64Family6Model85Stepping4/GenuineIntel,96logicalCPUs; no exclusive allocation/affinity claim. Children requested four backend environment budgets1, reported ArrowCPU/I/Ocounts1; other effective pools not independently introspected. Seed41001/K8/chunks128,1024;3repeated full checked calls after untimed golden/parity checks. Normal garbage collection and wall scheduling included. Parent cases launched serially; machine background load was not controlled.

| Supplied trades | Aggregate median rows/sec | TopK median rows/sec | Whole-child native peak MiB | Arrow visible bytes | NumPy array+mask bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| 128 uniform | 112006 | 79751 | 49.79 | 7330 | 9472 |
| 16384 uniform | 138273 | 89603 | 71.14 | 973978 | 1343488 |
| 16384 skew | 127748 | 87344 | 70.97 | 973978 | 1343488 |

| Supplied trades | Chunk128 median rows/sec | Chunk1024 median rows/sec | Governed history rows | SMA/EMA median calls/sec | Return median calls/sec |
| --- | ---: | ---: | ---: | ---: | ---: |
| 128 uniform | 64565 | 65203 | 128 | 418.9 | 478.9 |
| 16384 uniform | 86569 | 86984 | 512 | 114.0 | 133.8 |
| 16384 skew | 81654 | 83961 | 512 | 107.5 | 128.3 |

Every raw duration (min/median/max), fixture SHA256, construction/chunk/conversion timing, independent goldens and process initial/fixture/final peaks is retained in the JSON. Historyperiod20/S0EMAanchor/returnhorizon19 are separate from tradeN. Conversion roundtrips and NumPy ownership mutation check pass before timing; exposed buffer bytes exclude Python objects/hidden temporaries.

These are observations, not thresholds, speedup claims, retained-state bounds or platform comparisons. Process high-water includes interpreter/imports/input/reference/chunks/conversions/result allocations; subtraction cannot isolate calculator allocation. The current checked Python backend and source admission are measured together. Other39IDs, real distributions, cold starts/concurrent production/workers/providers are not certified by these three cases. Fullfreshpair/CI/mainartifact/separate-review gates remain required for EQ041Done; EQ042 measures retained state separately.
