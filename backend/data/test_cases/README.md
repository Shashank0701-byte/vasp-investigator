# Investigation Test Fixtures

Five deterministic importable test cases for SIH demonstration and regression testing.

| File | Purpose |
|---|---|
| 01_strong_vasp.json | Clear Binance attribution via 2-hop path |
| 02_mixed_flow.json | Ambiguous — Coinbase vs Kraken candidates |
| 03_mixer_risk.json | Tornado Cash exposure + Binance candidate |
| 04_dex_flow.json | DEX service boundary (tracing stops) |
| 05_unknown.json | No VASP labels — zero fabricated attribution |

Import via the UI's "Import evidence" button or use with the API:
`POST /api/cases` with `mode: "import"`.
