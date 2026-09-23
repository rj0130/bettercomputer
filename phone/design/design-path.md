# The design path for a modular hardware product

The order in which BC-1 is designed before anything is fabricated, as gated stages. Each stage maps
to one roadmap phase (`project/roadmap.md`). A stage is **passed** when its gate artifacts exist,
its decisions are rows in `project/decisions.md`, and `phone/tools/check.py` passes.

```
 P1 Definition ──► P2 Architecture ──► P3 Modules + tools ──┬──► P4 Mechanical ───┐
                        │                                    ├──► P5 Electrical ───┤
                        │                                    ├──► P6 Software ─────┼──► P9 DFM/Reg ──► P12 Build plan
                        │                                    └──► P7 Thermal ──────┤        ▲
                        └──────────── P8 Research (continuous) ────────────────────┘        │
                                                             P10 Cost ◄── P3 ── P11 Platform┘
```

Arrows are information flow. The strict sequence is P1 → P2 → P3; after that, wave execution.

## Why this order

- **Definition before architecture** because the bus and bay design encode the product promise
  (what the owner can replace). Change the promise later and every module spec moves.
- **Architecture before modules** because a module is defined by its bay and its connector, not
  the other way round. `device.yaml` is the parent of every module YAML.
- **Modules with tools, together**, because a spec no script reads drifts. The fit check, power
  budget and BOM roll-up exist so that every later stage edits YAML and re-runs, rather than
  editing prose.
- **Mechanical, electrical, software, thermal in parallel** because they consume the same
  frozen inputs (bays, bus, rails, module list) and produce independent outputs.
- **Research is continuous** and never a gate on its own: it replaces [UNVERIFIED] numbers with
  sourced ones and is consumed wherever it lands.
- **Cost and platform integration hang off P3** because both only need module IDs, masses and
  costs, not geometry.
- **DFM/regulatory last in M0** because they judge the whole; the build plan is the hand-off.

## Stage detail

### P1 — Product definition & plan
| | |
|---|---|
| Question | What is BC-1, who is it for, what may never be traded away, and in what order do we design it? |
| Inputs | `PRODUCT_VISION.md`, `TECHNICAL_DESIGN.md`, Rae's instruction, the termphone sibling (for contrast) |
| Method | Principles with trade-off rules; personas and jobs from the vision (flagged, no interviews yet); requirements with stable IDs and source tags; the decision-point list; risk register; the unit plan |
| Gate rule | Every requirement has a source tag and a phase that will satisfy it. Every decision point names the evidence that closes it. |

### P2 — System architecture
| | |
|---|---|
| Question | What is the envelope, what are the bays, what is the bus, what are the rails? |
| Method | Envelope from the display and battery targets; bay map as named volumes with clearances; BC-Bus connector class, pin groups, power negotiation, identity; rail list; ADRs for compute module and bus |
| Gate rule | `device.yaml` validates; the sum of bay volumes plus structure fits the envelope with margin; every bay names its connector. |

### P3 — Module specifications & deterministic tools
| | |
|---|---|
| Question | What is each module, and does the set fit, power, weigh and cost out? |
| Method | One YAML per module (dims, mass, rails drawn, connector, fasteners, cost estimate with flag, service class); scripts that read the whole tree and fail loudly |
| Gate rule | `report.py` produces fit, mass, power, cost and repairability reports with zero failures; tests pass. |

### P4 — Mechanical design
| | |
|---|---|
| Question | What does the frame look like, and can every module go in and out with one tool? |
| Method | CadQuery frame generated from `device.yaml` bays; module dummies; exploded view; fastener and tolerance plan; assembly order |
| Gate rule | Generated STEP opens; no bay collides; assembly order needs one driver and no adhesive except lamination. |

### P5 — Electrical architecture
| | |
|---|---|
| Question | How does power and data reach every module, and where do the antennas live? |
| Method | Power tree with rail budgets; block diagram; bus pinout with lane allocation per bay; antenna keep-outs and ground strategy across removable modules |
| Gate rule | Every rail in `device.yaml` has a source and a budget; every module's drawn power is within its bay's allocation. |

### P6 — Software architecture
| | |
|---|---|
| Question | What runs, how does it discover modules, how is it updated for ten years? |
| Method | OS stack (mainline-first); module descriptor format and signing; device-tree overlay loading; update model (A/B, per-module firmware); boot chain and owner-unlockable security |
| Gate rule | Descriptor schema validates the sample descriptors; the update model covers OS, module firmware and rollback. |

### P7 — Thermal & battery life
| | |
|---|---|
| Question | Does it stay cool and last a day? |
| Method | Lumped thermal model from SoC TDP and chassis surface; scenario-based battery model in `power_budget.py` |
| Gate rule | Screen-on-time and skin-temperature estimates exist with their assumptions listed and flagged. |

### P8 — Research (continuous)
Every topic file carries `as-of`, sources, and flags. Index in `00-index.md`.

### P9 — DFM, regulatory, repairability
| | |
|---|---|
| Method | DFM review of the frame and modules; regulatory path per target market (radio, safety, ecodesign, battery); repairability rubric run against the spec |
| Gate rule | Every regulatory line cites its instrument or is [UNVERIFIED]; the repairability report has no "unknown" fields. |

### P10 — Cost & unit economics
| | |
|---|---|
| Method | BOM roll-up from module YAMLs; unit economics for first sale, refurbish and resale |
| Gate rule | BOM under the ceiling in `device.yaml` or an explicit decision to raise it. |

### P11 — Platform integration
| | |
|---|---|
| Method | Map module IDs to Inventory SKUs, module YAML to RnD recipes, assembly order to Operations work orders |
| Gate rule | A sample recipe JSON validates against the schema the `src/RnD.Api` will store. |

### P12 — Integrated build plan
| | |
|---|---|
| Method | M1 phases with cost, people, time; the kill criteria; the capital ask in `project/asks.md` |
| Gate rule | Rae can read it and decide whether to raise money. |
