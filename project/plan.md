# Plan — the units of work

One unit = one commit-sized piece of work with an acceptance check. A cold-started session picks
the first unit whose status is `next` and whose dependencies are `done`. Update the status here
and the mirror table in `state.md` when a unit closes. Phases refer to `roadmap.md`.

| Unit | Phase | Produces | Acceptance | Depends on | Status |
|---|---|---|---|---|---|
| U1 | P1 | `CLAUDE.md`, `project/`, `.gitignore`, `phone/tools/check.py` | checker passes | — | done |
| U2 | P1 | `roadmap.md`, `design-path.md`, `phone/README.md`, `principles.md`, `personas-and-jobs.md`, `requirements.md`, `decision-points.md`, `risk-register.md`, this file | every REQ has a source tag and a phase; every DP has a closing condition | U1 | done |
| U3 | P2 | `phone/spec/device.yaml` (envelope, bays with dims and clearances, bus lane allocation per bay, rails, ceilings), `phone/spec/bus.md`, `phone/docs/adr/001-compute-module.md`, `002-bc-bus.md` | `validate_spec.py` (U4) parses it; bay volumes + structure ≤ envelope | U2 | next |
| U4 | P3 | `phone/tools/specload.py` (stdlib YAML subset loader), `validate_spec.py`, `fit_check.py`, `phone/tests/test_tools.py` | tests pass; fit check reports every bay | U3 | pending |
| U5 | P3 | `phone/spec/modules/{compute,display,battery,camera-rear,sensor-front,port,radio,frame}.yaml` | validate + fit pass for all eight | U4 | pending |
| U6 | P3 | `power_budget.py` (scenarios: idle, screen-on, video, 5G data), `bom_rollup.py`, `repairability.py`, `report.py` → `phone/build/*.md` | reports generate with zero failures; BOM vs ceiling stated | U5 | pending |
| U7 | P4 | `phone/hardware/cad/frame.py` (CadQuery from `device.yaml`), `modules.py` dummies, `exploded.py` SVG, `gen_cad.py` driver → `phone/build/*.step,*.stl,*.svg`; `phone/hardware/fasteners-and-tolerances.md` | STEP exports; no bay collision; assembly order listed | U5 | pending |
| U8 | P5 | `phone/hardware/electrical/{power-tree,block-diagram,bus-pinout,antenna-keepouts}.md` | every rail has source + budget; every module draw ≤ bay allocation | U5 | pending |
| U9 | P6 | `phone/software/{os-stack,module-descriptor,update-model,boot-and-security}.md`, `descriptor.schema.json`, sample descriptors | schema validates samples (stdlib json check) | U5 | pending |
| U10 | P7 | `phone/tools/thermal.py`, `phone/docs/thermal-and-battery.md` | estimates with assumptions listed and flagged | U6 | pending |
| U11 | P8 | `phone/docs/research/00-index.md`, `01-soc-candidates.md`, `02-battery-and-cells.md`, `03-regulation-eu-ecodesign.md`, `04-display-modules.md`, `05-connectors.md`, `06-comparable-devices.md` | every file has `as-of`; every number sourced or flagged; checker enforces | U2 | pending (parallel) |
| U12 | P9 | `phone/hardware/dfm.md`, `phone/docs/regulatory-path.md`, repairability report reviewed | no "unknown" rubric fields | U6, U7, U11 | pending |
| U13 | P10 | `phone/hardware/bom/bom.csv`, `business/unit-economics.md` | BOM ≤ ceiling or a decision row | U6, U11 | pending |
| U14 | P11 | `business/platform-integration.md`, `business/recipes/sample-recipe.json`, data-model deltas for `src/` | recipe JSON validates against the documented schema | U5 | pending |
| U15 | P12 | `project/build-plan.md`, `project/asks.md` capital ask | Rae can decide on it | U7–U14 | pending |

## Working rules for a unit
1. Start: `python3 phone/tools/check.py`; read the mailbox (see `CLAUDE.md` cold start).
2. Do the unit. Prose that a script could check goes in the spec and the script instead.
3. End: checker, tests, update `state.md` mirror + this table, log line in `project/log/`, commit.
