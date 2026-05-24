"""
Stage 1 -> Stage 2 seed: wrap the OrderBook in a Matching Engine that emits a
single SEQUENCED, totally-ordered event stream.

Every event has a global seq number. In Stage 2 we'll add consumers (MD, Drop,
TradeReporter) that REPLAY this stream deterministically to rebuild their state
from seq 0. This is the foundation of the talk's "state machine replication"
design — the stream IS the source of truth; any consumer can be "shot in the
head" and rebuilt by replaying. The secondary/passive ME (Stage 4) listens to
this same output stream, runs identical code, and can fail over.
"""
from dataclasses import dataclass
from typing import Any

from orderbook import OrderBook


@dataclass
class Event:
    seq: int
    kind: str              # "ACK" | "TRADE" | "CANCEL_ACK" | "CANCEL_REJECT"
    payload: dict[str, Any]


class MatchingEngine:
    def __init__(self) -> None:
        self.book = OrderBook()
        self._next_seq = 1
        self.stream: list[Event] = []   # append-only — the totally-ordered log

    def _emit(self, kind: str, payload: dict[str, Any]) -> Event:
        ev = Event(seq=self._next_seq, kind=kind, payload=payload)
        self._next_seq += 1
        self.stream.append(ev)
        return ev

    def submit(self, side: str, price: int, qty: int, participant: str) -> list[Event]:
        order_id, trades = self.book.add_limit_order(side, price, qty, participant)
        events = [self._emit("ACK", {
            "order_id": order_id, "side": side, "price": price,
            "qty": qty, "participant": participant,
        })]
        for t in trades:
            events.append(self._emit("TRADE", {
                "price": t.price, "qty": t.qty,
                "aggressor_id": t.aggressor_id, "resting_id": t.resting_id,
                "aggressor": t.aggressor, "resting": t.resting,
            }))
        return events

    def cancel(self, order_id: int) -> Event:
        ok = self.book.cancel(order_id)
        return self._emit(
            "CANCEL_ACK" if ok else "CANCEL_REJECT",
            {"order_id": order_id},
        )

    def dump_stream(self) -> None:
        for ev in self.stream:
            print(f"seq={ev.seq:>3}  {ev.kind:<14}  {ev.payload}")


if __name__ == "__main__":
    # Demo from the talk: MSCO rests BUY 500@3329; GSCO sells 500@3329.
    # Expected stream: ACK(buy), ACK(sell), TRADE(500@3329, aggressor=GSCO).
    me = MatchingEngine()
    me.submit("BUY", 3329, 500, "MSCO")
    me.submit("SELL", 3329, 500, "GSCO")
    me.dump_stream()
