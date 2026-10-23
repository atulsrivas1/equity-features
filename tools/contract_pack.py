#!/usr/bin/env python3
"""Compact markdown "layer pack" for a frozen contract JSON (read-only, stdlib).

Usage:
  python tools/contract_pack.py CONTRACT.json [--out FILE.md]
  python tools/contract_pack.py CONTRACT.json --fixture ID

Everything printed is derived from the JSON itself. Structure that is not
recognised is listed under "Unparsed" with its JSON path; nothing is invented.
--fixture prints the exact fixture subtree(s) as compact JSON, one per line
(the JSON path goes to stderr).
"""
import argparse
import json
import os
import re
import sys
import textwrap
from collections import OrderedDict, defaultdict

VERSION_KEY = re.compile(r"version|identity|^package$|policy_label|^status$|^state$")
VOCAB_KEY = re.compile(r"vocab|_values$|^values$|reasons|precedence|enum|codes|^direction")
ID_KEY = re.compile(r"^(instrument|entity|symbol|benchmark)(_id)?s?$|_(instrument|entity|symbol|benchmark)_id$")


def jpath(parent, key):
    if isinstance(key, int):
        return f"{parent}[{key}]"
    return f"{parent}.{key}" if re.fullmatch(r"\w+", key) else f'{parent}["{key}"]'


def compact(o, limit=0):
    s = json.dumps(o, separators=(",", ":"), ensure_ascii=False)
    if limit and len(s) > limit:
        s = s[: limit - 3] + "..."
    return s


def is_scalar(v):
    return v is None or isinstance(v, (str, int, float, bool))


def one(s, n=100):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 3] + "..."


def is_coll(v):
    return isinstance(v, list) and bool(v) and all(isinstance(x, dict) and "id" in x for x in v)


def find_fixture_collections(doc):
    """Lists of dicts that all carry 'id', under a key naming fixtures."""
    found = []
    for k, v in doc.items():
        if "fixture" in k.lower() and is_coll(v):
            found.append((jpath("$", k), k, v))
        elif k == "fixtures" and isinstance(v, dict):
            for kk, vv in v.items():
                if is_coll(vv):
                    found.append((jpath(jpath("$", k), kk), kk, vv))
    return found


def kind_of(name):
    n = name.lower()
    if "refusal" in n:
        return "refusal"
    if "prefix" in n:
        return "prefix"
    return "result"


def collect(o, key, out):
    """Collect every scalar stored under dict key `key` anywhere in o."""
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key and is_scalar(v):
                out.append(v)
            collect(v, key, out)
    elif isinstance(o, list):
        for v in o:
            collect(v, key, out)


def entity_values(o, out):
    if isinstance(o, dict):
        for k, v in o.items():
            if ID_KEY.search(k) and isinstance(v, str):
                out[k].add(v)
            entity_values(v, out)
    elif isinstance(o, list):
        for v in o:
            entity_values(v, out)


def wrap_ids(ids, indent="  "):
    return textwrap.wrap(" ".join(ids), 112, initial_indent=indent, subsequent_indent=indent)


def labelled(label, ids):
    """'- label (n): ids' wrapped with a hanging indent (one line when short)."""
    return textwrap.wrap(f"- {label} ({len(ids)}): " + " ".join(ids), 118, subsequent_indent="    ")


def refusal_code(f):
    for k in ("error_code", "code"):
        if k in f:
            return f[k]
    exp = f.get("expected")
    if isinstance(exp, dict):
        for k in ("error_code", "code"):
            if k in exp:
                return exp[k]
    return "(no code field)"


def build_pack(doc, name):
    L = [f"# Layer pack: {name}"]
    if not isinstance(doc, dict):
        L.append(f"Top-level JSON is {type(doc).__name__}, not an object; nothing parsed.")
        return "\n".join(L) + "\n"
    top = doc
    used = set()
    L.append("Derived mechanically from the JSON; pointers are JSON paths. Read one fixture with"
             " `--fixture ID`.")
    L += ["", "## Contract"]
    for k, v in top.items():
        if is_scalar(v) and (VERSION_KEY.search(k) or k in ("story", "frozen_contract_ref")):
            L.append(f"- {k}: {one(v, 140)}")
            used.add(k)

    # producers
    prods = []
    prod = top.get("producers")
    if isinstance(prod, dict):
        prods = [(k, v) for k, v in prod.items() if isinstance(v, dict)]
        used.add("producers")
    elif isinstance(prod, list):
        prods = [(str(v.get("producer") or v.get("name") or i), v) for i, v in enumerate(prod) if isinstance(v, dict)]
        used.add("producers")
    for k, v in top.items():
        if k.endswith("_producer") and isinstance(v, dict):
            prods.append((k, v))
            used.add(k)
    if prods:
        L += ["", "## Producers"]
        for pname, p in prods:
            vs = [f"{k}={one(v, 60)}" for k, v in p.items() if is_scalar(v) and VERSION_KEY.search(k)]
            L.append(f"- {pname}: " + "; ".join(vs))
            for k, v in p.items():
                if k in ("parameters", "params", "policy") and isinstance(v, (dict, list)):
                    L.append(f"  - {k}: {compact(v, 420)}")

    # output ids: lists of dicts with id + dtype
    hdr_lists = [(k, v) for k, v in top.items() if is_coll(v) and all("dtype" in x for x in v)]
    if hdr_lists:
        L += ["", "## Output ids (producer | dtype | unit)"]
        for k, hl in hdr_lists:
            used.add(k)
            L.append(f"{jpath('$', k)} ({len(hl)})")
            groups = OrderedDict()
            for h in hl:
                key = (h.get("producer") or h.get("family") or "-", h.get("dtype"), h.get("unit"))
                groups.setdefault(key, []).append(h["id"])
            for (p, dt, un), ids in groups.items():
                L += labelled(f"{p} | {dt} | {un}", ids)

    # roles
    roles = [(k, v) for k, v in top.items() if "roles" in k and isinstance(v, (dict, list))]
    if roles:
        L += ["", "## Roles (role: kind, nullable)"]
        for k, v in roles:
            used.add(k)
            items = list(v.items()) if isinstance(v, dict) else [(None, v)]
            for pn, lst in items:
                if isinstance(lst, list) and all(isinstance(x, dict) for x in lst):
                    txt = "; ".join(f"{x.get('role')}: {x.get('kind')}, nullable={x.get('nullable')}" for x in lst)
                    L.append(f"- {jpath('$', k)}{'.' + pn if pn else ''}: {txt}")
                else:
                    L.append(f"- {jpath('$', k)}: {compact(lst, 200)}")

    # config + closed vocabularies
    colls = find_fixture_collections(top)
    fixture_keys = {p.split(".")[1].split("[")[0].strip('"') for p, _, _ in colls} | {"fixtures"}
    vocab = []

    def find_vocab(o, path):
        if isinstance(o, dict):
            for k, v in o.items():
                p = jpath(path, k)
                if VOCAB_KEY.search(k) and isinstance(v, list) and v and all(is_scalar(x) for x in v):
                    vocab.append((p, v))
                elif VOCAB_KEY.search(k) and isinstance(v, dict) and v and len(v) <= 14 \
                        and all(is_scalar(x) for x in v.values()):
                    vocab.append((p, v))
                else:
                    find_vocab(v, p)
        elif isinstance(o, list):
            for i, v in enumerate(o[:60]):
                find_vocab(v, jpath(path, i))

    L += ["", "## Config parameters and closed vocabularies"]
    for k, v in top.items():
        if k in ("config", "parameters") and isinstance(v, dict):
            used.add(k)
            L.append(f"- {jpath('$', k)}: {compact(v, 600)}")
    L.append("- (producer parameters are listed under Producers)")
    find_vocab({k: v for k, v in top.items() if k not in fixture_keys}, "$")
    for p, v in vocab[:30]:
        L.append(f"- {p}: {compact(v, 330)}")
    if len(vocab) > 30:
        L.append(f"- ... {len(vocab) - 30} more vocabulary-like paths omitted")

    # fixtures
    L += ["", "## Fixtures"]
    counts = top.get("fixture_counts")
    if counts is None and isinstance(top.get("fixtures"), dict):
        counts = top["fixtures"].get("fixture_counts")
    if counts is not None:
        L.append(f"- declared fixture_counts: {compact(counts, 400)}")
    totals = defaultdict(int)
    ents = defaultdict(set)
    seen = defaultdict(list)
    for path, cname, fl in colls:
        kind = kind_of(cname)
        totals[kind] += len(fl)
        used.add(path.split(".")[1].split("[")[0].strip('"'))
        L.append(f"### {kind}: {path} ({len(fl)} fixtures)")
        for f in fl:
            seen[f["id"]].append(path)
            entity_values(f, ents)
        if kind == "refusal":
            by = OrderedDict()
            for f in fl:
                by.setdefault(refusal_code(f), []).append(f["id"])
            L.append("refusal code -> ids:")
            for code, ii in by.items():
                L += labelled(code, ii)
            continue
        grp = OrderedDict()
        for f in fl:
            grp.setdefault(f.get("group") or f.get("family") or "-", []).append(f["id"])
        if list(grp) == ["-"]:
            L += wrap_ids([f["id"] for f in fl])
        else:
            L.append("by group:")
            for g, ii in grp.items():
                L += labelled(g, ii)
        acc = OrderedDict()
        for f in fl:
            vals = []
            collect(f, "acceptance", vals)
            acc.setdefault(",".join(sorted(set(map(str, vals)))) or "(none recorded)", []).append(f["id"])
        L.append("acceptance rule kinds in body:")
        for a, ii in acc.items():
            if len(ii) == len(fl):
                L.append(f"- {a}: all {len(ii)}")
            else:
                L += labelled(a, ii)
    L.append("- totals: " + ", ".join(f"{k}={v}" for k, v in sorted(totals.items())))
    dup = [i for i, p in seen.items() if len(p) > 1]
    if dup:
        L.append(f"- ids in more than one collection (--fixture prints all): {' '.join(dup)}")
    L.append("- entity ids in fixture bodies (keys instrument/entity/symbol/benchmark[_id]): "
             + ("; ".join(f"{k}={sorted(v)[:12]}" for k, v in ents.items()) if ents else "none found"))

    # unparsed
    L += ["", "## Unparsed (not summarised; read by JSON path)"]
    for k, v in top.items():
        if k in used or k == "fixture_counts":
            continue
        if isinstance(v, (dict, list)):
            extra = f" keys={one(list(v)[:8], 90)}" if isinstance(v, dict) else ""
            L.append(f"- {jpath('$', k)}: {type(v).__name__}[{len(v)}]{extra}")
        else:
            L.append(f"- {jpath('$', k)}: {one(v, 80)}")
    return "\n".join(L) + "\n"


def find_fixture(doc, fid):
    hits = []
    if isinstance(doc, dict):
        for path, _, fl in find_fixture_collections(doc):
            for i, f in enumerate(fl):
                if f["id"] == fid:
                    hits.append((f"{path}[{i}]", f))
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("contract")
    ap.add_argument("--out", help="write the pack here instead of stdout")
    ap.add_argument("--fixture", help="print one fixture body (compact JSON) instead of the pack")
    a = ap.parse_args()
    with open(a.contract, encoding="utf-8") as fh:
        doc = json.load(fh)
    if a.fixture:
        hits = find_fixture(doc, a.fixture)
        if not hits:
            print(f"fixture id not found: {a.fixture}", file=sys.stderr)
            return 1
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
        for p, f in hits:
            print(f"# {p}", file=sys.stderr)
            sys.stdout.write(compact(f) + "\n")
        return 0
    text = build_pack(doc, os.path.basename(a.contract))
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    else:
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
