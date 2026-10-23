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
STATUS_KEY = re.compile(r"status_of_reason|reason_order|statuses|status_precedence")
VOCAB_KEY = re.compile(r"vocab|_values$|^values$|reasons|precedence|enum|codes|^direction|status_of_reason|statuses|reason_order")
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
    return textwrap.wrap(" ".join(ids), 140, initial_indent=indent, subsequent_indent=indent)


def clip(s, n):
    """Explicit, marked truncation (never silent)."""
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 12] + " [cut,full:--fixture]"


def render(label, v, indent="  "):
    """Full (untruncated) wrapped rendering of a JSON value as lines."""
    def wrap(text, ind):
        return textwrap.wrap(text, 140, initial_indent=ind, subsequent_indent=" " * len(ind) + "  ",
                             break_long_words=False, break_on_hyphens=False) or [ind]
    if isinstance(v, dict) and v and all(is_scalar(x) or (isinstance(x, list) and all(is_scalar(y) for y in x))
                                         for x in v.values()):
        out = [indent + f"{label}:"] if label else []
        for k, x in v.items():
            out += wrap(f"{k}: {x if isinstance(x, str) else json.dumps(x, ensure_ascii=False)}",
                        " " * len(indent) + "  " if label else indent)
        return out
    txt = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
    return wrap(f"{label}: {txt}" if label else txt, indent)


def labelled(label, ids):
    """'- label (n): ids' wrapped with a hanging indent (one line when short)."""
    return textwrap.wrap(f"- {label} ({len(ids)}): " + " ".join(ids), 140, subsequent_indent="    ")


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
    L.append("Derived mechanically from the JSON; nothing is invented. Pointers are JSON paths."
             " Read one fixture with `--fixture ID`. Truncation, where any, is marked [cut].")
    L += ["", "## Contract"]
    for k, v in top.items():
        if is_scalar(v) and (VERSION_KEY.search(k) or k in ("story", "frozen_contract_ref")):
            L += render(k, v, "- ")
            used.add(k)

    # producers (all fields, untruncated)
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
        L += ["", "## Producers (path: $.producers[.name] or *_producer)"]
        for pname, p in prods:
            vs = [f"{k}={v}" for k, v in p.items() if is_scalar(v) and VERSION_KEY.search(k)]
            L.append(f"- {pname}: " + "; ".join(vs))
            for k, v in p.items():
                if not (is_scalar(v) and VERSION_KEY.search(k)):
                    L += render(k, v, "    ")

    # output ids with all per-id attributes
    hdr_lists = [(k, v) for k, v in top.items() if is_coll(v) and all("dtype" in x for x in v)]
    if hdr_lists:
        L += ["", "## Output ids (producer | dtype | unit | other attributes)"]
        for k, hl in hdr_lists:
            used.add(k)
            L.append(f"{jpath('$', k)} ({len(hl)})")
            groups = OrderedDict()
            for h in hl:
                extra = {a: b for a, b in h.items() if a not in ("id", "dtype", "unit", "producer")
                         and (is_scalar(b) or (isinstance(b, list) and all(is_scalar(y) for y in b)))}
                key = (h.get("producer") or "-", h.get("dtype"), h.get("unit"),
                       json.dumps(extra, ensure_ascii=False, sort_keys=True) if extra else "")
                groups.setdefault(key, []).append(h["id"])
            for (pr, dt, un, ex), ids in groups.items():
                L += labelled(f"{pr} | {dt} | {un}" + (f" | {ex}" if ex else ""), ids)

    # roles (full contract text)
    roles = [(k, v) for k, v in top.items() if "roles" in k and isinstance(v, (dict, list))]
    if roles:
        L += ["", "## Roles (role | kind | nullable | contract text)"]
        for k, v in roles:
            used.add(k)
            items = list(v.items()) if isinstance(v, dict) else [(None, v)]
            for pn, lst in items:
                tag = jpath("$", k) + (f".{pn}" if pn else "")
                if isinstance(lst, list) and all(isinstance(x, dict) for x in lst):
                    L.append(f"- {tag}:")
                    for x in lst:
                        head = f"{x.get('role')} | {x.get('kind')} | nullable={x.get('nullable')}"
                        rest = {a: b for a, b in x.items() if a not in ("role", "kind", "nullable", "contract")}
                        txt = head + (f" | {json.dumps(rest)}" if rest else "") + f" | {x.get('contract', '')}"
                        L += render("", txt, "    ")
                else:
                    L += render(tag, lst, "- ")

    # notation / fact schemas: define role data for contracts with no roles section
    for k, v in top.items():
        if "notation" in k or "fact_schemas" in k:
            used.add(k)
            L += ["", f"## {k} ({jpath('$', k)})"]
            if isinstance(v, dict):
                for kk, vv in v.items():
                    if isinstance(vv, dict) and all(is_scalar(x) or (isinstance(x, list) and all(is_scalar(y) for y in x))
                                                    for x in vv.values()):
                        vv = "; ".join(f"{a}={b if isinstance(b, str) else json.dumps(b)}" for a, b in vv.items())
                    L += render(kk, vv, "- ")
            else:
                L += render("", v, "")

    # config parameters and closed vocabularies
    colls = find_fixture_collections(top)
    fixture_keys = {p.split(".")[1].split("[")[0].strip('"') for p, _, _ in colls} | {"fixtures"}
    vocab = []

    def find_vocab(o, path):
        if isinstance(o, dict):
            for k, v in o.items():
                p = jpath(path, k)
                if k == "coverage_map":
                    continue
                if VOCAB_KEY.search(k) and isinstance(v, list) and v and all(is_scalar(x) for x in v):
                    vocab.append((p, v))
                elif VOCAB_KEY.search(k) and isinstance(v, dict) and v and len(v) <= 24 \
                        and all(is_scalar(x) for x in v.values()):
                    vocab.append((p, v))
                else:
                    find_vocab(v, p)
        elif isinstance(o, list):
            for i, v in enumerate(o[:60]):
                find_vocab(v, jpath(path, i))

    L += ["", "## Config parameters, closed vocabularies, status mapping"]
    for k, v in top.items():
        if k in ("config", "parameters") and isinstance(v, dict):
            used.add(k)
            L += render(jpath("$", k), v, "- ")
    L.append("- (producer parameters and policy are listed under Producers)")
    find_vocab({k: v for k, v in top.items() if k not in fixture_keys}, "$")
    for p, v in vocab:
        L += render(p, v, "- ")
    q = top.get("quality")
    if isinstance(q, dict) and isinstance(q.get("rule"), str):
        L += render("$.quality.rule", q["rule"], "- ")

    # acceptance rule meanings
    acc_src = []
    if isinstance(top.get("acceptance_rules"), dict):
        acc_src.append(("$.acceptance_rules", top["acceptance_rules"]))
        used.add("acceptance_rules")
    npol = top.get("numeric_policy")
    if isinstance(npol, dict):
        used.add("numeric_policy")
        strs = {k: v for k, v in npol.items() if isinstance(v, str)}
        if strs:
            acc_src.append(("$.numeric_policy", strs))
        if isinstance(npol.get("acceptance_rules"), dict):
            acc_src.append(("$.numeric_policy.acceptance_rules", npol["acceptance_rules"]))
        other = [k for k, v in npol.items() if not isinstance(v, str) and k != "acceptance_rules"]
        if other:
            acc_src.append(("note", {"$.numeric_policy not rendered": ", ".join(other)}))
    if acc_src:
        L += ["", "## Acceptance rule meanings"]
        for path, d in acc_src:
            L.append(f"- {path}:")
            for kk, vv in d.items():
                L += render(f"{kk}", vv if isinstance(vv, str) else json.dumps(vv), "    ")

    # fixtures
    L += ["", "## Fixtures"]
    counts = top.get("fixture_counts")
    if counts is None and isinstance(top.get("fixtures"), dict):
        counts = top["fixtures"].get("fixture_counts")
    if counts is not None:
        L += render("declared fixture_counts", counts, "- ")
    totals = defaultdict(int)
    ents = defaultdict(set)
    seen = defaultdict(list)
    statuses = []
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
                by.setdefault(refusal_code(f), []).append(f)
            L.append("refusal code -> id [raised_by] description:")
            for code, ff in by.items():
                L.append(f"- {code} ({len(ff)}):")
                for f in ff:
                    rb = f.get("raised_by") or f.get("producer")
                    L.append("    " + clip(f"{f['id']}" + (f" [{rb}]" if rb else "") + f" {f.get('description', '')}", 175))
            continue
        for f in fl:
            collect(f, "status", statuses)
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
            acc.setdefault(",".join(sorted(set(map(str, vals)))) or "", []).append(f)
        L.append("acceptance rule kinds in body:")
        for a, ff in acc.items():
            ids = [f["id"] for f in ff]
            if a:
                label = a
            else:
                akeys = sorted({k for f in ff for k in f if re.search(r"expected|assert|oracle", k)})
                nested = sorted({c for f in ff if isinstance(f.get("hand_asserted"), dict)
                                 for c in f["hand_asserted"]})
                label = ("no `acceptance` key; these fixtures assert via top-level keys: "
                         + ", ".join(akeys or ["(none found)"])
                         + (f" (hand_asserted cell keys: {', '.join(nested)}; the other outputs are in expected)" if nested else ""))
            if len(ids) == len(fl):
                L += textwrap.wrap(f"- {label}: all {len(ids)}", 140, subsequent_indent="    ")
            else:
                L += labelled(label, ids)
    L.append("- totals: " + ", ".join(f"{k}={v}" for k, v in sorted(totals.items())))
    if statuses:
        L.append("- result `status` values seen in fixture bodies: " + ", ".join(sorted(set(map(str, statuses)))))
    dup = [i for i, p in seen.items() if len(p) > 1]
    if dup:
        L.append(f"- ids in more than one collection (--fixture prints all): {' '.join(dup)}")
    L.append("- entity ids in fixture bodies (keys instrument/entity/symbol/benchmark[_id]): "
             + ("; ".join(f"{k}={sorted(v)}" for k, v in ents.items()) if ents else "none found"))

    # unparsed
    L += ["", "## Unparsed (not summarised; read by JSON path)"]
    for k, v in top.items():
        if k in used or k == "fixture_counts":
            continue
        if isinstance(v, (dict, list)):
            extra = f" keys={one(list(v)[:8], 90)}" if isinstance(v, dict) else ""
            L.append(f"- {jpath('$', k)}: {type(v).__name__}[{len(v)}]{extra}")
        else:
            L.append(f"- {jpath('$', k)}: {one(v, 80)}" + (" [cut]" if len(str(v)) > 80 else ""))
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
    try:
        with open(a.contract, encoding="utf-8") as fh:
            doc = json.load(fh)
    except OSError as e:
        print(f"contract_pack: cannot read {a.contract}: {e.strerror or e}", file=sys.stderr)
        return 2
    except ValueError as e:
        print(f"contract_pack: {a.contract} is not valid JSON: {e}", file=sys.stderr)
        return 2
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
