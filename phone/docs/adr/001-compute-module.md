# ADR-001: Core compute is a removable module

**Status:** PROPOSED (D-007, `project/decisions.md`) — Rae may veto.
**Date:** 2026-09-22

## Context

MOD-003 requires the SoC, RAM and storage to be upgradable without touching the chassis,
display or battery (JTBD-3). Every mainstream phone today solders the SoC to the mainboard,
which is exactly the choice that makes a phone's silicon its shortest-lived part: the rest of
the device (frame, display, battery, cameras) frequently outlasts the SoC's platform support
window by years. Principle 3 (longevity over performance) makes this ADR's answer a design
requirement, not an optimization.

## Decision

The SoC, RAM and storage live on one small removable carrier board — the **compute
module** — that plugs into the `compute` bay over the BC-Bus host connector
(`phone/spec/device.yaml`, `phone/spec/bus.md`). The compute module is the bus host: its
connector carries every lane group (`DSI`, `CSI`, `USB3/PCIe`) and every rail (`VBAT`, `3V3`,
`1V8`), because the SoC is the source of the display/camera lanes and the root of USB/PCIe.

Consequences of "host" status:
- A future compute module revision must still drive the same lane groups at the same bay
  footprint (42.0 × 30.0 × 3.4 mm, `device.yaml`), or it is a new bay class, not a drop-in
  upgrade — this is the boundary MOD-008 draws.
- The compute module carries its own identity descriptor (MOD-007) like every other module, even
  though it is electrically the host; the OS reads it the same way over `identity-i2c`.
- SoC selection itself (DP-04, currently a Qualcomm QCM6490-class part per D-008) is a separate,
  narrower decision this ADR does not reopen — this ADR is about the module boundary, not the
  silicon inside it.

## Alternatives considered

| Alternative | Why not |
|---|---|
| SoC soldered to a shared mainboard with everything else | Fails MOD-003 outright; the one part every owner most wants to upgrade becomes the one part they cannot. |
| Compute module carries only the SoC+RAM, storage stays on the mainboard | Splits "what changes together" — a storage failure or capacity upgrade would then require a mainboard swap, reintroducing a removal-order dependency principle 1 forbids. |
| Two-tier bus (a slow shared bus plus a dedicated high-speed compute-to-display trace) | Violates principle 2 (one bus, many bodies) for no fit or cost benefit at this stage; revisit only if P5 electrical work finds the single-bus host topology cannot meet DSI/CSI signal integrity at the connector's mating-cycle-rated pitch. |

## Consequences

- **Positive:** the phone's longest-lived and shortest-lived parts are decoupled; a compute
  module refresh is the circular-tech platform's highest-value SKU (BIZ-001).
- **Negative:** the compute bay's connector is the most electrically demanding one on the bus
  (every lane group, at 500+ mating cycles) — this is the hardest connector-sourcing constraint
  BUS-005 has to clear, and P5/U8 should treat it as the long-pole item, not an afterthought.
- **Open:** whether DSI/CSI signal integrity survives a 0.35mm-pitch connector at the compute
  bay's lane count is `[UNVERIFIED]` until P5 does the electrical budget; if it does not, this
  ADR's bay footprint or the connector family choice (DP-03) is revisited, not the module
  boundary itself.

## Source

MOD-003, MOD-007, MOD-008, BUS-001, BUS-002, DP-04; `principles.md` #2, #3; D-007, D-008.
