# Next review and implementation milestones

1. Review this MVP together: validate synthetic scenario, scoring assumptions, UI and tests. Choose repository name/visibility and push only after that review.
2. Select an Ethereum/BNB history provider. Implement pagination, retry/backoff, API-key management, reorg/finality handling, failed-transaction exclusion and normalized native/ERC-20/internal events. RPC alone is not a complete address-history index.
3. Curate a small real label dataset with source URLs, date, licensing, evidence strength and explicit refresh policy. Keep demonstration labels isolated.
4. Evaluate attribution on known cases with ground truth, calibrate weights and quality thresholds, and add missing-data sensitivity analysis.
5. Improve lineage and mixed-balance uncertainty handling; add processing budgets and background jobs for large histories. Add more typologies only with testable evidence criteria.
6. Add authentication, authorization, case ownership, secure secrets, migrations, immutable audit logging and deployment hardening before any multi-user/public use.
7. Add reviewed document/PDF exports and authorized-contact routing metadata. Requests must remain investigator-controlled.

This first implementation intentionally does not claim commercial intelligence coverage or real-time ingestion. PostgreSQL is configured but the initial local validation runs against SQLite.
