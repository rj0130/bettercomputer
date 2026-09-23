# Requirements

IDs are stable; never renumber. Source tags: `[VISION]` from `PRODUCT_VISION.md`; `[PRINCIPLE]`
from `principles.md`; `[JTBD-n]` from `personas-and-jobs.md`; `[REG-CLAIM]` a regulatory line to
verify against the instrument in P8; `[PROPOSED]` added here, Rae may veto; `[TARGET]` a number
to validate, not a fact. Status: `pending` → `planned (Pn)` → `specified` → `verified`.

## PRD — Product

| ID | Requirement | Source | Phase | Status |
|---|---|---|---|---|
| PRD-001 | BC-1 is a general-purpose smartphone: calls, data, camera, apps; not a niche device | [VISION] | P1 | pending |
| PRD-002 | Ten-year design life for the chassis; every other part replaceable within it | [PRINCIPLE 3] [JTBD-1..3] | P2 | pending |
| PRD-003 | BOM ceiling USD 260, retail target USD 549 (default of Q2) | [PROPOSED] [TARGET] | P10 | pending |
| PRD-004 | Envelope target ≤ 152 × 73 × 10 mm, mass ≤ 215 g | [PROPOSED] [TARGET] | P2 | pending |
| PRD-005 | Ingress target IP54 baseline; IP55+ tracked as decision DP-09 | [PRINCIPLE 7] | P4/P9 | pending |

## MOD — Modularity

| ID | Requirement | Source | Phase | Status |
|---|---|---|---|---|
| MOD-001 | The phone is a frame plus named bays; each bay accepts exactly one module class | [PRINCIPLE 1] | P2 | pending |
| MOD-002 | Module classes v1: compute, display, battery, rear camera, front sensor, port (USB-C + speaker), radio front-end, chassis frame | [PROPOSED] | P2 | pending |
| MOD-003 | Compute module (SoC + RAM + storage) is removable and upgradable without changing any other module | [JTBD-3] | P2 | pending |
| MOD-004 | Battery removable without tools in under 60 s; every other module with one Torx T5 in under 10 min | [JTBD-1,2] [TARGET] | P4 | pending |
| MOD-005 | Removing any module disturbs no other module (no removal-order dependencies except the back cover) | [PRINCIPLE 1] | P4 | pending |
| MOD-006 | Zero adhesive except display cover-glass lamination | [PRINCIPLE 1] | P4 | pending |
| MOD-007 | Every module carries an identity descriptor readable without power to the compute module (I2C EEPROM on the bus) | [JTBD-4] | P5/P6 | pending |
| MOD-008 | Bay classes are versioned; a v1 module fits every v1 bay of its class in any BC-1 frame revision | [JTBD-6] | P2 | pending |

## BUS — The BC-Bus

| ID | Requirement | Source | Phase | Status |
|---|---|---|---|---|
| BUS-001 | One board-to-board connector family for all modules; pin groups: power (VBAT, 3V3, 1V8), identity I2C, control GPIO, one or more high-speed lane groups | [PRINCIPLE 2] | P2 | pending |
| BUS-002 | High-speed lanes carry MIPI DSI (display), MIPI CSI (cameras), USB 3.x / PCIe (port, radio); allocation per bay is fixed in `device.yaml` | [PROPOSED] | P2/P5 | pending |
| BUS-003 | Power negotiation: a module declares its rail draw in its descriptor; the OS enforces a per-bay budget | [PROPOSED] | P5/P6 | pending |
| BUS-004 | Rated for ≥ 500 mating cycles (repair) on every bay; battery contacts ≥ 5,000 | [TARGET] | P3/P9 | pending |
| BUS-005 | The connector is a catalogue part from at least two vendors, never custom | [PRINCIPLE 2] | P8 | pending |

## MECH, PWR, DISP, CAM, RADIO — Hardware

| ID | Requirement | Source | Phase | Status |
|---|---|---|---|---|
| MECH-001 | Frame is the structural and antenna-carrying part; modules add no structural load path | [PROPOSED] | P4 | pending |
| MECH-002 | Back cover is tool-less (latch) and gives access to every bay | [JTBD-1] | P4 | pending |
| MECH-003 | Drop target: survives 1.0 m onto concrete, all faces, with any module set installed | [TARGET] | P9 | pending |
| PWR-001 | Battery ≥ 4,000 mAh nominal in a hard-shell pouch pack with a standard footprint | [PROPOSED] [TARGET] | P3 | pending |
| PWR-002 | Battery retains ≥ 80 % capacity after 800 cycles | [REG-CLAIM] EU 2023/1670 | P8 | pending |
| PWR-003 | USB-C PD charging ≥ 20 W; charger not in the box | [PROPOSED] | P5 | pending |
| PWR-004 | Screen-on time ≥ 7 h mixed use at 200 nits (model in P7, measure in M1) | [TARGET] | P7 | pending |
| DISP-001 | 6.1-inch class, ≥ 1080p, OLED or LTPS LCD; screw-mounted module, MIPI DSI over the bus | [PROPOSED] | P3 | pending |
| DISP-002 | Display module includes touch, cover glass, and its own descriptor; replaced as one part | [JTBD-2] | P3 | pending |
| CAM-001 | Rear camera module: one main sensor ≥ 48 MP class with OIS optional; a second sensor is a variant, not a requirement | [PROPOSED] | P3 | pending |
| CAM-002 | Front sensor module: camera + ambient/proximity; separate from the display so a screen swap needs no camera calibration | [PROPOSED] | P3 | pending |
| RADIO-001 | 5G sub-6 + LTE, Wi-Fi 6, BT 5.x, GNSS, NFC; band set per region SKU via the radio front-end module | [PROPOSED] | P5 | pending |
| RADIO-002 | Antenna keep-outs are documented in the CAD and fixed across module swaps | [PROPOSED] | P4/P5 | pending |

## SW, SEC — Software and security

| ID | Requirement | Source | Phase | Status |
|---|---|---|---|---|
| SW-001 | Mainline Linux kernel; no vendor fork; all v1 modules have upstream or upstreamable drivers | [PRINCIPLE 3] [JTBD-5] | P6/P8 | pending |
| SW-002 | Two supported images on the same kernel: Linux (Debian/postmarketOS-class) and AOSP | [PROPOSED] | P6 | pending |
| SW-003 | Module discovery: OS reads each descriptor at boot and on hot-swap, loads the matching device-tree overlay | [JTBD-4] | P6 | pending |
| SW-004 | Update model: A/B OS updates, per-module firmware updates with rollback; ≥ 10 years of security updates as a company commitment | [REG-CLAIM] [PROPOSED] | P6 | pending |
| SEC-001 | Owner-unlockable bootloader; owner can enrol their own signing key; vendor keys removable | [JTBD-5] | P6 | pending |
| SEC-002 | Descriptors are signed; unsigned or unknown modules warn, never block | [PRINCIPLE 6] | P6 | pending |
| SEC-003 | No per-device part pairing; any module of a class works in any frame | [JTBD-6] | P6 | pending |

## REG, BIZ — Regulatory and business

| ID | Requirement | Source | Phase | Status |
|---|---|---|---|---|
| REG-001 | EU ecodesign for smartphones (2023/1670) and the EU battery regulation are the design baseline; US FCC and CE radio certification path documented | [REG-CLAIM] | P8/P9 | pending |
| REG-002 | Spare parts availability ≥ 7 years after last unit sold | [REG-CLAIM] | P9 | pending |
| REG-003 | A repairability score computed by the same rubric as the EU index, reproducible from the spec | [PRINCIPLE 4] | P3/P9 | pending |
| BIZ-001 | Every module maps to an Inventory SKU and every assembly step to an Operations work-order step in `src/` | [VISION] [JTBD-8] | P11 | pending |
| BIZ-002 | Grading a returned device is a scan of descriptors plus a script, not a technician's judgement | [JTBD-4] | P11 | pending |
| BIZ-003 | Module spec files double as R&D recipes in the `src/RnD.Api` document store | [VISION] | P11 | pending |
