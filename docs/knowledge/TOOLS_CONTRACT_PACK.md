# Token-saving tools: contract layer pack and quiet batch runner

Both tools are Python 3.12, stdlib only, and live in `tools/`. They have no
unit tests by policy; they were verified by manual runs (see Measured).

## tools/contract_pack.py

```
python tools/contract_pack.py docs/ef3/RELATIVE_RV_CONTRACT_PROPOSAL.json [--out pack.md]
python tools/contract_pack.py docs/ef3/RELATIVE_RV_CONTRACT_PROPOSAL.json --fixture RS07
```

Read-only. Prints a compact markdown pack: contract versions and status,
producers (identity, versions, parameters, policy), output ids grouped by
producer/dtype/unit, roles with kind and nullability, config parameters and
closed vocabularies (lists found under vocabulary-like keys), fixture ids
grouped by kind (result / prefix / refusal) with counts and groups, acceptance
rule kinds found in each fixture body, refusal code per refusal id, the JSON
path of every fixture collection, and an `Unparsed` section listing every
other top-level key with its JSON path.

`--fixture ID` prints the exact fixture subtree as compact JSON, one line per
match (the JSON path goes to stderr). Agents should read one fixture at a time
this way instead of opening the contract.

Guarantees: every value comes from the JSON; every fixture id in a recognised
collection appears in the pack (checked for all contracts below); `--fixture`
output equals the `json.load` subtree (checked for every fixture).

Does not: summarise prose (mathematics, rulings, decisions, quality rules,
coverage_map, notation); those are listed under `Unparsed` with a path to read
on demand. A "fixture collection" is a list of objects that all have `id`, under
a top-level key containing "fixture" or under `fixtures`. Kind comes from the
key name (contains "refusal" or "prefix", else result). Entity ids are only
reported when fixture bodies use keys such as instrument/entity/symbol/benchmark
(`_id`); the EF3 and EF2 contracts use none, and the pack says "none found".
Acceptance kinds are the values of any `acceptance` key in the body; fixtures
with none (for example refusals-by-status) show `(none recorded)`. The pack
cannot say whether a contract is semantically complete.

## tools/run_batch.py

```
python tools/run_batch.py --cmd-file cmds.txt --log-dir logs --workers 4 \
    --timeout 600 --heartbeat-file hb.txt
```

One shell command per line (blank lines and `#` lines skipped). Output of
command N goes to `<log-dir>/000N.log` (first line is the command, last line
the exit status). Nothing is printed while running. At the end one summary
line (`total/pass/fail/timeout`) plus, for each failure or timeout, the log path
and its last 5 lines. Exit code is non-zero if anything failed or timed out. A
timed-out command's process tree is killed. `--heartbeat-file` is rewritten with
`done/total` about every 3 seconds, for peeking only. `--cwd` sets the commands'
working directory.

## Measured (origin/main 778b608 contracts)

| Contract | raw lines / bytes | pack lines / bytes |
|---|---|---|
| ef3 RELATIVE_RV | 6798 / 176722 | 278 / 18198 |
| ef3 ROBUST_PACE | 12982 / 272244 | 371 / 23445 |
| ef3 BREADTH_ADAPTIVE | 30702 / 601323 | 293 / 20146 |
| ef3 EF3_SHARED_AMENDMENT | 640 / 19593 | 109 / 8037 |
| ef2 ICHIMOKU_CHANNELS | 23150 / 470198 | 230 / 17260 |
| ef2 MOMENTUM_TREND | 17863 / 333726 | 183 / 13795 |
| ef2 MONEYFLOW_RETRACEMENT | 5063 / 100737 | 174 / 10676 |
| ef2 PRODUCER_SET_AMENDMENT | 838 / 39088 | 230 / 19626 |

Packs grew versus the first version (which was 69-195 lines) because they now
carry full role contract text, full producer parameters and policy, per-id
attributes, acceptance rule meanings, status mapping and one line per refusal.
Reduction is still 20-100x in lines and 10-30x in bytes for the contract proposals.

Fixture counts found (match the declared `fixture_counts`): RELATIVE_RV 62
result + 3 prefix + 48 refusal; ROBUST_PACE 124 + 48; BREADTH_ADAPTIVE 99 + 62;
ICHIMOKU 74 + 21; MOMENTUM 100 + 23; MONEYFLOW 68 + 38. Amendments hold none.

Checks run (manual): all 770 fixture ids present in their packs; `--fixture`
equals the `json.load` subtree for all 770; `run_batch` with pass, fail and
timeout commands, a missing command file, a bad `--cwd` (log gets an `exit=`
line) and an interrupt (CTRL_BREAK on Windows: summary printed, exit 130; the
children share the console group, so they may show as FAIL rather than
not-finished); `contract_pack` on a missing file and on invalid JSON prints one
line and exits 2.

## Reading only the pack (adapter question check)

For RS07 (RELATIVE_RV), RF38, H01 (ROBUST_PACE), DB01 (BREADTH_ADAPTIVE) and
M01/E01 (MOMENTUM) the pack alone (plus `--fixture` for the body) gave: the
producer and its parameters/policy, the role names and their data kinds and
contract text, the acceptance rule kind and its formula (or, for BREADTH
fixtures, that they assert through `expected` plus `hand_asserted` cells), and
the refusal code with `raised_by` and description.

Still missing from the pack (read the JSON path): mathematics and formulas,
decisions and rulings, per-fixture group descriptions and coverage_map,
BREADTH roles other than as `roles_in_slot_order` plus
`reference_fact_schemas`, ICHIMOKU `numeric_policy.zero_exactness`, fixture
input shapes beyond the `fixture_notation` text, and descriptions cut at 175
characters in the refusal list (marked `[cut,full:--fixture]`).
