"""Ingestion boundary: providers must return validated normalized evidence."""

from datetime import datetime, timedelta, timezone
from typing import Protocol

from .models import Chain, Label, Transaction

DEMO_TARGET = "0x71a000000000000000000000000000000000092f"


def address(n):
    return "0x" + format(n, "040x")


class EvidenceProvider(Protocol):
    def fetch(
        self, target: str, chain: Chain
    ) -> tuple[list[Transaction], list[Label]]: ...


class SyntheticProvider:
    """Closed, deterministic fixture; labels do not describe real addresses."""

    def fetch(self, target, chain):
        if target != DEMO_TARGET:
            raise ValueError(
                f"Demo supports only {DEMO_TARGET}. Import evidence for another wallet."
            )
        start = datetime(2026, 8, 18, 12, 0, tzinfo=timezone.utc)
        # All transfers use one synthetic stablecoin. No current-price conversion.
        transfers = [
            (90, 0, 20000, 0),
            (0, 1, 10000, 3),
            (0, 2, 5000, 5),
            (0, 3, 3000, 6),
            (1, 4, 8000, 11),
            (2, 11, 4500, 13),
            (3, 20, 2500, 17),
            (4, 10, 7000, 22),
            (1, 30, 1500, 24),
            (30, 12, 1200, 31),
            (3, 40, 400, 35),
            (40, 21, 350, 48),
        ]
        txs = [
            Transaction(
                tx_hash="0x" + format(i + 1, "064x"),
                chain=chain,
                block_number=24001000 + i,
                timestamp=start + timedelta(minutes=minute),
                from_address=target if a == 0 else address(a),
                to_address=target if b == 0 else address(b),
                asset="DEMO-USD",
                amount=str(value),
                usd_value=str(value),
                contract_address=address(999),
                transaction_type="token",
                source="Synthetic SIH fixture v1; not on-chain evidence",
                source_confidence=1,
            )
            for i, (a, b, value, minute) in enumerate(transfers)
        ]
        labels = [
            Label(
                address=address(n),
                chain=chain,
                entity=entity,
                entity_type=kind,
                confidence=confidence,
                strength="strong",
                source="Synthetic fixture; fictional address association",
                source_reliability=1,
                observed_at=start,
                synthetic=True,
            )
            for n, entity, kind, confidence in [
                (10, "Binance (demo)", "vasp", 0.95),
                (11, "Binance (demo)", "vasp", 0.95),
                (12, "Binance (demo)", "vasp", 0.90),
                (20, "Coinbase (demo)", "vasp", 0.95),
                (21, "Kraken (demo)", "vasp", 0.90),
                (30, "Mixer service (demo)", "mixer", 0.95),
                (40, "Bridge service (demo)", "bridge", 0.95),
            ]
        ]
        return txs, labels
