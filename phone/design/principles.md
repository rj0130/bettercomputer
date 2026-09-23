# Design principles

Ranked. When two conflict, the higher one wins. Each has a trade-off rule so that a session can
apply it without asking.

## 1. Owner-replaceable, one tool, no collateral damage
Every module comes out and goes back in with a Torx T5 (battery: no tool) without disturbing any
other module. **Rule:** a change that adds a second fastener type, an adhesive, or a removal order
dependency is rejected unless a decision row says why.

## 2. One bus, many bodies
Modules attach through the BC-Bus only. No bespoke flex, no module-specific pinout. **Rule:** a
module that needs a signal the bus does not carry triggers a bus revision proposal, not a side
cable.

## 3. Longevity over performance
Ten years of software and parts is the target. **Rule:** a part is chosen for its support horizon
(mainline drivers, industrial availability window) before its benchmark; a faster part with a
vendor-only kernel loses.

## 4. Determinism over prose
Fit, mass, power, cost, repairability are computed from the spec by scripts. **Rule:** a claim
about the phone that a script could check is not written in prose; it is added to the spec and
the script.

## 5. Honest numbers
Every figure is sourced or flagged. **Rule:** a number without a source carries [UNVERIFIED]; a
number from a competitor teardown is labelled as such; no part number is invented.

## 6. Circular by construction
The refurbish line is a first-class user. **Rule:** every module carries machine-readable identity
and a service class; every design choice states what it does to grading, refactoring and resale.

## 7. Good enough is the spec
BC-1 is a mid-range phone that lasts, not a flagship. **Rule:** a feature that raises BOM above
the ceiling in `device.yaml` needs a decision row that raises the ceiling first.

## What we explicitly give up
- Thinness below about 9.5 mm. Bays and connectors cost millimetres.
- IP68. A user-swappable battery and screw-mounted display make IP54 the honest target; gaskets
  on every bay lid may reach IP55–IP57 and are tracked as a decision point.
- Best-in-class camera. A good, replaceable camera module beats a great glued one.
- The newest SoC. A well-supported one from two years ago, on a swappable module, is the point.
