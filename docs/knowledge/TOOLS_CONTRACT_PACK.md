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

## Measured (tools-pack branch, origin/main 778b608)

| Contract | raw lines / bytes | pack lines / bytes |
|---|---|---|
| ef3 RELATIVE_RV | 6798 / 176722 | 134 / 8282 |
| ef3 ROBUST_PACE | 12982 / 272244 | 195 / 10954 |
| ef3 BREADTH_ADAPTIVE | 30702 / 601323 | 144 / 7728 |
| ef3 EF3_SHARED_AMENDMENT | 640 / 19593 | 69 / 5134 |
| ef2 ICHIMOKU_CHANNELS | 23150 / 470198 | 127 / 8457 |
| ef2 MOMENTUM_TREND | 17863 / 333726 | 92 / 5521 |
| ef2 MONEYFLOW_RETRACEMENT | 5063 / 100737 | 98 / 5286 |
| ef2 PRODUCER_SET_AMENDMENT | 838 / 39088 | 76 / 7372 |

Fixture counts found (matches the declared `fixture_counts` in each file):
RELATIVE_RV 62 result + 3 prefix + 48 refusal; ROBUST_PACE 124 result + 48
refusal; BREADTH_ADAPTIVE 99 result + 62 refusal; ICHIMOKU 74 + 21; MOMENTUM
100 + 23; MONEYFLOW 68 + 38 (money-flow and retracement together). The two
amendment files hold no fixtures.

Checks run: all 770 fixture ids present in the packs (0 missing); `--fixture`
round-trip equal to the `json.load` subtree for all 770; `run_batch` on 7
commands (3 pass, 2 fail, 2 timeout) printed one summary, correct logs, exit 1,
and heartbeat `7/7`.
