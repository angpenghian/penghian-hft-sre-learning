"""
Stage 1 tests — encode the 6 scenarios from the Jane Street talk.

Run from inside this directory:
    python -m pytest test_orderbook.py -v
"""
from orderbook import OrderBook


def test_1_resting_order_no_trade():
    """A lone BUY at 100 just rests on the book — no trade, best_bid is 100."""
    book = OrderBook()
    oid, trades = book.add_limit_order("BUY", 100, 10, "MSCO")
    assert trades == []
    assert book.best_bid() == 100
    assert book.best_ask() is None
    assert oid in book.orders, "order must be registered in the locate map"


def test_2_marketable_sell_crosses():
    """BUY 10@100 rests; SELL 10@100 arrives and crosses — one trade for 10@100."""
    book = OrderBook()
    book.add_limit_order("BUY", 100, 10, "MSCO")
    _oid, trades = book.add_limit_order("SELL", 100, 10, "GSCO")
    assert len(trades) == 1
    t = trades[0]
    assert t.price == 100
    assert t.qty == 10
    assert t.aggressor == "GSCO"
    assert t.resting == "MSCO"
    # Book is empty after the cross.
    assert book.best_bid() is None
    assert book.best_ask() is None


def test_3_price_improvement_to_aggressor():
    """BUY 10@101 rests; SELL 10@100 arrives.

    The seller would have accepted 100, but the resting buy is offering 101.
    Trade executes at the RESTING price = 101. The aggressor (seller) gets price
    improvement. This is the Instinet cautionary tale from the talk — improvement
    must go to the aggressor, not to resting hidden orders, or you incentivize
    gaming.
    """
    book = OrderBook()
    book.add_limit_order("BUY", 101, 10, "MSCO")
    _oid, trades = book.add_limit_order("SELL", 100, 10, "GSCO")
    assert len(trades) == 1
    assert trades[0].price == 101, "price improvement must go to the aggressor"


def test_4_price_time_priority():
    """Two BUYs at 100 (MSCO first, GSCO second). A SELL 10@100 fills MSCO, not GSCO."""
    book = OrderBook()
    book.add_limit_order("BUY", 100, 10, "MSCO")
    book.add_limit_order("BUY", 100, 10, "GSCO")
    _oid, trades = book.add_limit_order("SELL", 100, 10, "JPMC")
    assert len(trades) == 1
    assert trades[0].resting == "MSCO", "oldest order at a price must fill first"
    # GSCO still on the book at 100.
    assert book.best_bid() == 100


def test_5_partial_fill_rests_remainder():
    """BUY 10@100 rests; SELL 15@100 partially fills 10, leaves 5 resting on the ASK side."""
    book = OrderBook()
    book.add_limit_order("BUY", 100, 10, "MSCO")
    sell_id, trades = book.add_limit_order("SELL", 100, 15, "GSCO")
    assert len(trades) == 1
    assert trades[0].qty == 10
    # Leftover 5 sits on the ask side at 100.
    assert book.best_ask() == 100
    assert sell_id in book.orders
    assert book.orders[sell_id].qty == 5


def test_6_cancel_then_reject():
    """Cancel a resting order, then try to cancel again -> second call returns False.

    This is the cancel-reject case (the bow-tie diagram from the talk, which we'll
    properly exercise in Stage 3 with topic sequence numbers).
    """
    book = OrderBook()
    oid, _ = book.add_limit_order("BUY", 100, 10, "MSCO")
    assert book.cancel(oid) is True
    assert book.best_bid() is None, "cancelled level must be gone, not stale-empty"
    assert book.cancel(oid) is False, "second cancel must reject"
