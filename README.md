# Tracepoint — VASP Investigator

A runnable SIH 2026 prototype for explainable attribution of cryptocurrency fund flows to labelled service endpoints. It identifies **evidence-supported VASP candidates**, not people or wallet ownership.

## Run locally

Requires Node.js 20.9+ and Python 3.9+ (3.12 recommended).

```sh
./scripts/setup.sh
./scripts/dev.sh
```

Open http://127.0.0.1:3000. Choose **Explore demo investigation**. API documentation: http://127.0.0.1:8000/docs.

The synthetic Ethereum / BNB scenario needs no API keys. It is restricted to the supplied demo address. Changing to an arbitrary address does not fabricate results. For other addresses use **Import evidence**, following [the import guide](docs/IMPORT.md).

## Implemented

- Next.js / TypeScript dashboard with six investigation views.
- React Flow graph: zoom/pan, node/edge evidence, depth/value/date/entity filters, risk highlights, candidate-path highlighting and expansion of already-loaded neighbors.
- FastAPI/Pydantic normalized evidence contracts with chain isolation, decimal amounts, contract-based token identity, duplicate-event rejection and timezone validation.
- Chronological, same-asset proportional tracing, hop limits, cycle boundaries and conservative service endpoint stops.
- Transparent weighted attribution scores with label/source-quality caps, conservative edge-disjoint support, exposure and hop evidence.
- Rule-based risk signals, valuation coverage, observed velocity, HHI and entropy.
- Saved cases, source evidence digest, downloadable Markdown reports and JSON evidence.
- SQLite for easy local use; PostgreSQL through `DATABASE_URL` and Docker Compose.

## Verify

```sh
cd backend
.venv/bin/python -m pytest -q
cd ../frontend
npm run build
npm run typecheck
npx playwright install chromium
# With both local servers running:
npm run test:e2e
```

Browser tests cover demo analysis, candidate selection, graph filtering, evidence selection, report download, imported no-evidence cases, persistence, and a mobile viewport. GitHub Actions runs the backend checks and frontend production build. CI is provided but has not run on GitHub yet.

## Structure

```text
backend/app/models.py       Validated evidence schema
backend/app/providers.py    Provider interface and synthetic scenario
backend/app/engine.py       Tracing, attribution, risk and quantitative metrics
backend/app/storage.py      SQLAlchemy case persistence
backend/app/report.py       Deterministic evidence report
backend/app/main.py         HTTP API
frontend/app/               Dashboard and styles
frontend/components/        Interactive graph
frontend/tests/             Browser workflow tests
```

See [methodology](docs/METHODOLOGY.md), [API/import format](docs/IMPORT.md), and [next milestones](docs/ROADMAP.md).

## PostgreSQL / containers

```sh
docker compose up --build
```

This runs PostgreSQL, the API and the dashboard. The database is on the internal Compose network; the UI and API bind to localhost. Compose supplies development-only database credentials. For a separately managed database, set `DATABASE_URL=postgresql+psycopg://user:password@host/database` before starting the API. Docker configuration is supplied; local validation used SQLite, not Docker/PostgreSQL.

## Scope and operating boundaries

This is a **local, single-investigator prototype**. It has no authentication, multi-user isolation or production deployment hardening. Keep it on localhost. Do not expose it as a public service.

Live RPC/explorer adapters, a real verified label dataset, cross-chain linkage, token swaps, calibration against labelled outcomes, production migrations, authentication and PDF export are future milestones. Imported labels retain their asserted source and confidence; the application does not certify them. No freezing/disclosure messages are sent.

The source evidence SHA-256 digest permits content comparison; it is not a signature, immutable audit log, or proof that supplied transactions happened on-chain. SQLite files and local evidence are excluded from Git.

## Framework references

- [Next.js installation](https://nextjs.org/docs/app/getting-started/installation)
- [React Flow quick start](https://reactflow.dev/learn)
- [FastAPI SQL databases](https://fastapi.tiangolo.com/tutorial/sql-databases/)
