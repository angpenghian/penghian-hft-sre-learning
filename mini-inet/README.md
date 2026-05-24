# mini-inet

A simulated exchange built from first principles in Python, replicating the
architecture from Jane Street's "Building an Exchange" talk.

Five build stages, each mapping to a lesson from the talk and shipping with a
write-up and a visual.

| Stage | Status | What it teaches | Talk concept |
|-------|--------|-----------------|--------------|
| 1 | scaffolded, TODOs to fill | Limit order book + matching engine, price-time priority, price-improvement-to-aggressor, cancel as O(1) via the locate map | the order book + matching slides |
| 2 | planned | Ordered event stream + state-machine replication: replay consumers; kill one, replay from seq 0, identical state | "shoot it in the head" SMR design |
| 3 | planned | Per-topic sequence numbers + optimistic concurrency; reproduce the cancel-vs-execution bow-tie race | the bow-tie diagram |
| 4 | planned | Real TCP Ports + retransmitter + UDP multicast bus + passive ME failover | multicast bus + RT + secondary ME |
| 5 | planned | Cancel Fairy + Auction Fairy offloaded consumers + latency measurement (HdrHistogram, cache-miss hot path) | offloaded fairies + perf lessons |

## Stage 1 — order book + matching engine

Files:

- [`stage1_orderbook/orderbook.py`](stage1_orderbook/orderbook.py) — `Order`, `Trade`, `OrderBook`. Four `TODO` blocks for the learner to fill in (resting, cancel, BUY match loop, SELL match loop).
- [`stage1_orderbook/matching_engine.py`](stage1_orderbook/matching_engine.py) — wraps the book in a global-sequenced event stream. The seed of Stage 2's SMR design.
- [`stage1_orderbook/test_orderbook.py`](stage1_orderbook/test_orderbook.py) — six tests encoding the talk's scenarios: resting / cross / price-improvement / price-time priority / partial fill / cancel-then-reject.

Run the tests:

```
cd mini-inet/stage1_orderbook
python -m pytest test_orderbook.py -v
```

Run the demo (the MSCO/GSCO scenario from the talk):

```
python matching_engine.py
```

Expected output:

```
seq=  1  ACK             {'order_id': 1, 'side': 'BUY',  'price': 3329, 'qty': 500, 'participant': 'MSCO'}
seq=  2  ACK             {'order_id': 2, 'side': 'SELL', 'price': 3329, 'qty': 500, 'participant': 'GSCO'}
seq=  3  TRADE           {'price': 3329, 'qty': 500, 'aggressor_id': 2, 'resting_id': 1, 'aggressor': 'GSCO', 'resting': 'MSCO'}
```

## Visual

The Stage 1 animation lives at
[`../docs/mini-inet/order_flow.html`](../docs/mini-inet/order_flow.html) — when
GitHub Pages is enabled on `main` → `/docs`, it's served at
`/penghian-hft-sre-learning/mini-inet/order_flow.html`.
