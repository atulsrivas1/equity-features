# Contract fixture expansion helpers (EF4)

These are fixture-expansion helpers for manual qualification. They are not tests and are not run by CI.

| File | What it does |
|---|---|
| `ef4g_fixture_expand.py` | Recomputes the EF4-G window/top-k/merge/generator fixtures and typed refusals from the TAPE contract proposal. |
| `ef4h_fixture_expand.py` | Independent exact-fraction recompute of the EF4-H quote and VWAP fixtures and refusal recipes (EQ-159, EQ-160). |
| `ef4i_fixture_expand.py` | Independent recompute of the EF4-I path-efficiency and path-projection result fixtures and refusals. |
| `ef5_fixture_expand.py` | Independent recompute of the EF5 candle, structure, technical and known_at KA-set fixtures, plus a single-fault admission audit of every refusal recipe. |

Run from the repo root (stdlib only, Python 3):

    python3 tools/contract_fixtures/ef4g_fixture_expand.py [docs/ef4/TAPE_CONTRACT_PROPOSAL.json]
    python3 tools/contract_fixtures/ef4h_fixture_expand.py [docs/ef4/QUOTE_VWAP_CONTRACT_PROPOSAL.json [proposal.md]]
    python3 tools/contract_fixtures/ef4i_fixture_expand.py [DIR_WITH_JSON]
    python3 tools/contract_fixtures/ef5_fixture_expand.py [docs/ef5/PRICE_STRUCTURES_CONTRACT_PROPOSAL.json]

With no arguments each reads its JSON from `docs/ef4/` at the repo root. The docs folder can also be set with
`EF4_DOCS_DIR=/path/to/docs/ef4`. Exit code 0 means every fixture matched.

SHA-256 (committed blobs, LF endings):

- ef4g_fixture_expand.py: d28f551c2ea21ea4454e6c81b329a52d4edcf06e36ec3e097ee80033f940fd7f
- ef4h_fixture_expand.py: ca986ccffceb5cc8b318dbc20f3339c89f9bd585e34e32f8a42fc368eaf8b3ad
- ef4i_fixture_expand.py: ffc65b2156acaadcfb1969612cbd88e4f628e025847dfd62e0585cf8a66150b8
- ef5_fixture_expand.py: ae93aa5c584755f82f289cf60084b31bc1c8db0d6eec690ba14cf7096a53c5a9

Rule: these are fixture-expansion helpers, not tests. `tools/verify_ef4_fixtures.py` is the gate that runs the three EF4 helpers (`tools/verify_ef5_fixtures.py` gates the EF5 helper)
and pins the known_at semantics; a passing run is a verification result, not a unit test. The paired review comparators are intentionally not vendored here.
