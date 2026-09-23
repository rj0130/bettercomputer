# Glossary

One line each. Point at the file that teaches the term.

- **BC-1** — the BetterComputer phone, working name. `phone/README.md`.
- **BC-Bus** — the single board-to-board connector standard every BC-1 module uses. `phone/spec/bus.md`.
- **Bay** — a named volume in the chassis frame that accepts exactly one module class. `phone/spec/device.yaml`.
- **Module** — a field-replaceable unit with its own YAML spec, identity EEPROM and BC-Bus connector. `phone/spec/modules/`.
- **Compute module** — the SoC + RAM + storage carrier; the upgradable brain. `phone/docs/adr/001-compute-module.md`.
- **Identity EEPROM** — the I2C descriptor chip on every module; signed, tells the OS what the module is. `phone/software/module-descriptor.md`.
- **Fit check** — the script that proves every module fits its bay with clearance. `phone/tools/fit_check.py`.
- **Power tree** — the diagram of rails from battery to every load. `phone/hardware/electrical/power-tree.md`.
- **Repairability score** — the deterministic rubric score computed from the spec. `phone/tools/repairability.py`.
- **REQ-id** — a stable requirement identifier. `phone/design/requirements.md`.
- **Unit (U-n)** — one commit-sized piece of work tracked in `project/state.md`.
- **[UNVERIFIED] / [CONTESTED]** — evidence flags; see `CLAUDE.md`.
- **Platform** — the .NET services in `src/` that sell, refurbish and track devices. `TECHNICAL_DESIGN.md`.
