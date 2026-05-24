# penghian-hft-sre-learning

Public lab notes from a 12-week low-latency Linux + exchange-internals study plan,
built while transitioning from cloud/DevOps SRE work into HFT / trading-infra SRE
roles in APAC.

Author: **Penghian Ang** — Singapore. Previously: Tencent (PUBG Mobile global
production, 6,000+ VMs / 4–10M DAU), Crypto.com (blockchain node infra across
9 protocols), Coinbase (Cold Storage Engineer III, n8n compliance pipelines).

## Live demos (GitHub Pages)

- **mini-inet Stage 1 — order flow through a matching engine**:
  [order_flow.html](docs/mini-inet/order_flow.html) (visual)

> If you're reading this on GitHub, the Pages site lives at
> `https://<user>.github.io/penghian-hft-sre-learning/` once Pages is enabled
> on `main` → `/docs`.

## Projects

### `mini-inet/` — a simulated exchange built from first principles

A Python implementation of the architecture described in Jane Street's
"Building an Exchange" talk: single in-memory matching engine, per-client TCP
Ports with sequenced flow control, an internal UDP multicast bus, deterministic
state-machine replication so any consumer can be "shot in the head" and
rebuilt by replaying the sequenced stream from seq 0, and a passive secondary
ME listening to the primary's output for failover.

Built in stages — each stage maps to a lesson from the talk and has its own
write-up and visual. See [mini-inet/README.md](mini-inet/README.md).

## Why this exists

To close a specific gap: deep Linux performance, kernel-bypass networking, and
exchange-internals literacy — the things that don't come from running a SaaS
cluster but do come up in HFT SRE interviews. The lab runs on a Hetzner AX42
(~€46/mo) with bursts to AWS `c5n.metal` for NUMA / 100GbE / DPDK work.

The portfolio is honest about what a cloud box cannot replicate — Solarflare
Onload, FPGA pre-trade risk, venue-grade PTP grandmasters, real co-location.
Those are the gaps to ramp on in the right environment, not pretend to have
solved at home.
