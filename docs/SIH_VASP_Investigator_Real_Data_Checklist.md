# SIH 2026 — VASP Investigator
## Real Data & Dataset Acquisition Checklist

> **Purpose:** Define every external data source, dataset, label, metadata field, credential, and test fixture required to turn the current VASP Investigator prototype into a real-data, demonstrable SIH system.
>
> **Use this as a team acquisition checklist, not as a coding task list.**

---

# 1. Definition of Done

The data layer is ready when:

- [ ] Given an Ethereum or BNB Smart Chain wallet address, the system can retrieve real historical activity.
- [ ] Raw provider responses can be stored and reproduced.
- [ ] Blockchain data is normalized into the existing `Transaction` model.
- [ ] Known VASP/exchange addresses can be identified with provenance.
- [ ] Risk intelligence can identify relevant sanctioned, mixer, scam/phishing, bridge, and DEX addresses.
- [ ] The trace engine can produce candidate VASP attribution with supporting transaction paths.
- [ ] The UI can show graph, candidate VASPs, evidence, risk indicators, and provenance.
- [ ] At least 4–5 deterministic investigation cases exist for SIH demonstration and regression testing.
- [ ] No API keys, private keys, or other secrets are committed to Git.

---

# 2. Priority Overview

| Priority | Requirement | Why | Suggested Owner |
|---|---|---|---|
| **P0** | Blockchain history provider | Core real-data ingestion | Backend |
| **P0** | Ethereum + BNB transaction/transfer data | Input to tracing engine | Backend/Data |
| **P0** | Verified VASP address labels | Core VASP attribution | Data/Research |
| **P0** | Source/provenance metadata | Evidence and defensibility | Data/Research |
| **P0** | 4–5 investigation test cases | Demo + regression testing | Backend + Data |
| **P1** | OFAC digital-currency sanctions data | Risk enrichment | Data/Compliance |
| **P1** | Mixer / bridge / DEX / scam labels | Typology and risk context | Data/Research |
| **P1** | Historical USD pricing | Value-based metrics | Backend |
| **P1** | Ethereum labeled research dataset | Evaluation/calibration | Research |
| **P2** | Regulatory/VASP registry enrichment | Entity context | Research |
| **P2** | Additional chains/providers | Future expansion | Backend |

---

# 3. A — Blockchain Data

## Primary provider

Use one structured blockchain-history provider first rather than immediately building separate explorer adapters.

### Recommended starting provider

**GoldRush (formerly Covalent)**

Required:

- [ ] Create GoldRush account.
- [ ] Obtain API key.
- [ ] Store key only in `backend/.env`.
- [ ] Add something like:

```env
GOLDRUSH_API_KEY=your_key_here
```

- [ ] Never commit the key to Git.

## Ethereum data

Collect:

- [ ] Normal Ethereum transaction history.
- [ ] ERC-20 token transfers.
- [ ] Internal/native-value movements where supported.
- [ ] Block numbers.
- [ ] Transaction indices.
- [ ] Transaction hashes.
- [ ] Timestamps.
- [ ] Sender addresses.
- [ ] Recipient addresses.
- [ ] Token contract addresses.
- [ ] Token symbols/names where available.
- [ ] Token decimals.
- [ ] Amounts.
- [ ] Historical USD values.

## BNB Smart Chain data

Collect:

- [ ] Normal BNB transactions.
- [ ] BEP-20 token transfers.
- [ ] Internal/native-value movements where supported.
- [ ] Block numbers.
- [ ] Transaction indices.
- [ ] Transaction hashes.
- [ ] Timestamps.
- [ ] Sender addresses.
- [ ] Recipient addresses.
- [ ] Token contract addresses.
- [ ] Token symbols/names.
- [ ] Token decimals.
- [ ] Amounts.
- [ ] Historical USD values.

## Provider engineering requirements

- [ ] Pagination.
- [ ] Retry/backoff.
- [ ] Rate-limit handling.
- [ ] API-key management.
- [ ] Reorg/finality handling.
- [ ] Failed transaction handling.
- [ ] Provider health status.
- [ ] Retrieval timestamps.
- [ ] Raw response storage.
- [ ] Deterministic normalization.

---

# 4. Blockchain → Existing `Transaction` Model

The existing backend expects normalized evidence. The provider adapter should map external data into these fields.

| Field | Required | Purpose |
|---|---:|---|
| `tx_hash` | Yes | Transaction identifier |
| `event_index` | Yes | Distinguish multiple transfers in one transaction |
| `chain` | Yes | `ethereum` / `bnb` |
| `block_number` | Yes | Ordering/finality |
| `transaction_index` | Preferred | Ordering within block |
| `timestamp` | Yes | Chronological tracing |
| `from_address` | Yes | Sender |
| `to_address` | Yes | Recipient |
| `asset` | Yes | Native asset/token |
| `amount` | Yes | Exact amount |
| `usd_value` | Preferred | Value/risk metrics |
| `contract_address` | Preferred | Token contract |
| `transaction_type` | Yes | `native` / `token` / `internal` |
| `source` | Yes | Data provider |
| `source_confidence` | Yes | Data-quality confidence |

---

# 5. B — VASP / Exchange Address Intelligence

This is the most important label layer for the project's core question:

> **Which known VASP/entity is supported by the observed transaction path?**

## Required chains

- [ ] Ethereum
- [ ] BNB Smart Chain

## Initial VASP set

Start with:

- [ ] Binance
- [ ] Coinbase
- [ ] Kraken
- [ ] OKX
- [ ] Bybit
- [ ] KuCoin

Optional:

- [ ] Gate.io
- [ ] Bitstamp
- [ ] Crypto.com

## Address roles

Where possible, identify:

- Deposit address
- Hot wallet
- Cold wallet
- Withdrawal wallet
- Treasury wallet
- Operational wallet
- Unknown

## Verification requirements

For important addresses:

- [ ] Verify against a reliable source.
- [ ] Record source URL.
- [ ] Record source name.
- [ ] Record verification date.
- [ ] Record confidence.
- [ ] Record source reliability.
- [ ] Record address role if known.
- [ ] Do not silently merge conflicting labels.

### Important

A VASP's regulatory registration **does not prove** that a particular blockchain address belongs to that VASP.

Regulatory/entity data and blockchain address attribution must remain separate evidence layers.

## Public starting sources

### CEX addresses

https://github.com/ohhkaneda/cex-addresses-ethereum

### Crypto wallet address labels

https://github.com/ImMike/crypto-wallet-address-labels

### eth-labels

https://github.com/dawsbot/eth-labels

---

# 6. VASP Label Schema

Recommended record:

```json
{
  "address": "0x...",
  "entity": "Binance",
  "entity_type": "vasp",
  "chain": "ethereum",
  "address_role": "hot_wallet",
  "confidence": 0.95,
  "strength": "strong",
  "source": "Etherscan",
  "source_url": "https://...",
  "source_reliability": "high",
  "first_verified": "2026-09-01",
  "last_verified": "2026-09-28",
  "observed_at": "2026-09-28",
  "synthetic": false
}
```

Recommended files:

```text
backend/data/labels/
├── ethereum_vasps.json
├── bnb_vasps.json
├── mixers.json
├── bridges.json
├── dex.json
└── scams.json
```

---

# 7. C — Entity / Regulatory Intelligence

This is **enrichment**, not blockchain ownership evidence.

For each VASP/entity, collect:

- [ ] Legal entity name.
- [ ] Trading/brand name.
- [ ] Jurisdiction.
- [ ] Regulator.
- [ ] Registration/license identifier where applicable.
- [ ] Registration/status date.
- [ ] Official website.
- [ ] Official regulatory source.
- [ ] Verification date.
- [ ] Current status.
- [ ] Exact source wording for unusual statuses/notices.

## India-specific

Review:

**FIU-IND**

https://fiuindia.gov.in/

Downloads:

https://fiuindia.gov.in/files/Downloads/Downloads.html

Relevant material includes VDA reporting-entity/AML-CFT guidance and registration information.

### Important distinction

```text
Regulatory registration
        ≠
Proof of blockchain address ownership
```

Keep these as separate evidence layers.

---

# 8. D — Sanctions & Risk Intelligence

Collect:

## Sanctions

- [ ] OFAC SDN data.
- [ ] OFAC consolidated sanctions data.
- [ ] Digital-currency addresses contained in sanctions data.

Official source:

https://ofac.treasury.gov/sanctions-list-service

## Other risk labels

- [ ] Mixer addresses.
- [ ] Scam addresses.
- [ ] Phishing addresses.
- [ ] Bridge addresses.
- [ ] DEX/router addresses.
- [ ] Optional ransomware/illicit-address datasets.

## Risk label schema

```json
{
  "address": "0x...",
  "chain": "ethereum",
  "entity": "Example Entity",
  "entity_type": "sanctioned",
  "source": "OFAC",
  "source_url": "https://...",
  "confidence": 1.0,
  "source_reliability": "high",
  "observed_at": "2026-09-28"
}
```

### Important

Risk labels should be presented as **sourced intelligence**, not as proof that an address owner committed wrongdoing.

---

# 9. E — Research / Evaluation Datasets

These datasets are primarily for evaluating the system, not for direct live investigative evidence.

| Dataset | Use | Priority |
|---|---|---|
| Ethereum labeled-address + transaction dataset | Entity/VASP attribution evaluation | P1 |
| Elliptic Bitcoin dataset | Illicit/licit graph-risk evaluation | P1 |
| BitcoinHeist | Ransomware/risk experiments | P2 |
| XBlock Ethereum datasets | Phishing/Ponzi/transaction experiments | P2 |
| Commercial Elliptic Data Fabric | High-quality commercial enrichment | Not required for MVP |

## Ethereum labeled dataset

Scientific Data paper:

https://www.nature.com/articles/s41597-025-05662-w

This is particularly useful for evaluating entity attribution because it contains labeled Ethereum addresses associated with known entities.

## Elliptic

https://www.elliptic.co/insights/elliptic-dataset-cryptocurrency-financial-crime/

Useful for graph/risk evaluation.

## BitcoinHeist

https://archive.ics.uci.edu/dataset/526/bitcoinheistransomwareaddressdataset

Useful for ransomware experiments.

## XBlock

https://www.kaggle.com/xblock/datasets

Useful for Ethereum phishing/Ponzi/transaction experiments.

---

# 10. F — Historical Pricing / Valuation

The existing engine uses value-related metrics, so pricing matters.

Collect:

- [ ] Historical ETH/USD prices.
- [ ] Historical BNB/USD prices.
- [ ] Historical ERC-20 USD prices where available.
- [ ] Historical BEP-20 USD prices where available.
- [ ] Token decimals.
- [ ] Price timestamp.
- [ ] Pricing source.
- [ ] Retrieval date.
- [ ] Fallback behavior when price is unavailable.

Do not invent USD values when no reliable historical price exists.

---

# 11. G — Investigation Test Cases

Prepare at least **5 deterministic cases**.

| Case | Purpose | Example |
|---|---|---|
| 01 — Strong VASP | Clear attribution | Wallet → intermediate → known VASP |
| 02 — Mixed/Ambiguous | Multiple candidates | Wallet → several possible entities |
| 03 — Mixer/Risk | Risk boundary | Wallet → mixer/risk address |
| 04 — DEX/Service | Service boundary | Wallet → DEX |
| 05 — Unknown | Avoid unsupported attribution | Wallet with no verified VASP destination |

Each fixture should contain:

- [ ] Input wallet.
- [ ] Chain.
- [ ] Relevant transaction history.
- [ ] Expected candidate entities.
- [ ] Expected evidence edges.
- [ ] Risk labels where applicable.
- [ ] Source/provenance.
- [ ] Retrieval date.
- [ ] Expected engine behavior.

Recommended directory:

```text
backend/data/test_cases/
├── strong_vasp.json
├── mixed_flow.json
├── mixer_flow.json
├── dex_flow.json
└── unknown.json
```

Do not manufacture real-world ownership claims for demo addresses.

---

# 12. H — Raw Data & Repository Structure

Recommended structure:

```text
vasp-investigator/
└── backend/
    └── data/
        ├── labels/
        │   ├── ethereum_vasps.json
        │   ├── bnb_vasps.json
        │   ├── mixers.json
        │   ├── bridges.json
        │   ├── dex.json
        │   └── scams.json
        │
        ├── entities/
        │   └── vasps.json
        │
        ├── sanctions/
        │   └── ofac.json
        │
        ├── raw/
        │   ├── ethereum/
        │   └── bnb/
        │
        └── test_cases/
            ├── strong_vasp.json
            ├── mixed_flow.json
            ├── mixer_flow.json
            ├── dex_flow.json
            └── unknown.json
```

---

# 13. I — Data Quality & Provenance Requirements

Every dataset/label should answer:

> **Where did this information come from, when was it verified, and how confident are we?**

Checklist:

- [ ] Every non-synthetic label has a source.
- [ ] Every source has a retrieval/verification date.
- [ ] High-confidence labels use reliable/verifiable sources.
- [ ] Conflicting labels are not silently overwritten.
- [ ] Addresses are normalized consistently.
- [ ] Chain/network is explicitly recorded.
- [ ] Address tags are not automatically transferred between chains.
- [ ] Raw provider data is kept separate from normalized data.
- [ ] Dataset licenses/usage terms are reviewed.
- [ ] API keys are never committed.
- [ ] Private keys are never stored in the repository.
- [ ] Retrieval timestamps are recorded.
- [ ] Data refresh policy is documented.

---

# 14. J — What We Do NOT Need for the SIH MVP

Do **not** over-engineer the data acquisition.

We do not currently need:

- [ ] Full Ethereum node.
- [ ] Full BNB node.
- [ ] Terabytes of blockchain history.
- [ ] Every VASP.
- [ ] Every wallet.
- [ ] 100+ blockchain networks.
- [ ] ML model for the core tracing pipeline.
- [ ] LLM-based attribution.
- [ ] Commercial Chainalysis subscription.
- [ ] Commercial Elliptic subscription.
- [ ] Kafka.
- [ ] Redis.
- [ ] Kubernetes.
- [ ] Microservices architecture.

### MVP target

```text
2 chains
+
5–10 VASPs
+
a few hundred verified labels
+
real wallet histories
+
OFAC/risk labels
+
4–5 deterministic test cases
```

That is enough to demonstrate the core system properly.

---

# 15. K — Team Ownership

Suggested division:

| Workstream | Deliverables | Suggested Owner |
|---|---|---|
| Blockchain ingestion | Provider access, API samples, normalization mapping | Backend |
| VASP labels | Ethereum + BNB verified address registry | Data/Research 1 |
| Risk labels | OFAC + mixer/scam/bridge/DEX registry | Data/Research 2 |
| Regulatory intelligence | VASP entity metadata + Indian official sources | Research |
| Evaluation datasets | Research datasets + documentation | ML/Research |
| Test fixtures | 5 deterministic investigation cases | Backend + Data |
| Frontend | Graph/evidence/VASP display requirements | Frontend |
| DevOps | Secrets, environment variables, deployment data handling | DevOps |

---

# 16. L — Final Acquisition Checklist

## Blockchain

- [ ] GoldRush account created
- [ ] API key obtained
- [ ] Ethereum sample retrieved
- [ ] BNB sample retrieved
- [ ] ERC-20 sample retrieved
- [ ] BEP-20 sample retrieved
- [ ] Internal/native movements retrieved
- [ ] Historical pricing confirmed
- [ ] Pagination tested
- [ ] Retry/rate-limit behavior tested
- [ ] Raw responses stored

## VASP

- [ ] Ethereum VASP labels collected
- [ ] BNB VASP labels collected
- [ ] Binance verified
- [ ] Coinbase verified
- [ ] Kraken verified
- [ ] OKX verified
- [ ] Bybit verified
- [ ] KuCoin verified
- [ ] Address roles captured where possible
- [ ] Source URL captured for every important label
- [ ] Verification date captured

## Regulatory

- [ ] VASP legal names collected
- [ ] Brand names collected
- [ ] Jurisdictions collected
- [ ] Regulatory sources collected
- [ ] FIU-IND sources reviewed
- [ ] Registration/status metadata separated from blockchain labels

## Risk

- [ ] OFAC data obtained
- [ ] OFAC digital-currency addresses parsed
- [ ] Mixer labels collected
- [ ] Bridge labels collected
- [ ] DEX labels collected
- [ ] Scam labels collected
- [ ] Phishing labels collected

## Research

- [ ] Ethereum labeled-address dataset selected
- [ ] Elliptic dataset reviewed
- [ ] BitcoinHeist reviewed if needed
- [ ] XBlock reviewed if needed
- [ ] Licenses/usage terms documented

## Testing

- [ ] Strong VASP case
- [ ] Mixed/ambiguous case
- [ ] Mixer/risk case
- [ ] DEX/service case
- [ ] Unknown case

## Quality

- [ ] Provenance on labels
- [ ] Verification dates
- [ ] Retrieval dates
- [ ] Source reliability
- [ ] Confidence
- [ ] Chain recorded
- [ ] Conflicting labels handled explicitly
- [ ] No secrets committed

---

# 17. Sources

| Source | URL |
|---|---|
| GoldRush — Ethereum | https://goldrush.dev/chains/ethereum/ |
| GoldRush — BNB Smart Chain | https://goldrush.dev/chains/bnb-smart-chain-%28bsc%29/ |
| GoldRush Documentation | https://goldrush.dev/docs/ |
| CEX Ethereum Address Labels | https://github.com/ohhkaneda/cex-addresses-ethereum |
| Crypto Wallet Address Labels | https://github.com/ImMike/crypto-wallet-address-labels |
| eth-labels | https://github.com/dawsbot/eth-labels |
| OFAC Sanctions List Service | https://ofac.treasury.gov/sanctions-list-service |
| FIU-IND | https://fiuindia.gov.in/ |
| FIU-IND Downloads | https://fiuindia.gov.in/files/Downloads/Downloads.html |
| Ethereum Labeled Address Dataset | https://www.nature.com/articles/s41597-025-05662-w |
| Elliptic Dataset | https://www.elliptic.co/insights/elliptic-dataset-cryptocurrency-financial-crime/ |
| BitcoinHeist / UCI | https://archive.ics.uci.edu/dataset/526/bitcoinheistransomwareaddressdataset |
| XBlock Datasets | https://www.kaggle.com/xblock/datasets |

---

# 18. Immediate Next Step

**Do not collect everything simultaneously.**

The team should first finish **P0**:

```text
1. Blockchain provider access
        ↓
2. Real Ethereum + BNB samples
        ↓
3. Initial verified VASP registry
        ↓
4. Provenance metadata
        ↓
5. Five replayable investigation cases
```

Once these exist, the backend can connect the real data to the existing normalizer and trace engine without redesigning the core architecture.

---

## Team Rule

> **Every external fact used by the investigator should be traceable back to a source.**

For this project, provenance is not optional metadata — it is part of the evidence model.
