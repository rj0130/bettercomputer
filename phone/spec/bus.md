# The BC-Bus

The one connector standard every BC-1 module attaches through. No bespoke flex, no
module-specific pinout (`principles.md` #2; D-003). This file is the standard; per-bay lane and
rail allocation is data, in `phone/spec/device.yaml`, not repeated here.

## Connector family

- **0.35mm-pitch board-to-board, catalogue part, two-vendor minimum** (DP-03, D-003). Family is
  chosen in P8/U11 research when two vendors' datasheets confirm cycle rating and lane count
  simultaneously (BUS-005); until then this is `[UNVERIFIED]`.
- **Mating cycles:** every bay connector ≥ 500 cycles; the battery bay's power-only contacts
  ≥ 5,000 cycles, since a battery swap is expected far more often than any other module swap
  (BUS-004, MOD-004).
- **Keying:** each bay's connector is mechanically keyed to its module class so a module cannot
  be seated in the wrong bay, matching MOD-008 (a v1 module fits every v1 bay of its class).

## Pin groups (BUS-001)

Every connector carries a subset of these four groups; which subset is per-bay data in
`device.yaml`.

| Group | Carries | Notes |
|---|---|---|
| `power` | `VBAT`, `3V3`, `1V8` | Rail definitions and consumers are in `device.yaml`'s `rails:` list. Budgets are P5. |
| `identity-i2c` | One I2C bus | Every module's identity EEPROM (MOD-007) sits here, readable without powering the compute module. |
| `control-gpio` | Reset, interrupt, presence-detect lines | Presence-detect is what lets the OS notice a hot-swap (SW-003) without polling I2C. |
| `high-speed-lanes` | One or more of the lane groups below | A bay carries only the lane groups its module class needs; see `device.yaml` `bays[].lanes`. |

## Lane groups (BUS-002)

| Lane group | Protocol | Consumers (v1) |
|---|---|---|
| `DSI` | MIPI DSI | `display` |
| `CSI` | MIPI CSI | `camera-rear`, `sensor-front` |
| `USB3/PCIe` | USB 3.x or PCIe, module declares which in its descriptor | `port`, `radio` |

The `compute` bay is the bus host: its connector is the union of every lane group and every
rail, since the SoC on the compute module is the source of DSI/CSI and the root of USB/PCIe.
Every other bay carries only the lanes its own module class consumes.

A module that needs a signal not in this table triggers a **bus revision proposal** — a new row
here and in `device.yaml`, with a decision row in `project/decisions.md` — never a side cable or
a bay-specific pinout (`principles.md` #2). The `camera-rear` bay's optional second sensor
(CAM-001) is the first candidate for this if it ships.

## Power negotiation (BUS-003)

Each module declares its rail draw in its identity descriptor (MOD-007, SEC-002 for the signing
scheme). The OS enforces a per-bay power budget read from the descriptor, not a fixed allocation
baked into the frame — a future module of the same class that draws less leaves headroom; one
that draws more is refused power (never bricked, never silently starved) until the owner
approves it. Rail budgets themselves, and what "refuse" means at the regulator level, are P5
(`phone/hardware/electrical/power-tree.md`, U8).

## What this file does not decide

- The exact connector part number and pin-out diagram: P8/U11 research, then P5/U8
  (`phone/hardware/electrical/bus-pinout.md`).
- Rail voltages, current budgets, and regulator topology: P5/U8.
- Antenna feed lines for the `radio` bay: these do not travel on the BC-Bus; they are routed
  directly to keep-out zones fixed in the frame (RADIO-002, P5/U8).

## Source

BUS-001 through BUS-005 (`phone/design/requirements.md`); DP-03 (`decision-points.md`); D-003
(`project/decisions.md`).
