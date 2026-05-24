"""
Stage 1: Limit Order Book (Jane Street "Building an Exchange" talk, Part 5 of context).

Invariants encoded here:
- Bids sort HIGH -> LOW. Best bid is the highest price someone wants to buy at.
- Asks sort LOW  -> HIGH. Best ask is the lowest price someone will sell at.
- Price-time priority: at the same price, the OLDEST order fills first (FIFO per level).
- Price improvement goes to the AGGRESSOR: when a marketable order crosses the book,
  the trade executes at the RESTING order's price (the maker set the price first).
- Cancel must be O(1) via the "locate map" (dict[order_id -> Order]). The talk calls
  the order_id a "locate number" — really an array index handed back to the client.

Prices are integer TICKS, never floats — floats break equality and ordering.
"""
from collections import deque
from dataclasses import dataclass
from typing import Optional


Side = str  # "BUY" or "SELL"


@dataclass
class Order:
    order_id: int        # the "locate number"
    side: Side
    price: int           # integer ticks
    qty: int             # remaining qty (decremented as fills occur)
    participant: str     # e.g. "MSCO", "GSCO"
    seq: int             # exchange-assigned sequence number when accepted


@dataclass
class Trade:
    price: int
    qty: int
    aggressor_id: int    # order_id of the incoming (taker) order
    resting_id: int      # order_id of the order already on the book (maker)
    aggressor: str       # participant of the taker
    resting: str         # participant of the maker


class OrderBook:
    def __init__(self) -> None:
        self.bids: dict[int, deque[Order]] = {}   # price -> FIFO of resting buys
        self.asks: dict[int, deque[Order]] = {}   # price -> FIFO of resting sells
        self.orders: dict[int, Order] = {}        # the LOCATE MAP — O(1) cancel
        self._next_id = 1
        self._next_seq = 1

    def _new_id(self) -> int:
        oid = self._next_id
        self._next_id += 1
        return oid

    def _new_seq(self) -> int:
        s = self._next_seq
        self._next_seq += 1
        return s

    def best_bid(self) -> Optional[int]:
        return max(self.bids) if self.bids else None

    def best_ask(self) -> Optional[int]:
        return min(self.asks) if self.asks else None

    def add_limit_order(self, side: Side, price: int, qty: int, participant: str) -> tuple[int, list[Trade]]:
        """Submit a new limit order. Returns (order_id, list_of_resulting_trades)."""
        order = Order(
            order_id=self._new_id(),
            side=side,
            price=price,
            qty=qty,
            participant=participant,
            seq=self._new_seq(),
        )
        trades = self._match(order)

        # ------------------------------------------------------------------
        # TODO #1 — REST THE REMAINDER
        # ------------------------------------------------------------------
        # If `order.qty > 0` after _match returned, the order didn't fully fill.
        # The remainder needs to be added to the book AND registered in self.orders
        # so that a future cancel can find it in O(1).
        #
        # Steps:
        #   1. If order.qty == 0, do nothing (it fully filled, no remainder to rest).
        #   2. Otherwise:
        #        - if order.side == "BUY":  append to self.bids[order.price]
        #          (create an empty deque() at that price if the key doesn't exist yet)
        #        - else (SELL):             append to self.asks[order.price]
        #   3. Register the order: self.orders[order.order_id] = order
        #
        # Why: the talk hammers that the locate map is the ONLY way cancel can be O(1).
        # Skip step 3 and test_6 fails. Skip step 2 and test_1 / test_5 fail.
        # ------------------------------------------------------------------
        # ...your code here...

        return order.order_id, trades

    def cancel(self, order_id: int) -> bool:
        """Cancel a resting order.

        Returns True if cancelled, False if not found (already filled / already
        cancelled — this is the "cancel-reject" case from the bow-tie diagram
        we'll exercise properly in Stage 3).
        """
        # ------------------------------------------------------------------
        # TODO #2 — CANCEL
        # ------------------------------------------------------------------
        # Steps:
        #   1. If order_id not in self.orders -> return False (cancel-reject).
        #   2. order = self.orders[order_id]
        #   3. Pick the right side: book_side = self.bids if order.side == "BUY" else self.asks
        #   4. Remove `order` from the deque at book_side[order.price]:
        #        book_side[order.price].remove(order)        # deque supports .remove()
        #   5. If the deque is now empty, delete the price-level key entirely:
        #        if not book_side[order.price]: del book_side[order.price]
        #      (otherwise best_bid()/best_ask() can return a stale empty price!)
        #   6. del self.orders[order_id]
        #   7. Return True.
        # ------------------------------------------------------------------
        # ...your code here...
        return False

    def _match(self, incoming: Order) -> list[Trade]:
        """Match an incoming order against the opposite side of the book.

        Mutates `incoming.qty` (decrements as fills happen) and the resting orders
        / book structure. Returns the list of trades produced (possibly empty).
        """
        trades: list[Trade] = []

        if incoming.side == "BUY":
            # --------------------------------------------------------------
            # TODO #3 — BUY MATCHING LOOP
            # --------------------------------------------------------------
            # While the incoming BUY still has qty AND there's an ask AND the BUY is
            # willing to pay the best ask, consume liquidity from the ASK side.
            #
            # Loop condition (all three must hold):
            #   incoming.qty > 0
            #   self.best_ask() is not None
            #   incoming.price >= self.best_ask()
            #
            # Each iteration:
            #   best = self.best_ask()
            #   level = self.asks[best]                # FIFO deque of resting sells
            #   resting = level[0]                     # oldest first (price-time priority)
            #   fill_qty = min(incoming.qty, resting.qty)
            #   trade_price = resting.price            # *** PRICE IMPROVEMENT TO AGGRESSOR ***
            #   trades.append(Trade(
            #       price=trade_price, qty=fill_qty,
            #       aggressor_id=incoming.order_id, resting_id=resting.order_id,
            #       aggressor=incoming.participant, resting=resting.participant,
            #   ))
            #   resting.qty -= fill_qty
            #   incoming.qty -= fill_qty
            #   if resting.qty == 0:
            #       level.popleft()
            #       del self.orders[resting.order_id]      # remove from locate map
            #       if not level: del self.asks[best]      # drop empty price level
            # --------------------------------------------------------------
            # ...your code here...
            pass

        elif incoming.side == "SELL":
            # --------------------------------------------------------------
            # TODO #4 — SELL MATCHING LOOP
            # --------------------------------------------------------------
            # Mirror of TODO #3 against self.bids.
            #
            # Loop condition:
            #   incoming.qty > 0
            #   self.best_bid() is not None
            #   incoming.price <= self.best_bid()
            #
            # Each iteration: same shape as TODO #3 but use self.bids[best_bid()] and
            # again execute at trade_price = resting.price (the resting BUY's price).
            # --------------------------------------------------------------
            # ...your code here...
            pass

        return trades
