# ADR-002: One connector standard for every module — the BC-Bus

**Status:** PROPOSED (D-003, `project/decisions.md`) — Rae may veto.
**Date:** 2026-09-22

## Context

BC-1 is a frame plus named bays, each accepting exactly one module class (MOD-001). If each bay
used a connector matched to its module's own needs, a display connector would differ from a
camera connector, a radio connector, a battery connector — and every new module design would be
free to invent a new pinout. That is exactly the bespoke-flex failure mode principle 2 rules
out: a part the owner cannot source because no one else uses that connector.

## Decision

Every bay uses the **same connector family** (BUS-001, BUS-005): a catalogue board-to-board part
available from at least two vendors, at 0.35mm pitch, rated for ≥ 500 mating cycles on every bay
and ≥ 5,000 on the battery bay's power contacts (BUS-004). Every connector instance carries a
subset of four fixed pin groups — `power`, `identity-i2c`, `control-gpio`, `high-speed-lanes` —
and a bay's module class determines which lane groups (`DSI`, `CSI`, `USB3/PCIe`) it gets, not a
custom pin assignment. The full standard is `phone/spec/bus.md`; per-bay allocation is data in
`phone/spec/device.yaml`, kept out of this ADR so the allocation can change without reopening the
decision.

A module needing a signal outside this table requires a **bus revision** — a new row in
`bus.md` and `device.yaml` plus a decision row — not a side cable (principle 2's rule, restated
here because it is this ADR's entire point).

## Alternatives considered

| Alternative | Why not |
|---|---|
| Per-module-class connector families (e.g. FPC for display, a separate B2B for compute) | Multiplies the connector-sourcing problem by module count; fails BUS-005's two-vendor rule for the smaller-volume classes and reopens principle 2's bespoke-flex failure for any class whose connector goes end-of-life. |
| A backplane with slots (PCIe-card style) | Adds a rigid backplane PCB spanning the whole envelope, which competes with the battery and display bays for the thinnest dimension (11.8mm) and buys nothing the flat bay layout does not already give a 152.4 × 73.2mm frame. |
| Wireless intra-device links for low-bandwidth modules (e.g. sensor-front) | Adds a radio, power, and pairing-security surface to save a handful of pins on the smallest bay; the bus's fixed pin groups already reserve `identity-i2c` and `control-gpio` cheaply. |

## Consequences

- **Positive:** one connector family to qualify, stock, and repair-shop-source, ever, for the
  ten-year design life (PRD-002); a module class's bay is defined once in `device.yaml` and every
  module of that class fits it (MOD-008).
- **Negative:** the connector family must satisfy the compute bay's full lane-group superset
  (ADR-001) at the same pitch and cycle rating as the simplest bay (sensor-front); this is a
  harder single connector to qualify than several specialized ones would each be individually.
- **Open:** the connector family itself is `[UNVERIFIED]` (DP-03) until two vendors' datasheets
  confirm cycle rating and lane count together — this is P8/U11's job, and the long-pole item for
  P5's electrical sign-off, same as noted in ADR-001.

## Source

MOD-001, MOD-008, BUS-001 through BUS-005; `principles.md` #2; D-003; `phone/spec/bus.md`.
