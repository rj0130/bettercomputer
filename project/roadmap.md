# Roadmap

Milestones for BC-1 and the platform that sells it. M0 is the only milestone that needs no
capital: everything in it is files, scripts and generated geometry. M1 onward needs money and
people; `project/asks.md` carries the ask when M0 closes.

Status: `pending` → `active` → `gated` (artifacts exist, gate check not yet run) → `passed`.

## M0 — Designed on paper and in code (no capital)

The exit test for M0: a competent hardware team could read this repo cold and start M1 without
asking what the product is, what its parts are, why each decision was made, or what to test first.

| Phase | Name | Question it answers | Gate artifacts | Status |
|---|---|---|---|---|
| P1 | Product definition & plan | What is BC-1, for whom, and in what order do we design it? | `phone/README.md`, `phone/design/principles.md`, `personas-and-jobs.md`, `requirements.md`, `design-path.md`, `decision-points.md`, `risk-register.md`, `project/plan.md` | active |
| P2 | System architecture | What are the bays, the bus, the rails, the envelope? | `phone/spec/device.yaml`, `phone/spec/bus.md`, `phone/docs/adr/001-compute-module.md`, `002-bc-bus.md` | pending |
| P3 | Module specifications & tools | What is each module, exactly, and does it fit, power and cost out? | `phone/spec/modules/*.yaml`, `phone/tools/{validate_spec,fit_check,power_budget,bom_rollup,repairability,report}.py`, `phone/tests/` | pending |
| P4 | Mechanical design | What does the frame look like, and can the modules be assembled and removed with one tool? | `phone/hardware/cad/*.py`, STEP/STL in `phone/build/`, exploded SVG, `phone/hardware/fasteners-and-tolerances.md` | pending |
| P5 | Electrical architecture | How does power and data reach every module, and where are the antennas? | `phone/hardware/electrical/{power-tree,block-diagram,bus-pinout,antenna-keepouts}.md` | pending |
| P6 | Software architecture | What runs, how does it learn what modules are present, and how is it updated for ten years? | `phone/software/{os-stack,module-descriptor,update-model,boot-and-security}.md` | pending |
| P7 | Thermal & battery-life models | Does it stay cool and last a day? | `phone/tools/thermal.py`, scenarios in `power_budget.py`, `phone/docs/thermal-and-battery.md` | pending |
| P8 | Research consolidation | Which real parts and rules does this design lean on, with sources? | `phone/docs/research/00-index.md` + one file per topic, all with `as-of` dates | pending |
| P9 | DFM, regulatory, repairability | Can it be made, certified and scored? | `phone/hardware/dfm.md`, `phone/docs/regulatory-path.md`, `phone/build/repairability.md` | pending |
| P10 | Cost & unit economics | What does it cost to build, and what does the circular model earn on it? | `phone/hardware/bom/bom.csv`, `phone/build/bom-rollup.md`, `business/unit-economics.md` | pending |
| P11 | Platform integration | How do the phone's modules, BOM and recipes flow through the `src/` services? | `business/platform-integration.md`, sample recipe JSON, data-model deltas for `src/` | pending |
| P12 | Integrated build plan | What does M1 do first, with how much, and what could kill it? | `project/build-plan.md`, updated `project/asks.md` with the capital ask | pending |

Phases P4, P5, P6 and P7 can run in parallel once P2 and P3 are passed. P8 runs alongside
everything and feeds P9/P10. P11 needs P3 (module IDs and BOM) only.

## M1 — Validated (needs capital: people, dev kits, a mock-up shop)

| Phase | Name | Exit |
|---|---|---|
| M1.1 | Form mock-ups | 3D-printed frame + weighted dummy modules; hand-feel and assembly time measured |
| M1.2 | Compute bring-up | SoC dev kit boots the mainline image; module descriptor read over I2C from a bench EEPROM |
| M1.3 | Bus proof | Two modules hot-swapped over a real board-to-board connector 500 times without failure |
| M1.4 | Display + battery proof | Display module on the bus at full refresh; battery module swap under load |
| M1.5 | Regulatory pre-scan | Pre-compliance EMC on the bring-up board; antenna efficiency measured in the mock-up frame |

## M2 — Engineered (EVT → DVT → PVT)

Standard hardware gates. EVT: does it work. DVT: does it survive (drop, thermal, cycle). PVT: can
the line build it at yield. Each is a phase with its own test plan; not detailed until M1 passes.

## M3 — Pilot run + circular loop live

A small pilot run (size decided in P12) sold through the `src/` storefront; first devices
returned, graded, refactored and resold through the platform. The circular loop is the product.
