from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.engine import analyze
from app.models import Chain, InvestigationRequest, Label, Transaction
from app.providers import DEMO_TARGET, SyntheticProvider, address

BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)


def tx(i, a, b, amount, usd="auto", contract=None):
    return Transaction(
        tx_hash="0x" + format(i, "064x"),
        chain="ethereum",
        block_number=i,
        timestamp=BASE + timedelta(minutes=i),
        from_address=address(a),
        to_address=address(b),
        asset="USD" if contract else "ETH",
        amount=str(amount),
        usd_value=str(amount) if usd == "auto" else usd,
        contract_address=address(contract) if contract else None,
        transaction_type="token" if contract else "native",
        source="test fixture",
        source_confidence=1,
    )


def label(a, entity="Exchange", kind="vasp", confidence=1):
    return Label(
        address=address(a),
        chain="ethereum",
        entity=entity,
        entity_type=kind,
        confidence=confidence,
        strength="strong",
        source="test fixture",
        source_reliability=1,
        observed_at=BASE,
    )


def run(txs, labels, hops=4):
    req = InvestigationRequest(
        target=address(0),
        chain="ethereum",
        mode="import",
        max_hops=hops,
        transactions=txs,
        labels=labels,
    )
    return analyze(req, txs, labels)


def test_demo_is_deterministic_and_conserved():
    req = InvestigationRequest(target=DEMO_TARGET)
    txs, labels = SyntheticProvider().fetch(DEMO_TARGET, Chain.ethereum)
    first = analyze(req, txs, labels)
    assert first == analyze(req, list(reversed(txs)), labels)
    assert first["candidates"][0]["entity"] == "Binance (demo)"
    assert first["candidates"][0]["traced_usd"] == 11500
    assert first["candidates"][0]["independent_paths"] == 2
    assert first["metrics"]["attributed_usd"] == 14000
    assert first["metrics"]["outgoing_usd"] == 18000
    assert first["risk"]["score"] == 65
    assert all(c["score"] <= c["quality_cap"] for c in first["candidates"])


def test_branching_cannot_create_money():
    a = run(
        [tx(1, 0, 1, 100), tx(2, 1, 2, 80), tx(3, 1, 3, 80)],
        [label(2, "A"), label(3, "B")],
    )
    assert {c["entity"]: c["traced_usd"] for c in a["candidates"]} == {"A": 80, "B": 20}
    assert a["metrics"]["unresolved_usd"] == 0


def test_out_of_order_transfers_do_not_establish_path():
    assert run([tx(1, 1, 2, 100), tx(2, 0, 1, 100)], [label(2)])["candidates"] == []


def test_contracts_not_symbols_control_asset_identity():
    assert (
        run(
            [tx(1, 0, 1, 100, contract=100), tx(2, 1, 2, 100, contract=200)], [label(2)]
        )["candidates"]
        == []
    )


def test_observed_unrelated_inflow_dilutes_trace():
    a = run([tx(1, 9, 1, 100), tx(2, 0, 1, 100), tx(3, 1, 2, 100)], [label(2)])
    assert a["candidates"][0]["traced_usd"] == 50


def test_service_boundaries_and_hop_limit():
    txs = [tx(1, 0, 1, 100), tx(2, 1, 2, 100), tx(3, 2, 3, 100)]
    for kind in ["mixer", "bridge", "dex"]:
        assert run(txs, [label(1, kind=kind), label(3)])["candidates"] == []
    assert run(txs, [label(3)], 2)["candidates"] == []
    assert run(txs, [label(2, "A"), label(3, "B")])["metrics"]["attributed_usd"] == 100


def test_weak_labels_cap_confidence():
    assert (
        run([tx(1, 0, 1, 100)], [label(1, confidence=0.1)])["candidates"][0]["score"]
        <= 10
    )


def test_missing_valuation_not_fabricated():
    a = run([tx(1, 0, 1, 100, usd=None)], [label(1)])
    assert a["metrics"]["valuation_coverage"] == 0
    assert a["candidates"][0]["traced_usd"] == 0
    assert a["candidates"][0]["components"]["interaction"]["points"] == 0


def test_origin_valuation_not_replaced_by_downstream_price():
    a = run([tx(1, 0, 1, 100, usd="100"), tx(2, 1, 2, 100, usd="900")], [label(2)])
    assert a["candidates"][0]["traced_usd"] == 100


def test_shared_edges_not_independent_support():
    a = run([tx(1, 0, 1, 100), tx(2, 1, 2, 50), tx(3, 1, 3, 50)], [label(2), label(3)])
    assert a["candidates"][0]["path_count"] == 2
    assert a["candidates"][0]["independent_paths"] == 1


def test_cycles_stop_without_reusing_traced_lot():
    assert not run(
        [tx(1, 0, 1, 100), tx(2, 1, 2, 100), tx(3, 2, 1, 100), tx(4, 1, 3, 100)],
        [label(3)],
    )["candidates"]


def test_empty_case():
    a = run([], [])
    assert a["metrics"]["valuation_coverage"] is None
    assert a["metrics"]["exposure_hhi"] is None
    assert a["graph"]["nodes"][0]["id"] == address(0)


@pytest.mark.parametrize(
    "change",
    [
        {"amount": "NaN"},
        {"amount": "-1"},
        {"usd_value": "Infinity"},
        {"timestamp": "2026-01-01T00:00:00"},
        {"transaction_type": "token"},
    ],
)
def test_invalid_evidence_rejected(change):
    data = tx(1, 0, 1, 100).model_dump()
    data.update(change)
    with pytest.raises(ValidationError):
        Transaction(**data)


def test_duplicates_and_cross_chain_rejected():
    t = tx(1, 0, 1, 100)
    with pytest.raises(ValidationError):
        run([t, t], [])
    with pytest.raises(ValidationError):
        InvestigationRequest(
            target=address(0), chain="bnb", mode="import", transactions=[t]
        )


def test_arbitrary_wallet_never_gets_demo():
    with pytest.raises(ValueError):
        SyntheticProvider().fetch(address(100), Chain.ethereum)


@pytest.mark.parametrize("chain", list(Chain))
def test_demo_chain_isolation(chain):
    txs, labels = SyntheticProvider().fetch(DEMO_TARGET, chain)
    assert all(t.chain == chain for t in txs)
    assert all(label.chain == chain for label in labels)


def test_tiny_remaining_balances_are_not_discarded():
    a = run(
        [
            tx(1, 0, 1, "0.000000000000000000000000000002"),
            tx(2, 1, 2, "0.000000000000000000000000000001"),
            tx(3, 1, 3, "0.000000000000000000000000000001"),
        ],
        [label(2, "A"), label(3, "B")],
    )
    assert len(a["candidates"]) == 2


def test_complexity_budget_fails_explicitly(monkeypatch):
    from app import engine

    monkeypatch.setattr(engine, "MAX_TRACE_OPERATIONS", 0)
    with pytest.raises(engine.TraceBudgetExceeded):
        run([tx(1, 0, 1, 100), tx(2, 1, 2, 100)], [label(2)])
