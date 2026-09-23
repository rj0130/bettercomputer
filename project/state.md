# State

**Updated:** 2026-09-23 (end of run 5)
**Branch:** main
**Cold start:** follow the numbered block at the top of `CLAUDE.md`.

## Current position

**P3 (Module architecture) is now fully gated end to end.** `phone/spec/modules/` holds all eight
v1 module-class YAMLs (MOD-002); `validate_modules.py` (U5) validates and fit-checks each one; and
`power_budget.py`, `bom_rollup.py`, `repairability.py`, `report.py` (U6) consume that same data to
produce the first `phone/build/*.md` reports — `phone/build/fit.md`, `phone/build/power-budget.md`,
`phone/build/bom.md`, `phone/build/repairability.md`, and an index `phone/build/report.md` that
states the P3 gate condition
(design-path.md: "report.py produces fit, mass, power, cost and repairability reports with zero
failures; tests pass"). That gate passes: 0 script failures, 76/76 tests. **The next unit is
U7** (CAD) — see `project/plan.md`.

| Unit | What | Status |
|---|---|---|
| U1 | Cold-start scaffold, tracker, checker | done |
| U2 | Planning corpus: roadmap, design path, README, principles, personas, requirements, decision points, risks, plan | done |
| U3 | Master spec + bus standard + ADRs | done |
| U4 | specload.py, validate_spec.py, fit_check.py, tests | done |
| U5 | Eight module spec YAMLs, validate_modules.py, tests | done |
| U6 | power_budget.py, bom_rollup.py, repairability.py, report.py, phone/build/*.md, tests | done |
| U7–U15 | CAD, electrical, software, thermal, research, DFM, cost, platform, build plan | pending; see `project/plan.md`; **U7 next** |

## What is true right now

- `python3 phone/tools/check.py` passes at the end of run 5. Re-run it; it is the authority.
- **U6 is done.** `phone/tools/power_budget.py`, `bom_rollup.py`, `repairability.py`, `report.py`
  exist; `report.py` writes `phone/build/{fit,power-budget,bom,repairability,report}.md` from the
  real spec tree. All four scripts revalidate `phone/spec/device.yaml` + every module spec before computing
  anything (same pattern as `validate_modules.py`'s `main()`) and fail loudly on a load/validate
  error, never on a design-space finding they aren't positioned to gate:
  - `power_budget.py` sums per-rail mA across four scenarios (idle, screen-on, video, 5g-data)
    using a hand-authored module-activity table (`SCENARIOS`, one "off"/"typical"/"max" per
    module per scenario) — **not sourced from any requirement**, flagged in the script and in
    D-018; no rail carries a budget yet (P5/U8), so this never fails the gate, only reports.
  - `bom_rollup.py` sums `mass_budget_g` (114.0g across 7 modules, frame's mass still `null`
    pending U7 CAD, 101.0g provisional headroom against the 215g ceiling — not a confirmed PASS)
    and looks for a `cost.usd` field on each module. None exists (D-019): no module YAML carries
    cost data, so the BOM is reported as **not computable** against the $260 ceiling rather than
    invented — real figures are P10/U13. The script does fail loudly if the *mass-only* total
    alone already exceeds the ceiling (mirrors `fit_check.py`'s envelope gate); it doesn't here.
  - `repairability.py` computes a **disassembly-only** sub-score out of 10 per module (tool,
    fastener count scaled 0–6, adhesive, removal-order dependency) — not the full EU/French
    repairability index REQ REG-003 wants, since documentation and spare-parts data don't exist
    yet (D-020). Device average across the 7 bay-mapped modules (frame excluded, MOD-005's own
    carve-out): 8.57/10. It correctly re-surfaces `phone/spec/modules/radio.yaml`'s known
    RF-pigtail order-dependency nuance as a flag, and `phone/spec/modules/frame.yaml`'s tool
    ("full teardown") and fastener count (`null`) as flags rather than silently scoring them.
  - `report.py` renders all of the above to markdown and states the P3 gate
    (design-path.md: "report.py produces fit, mass, power, cost and repairability reports with
    zero failures; tests pass") explicitly in `phone/build/report.md`. Current run: gate PASS.
  - `phone/tests/test_reports.py` adds 32 new tests (function-level unit tests plus two
    file-writing integration tests for `bom_rollup.main()`'s mass-ceiling-exceeded path and
    `report.main()`'s five-file output). Full suite: 76 tests, all pass.
- `phone/spec/modules/{compute,display,battery,camera-rear,sensor-front,port,radio,frame}.yaml`
  (U5) exist. Each of the seven bay-mapped modules declares a footprint, lane list and power-rail
  list that `phone/tools/validate_modules.py` checks against the matching bay in
  `phone/spec/device.yaml` —
  exact dimension and lane match, and every power rail must be one of that bay's declared rails.
  The `frame` module (MOD-002's eighth v1 class) is not a bay; it shares `structure.
  volume_budget_mm3` with the back cover and the BC-Bus backbone board, so its own footprint is
  deliberately left `null` (a warning, not a failure) pending real geometry from U7 CAD, and the
  validator only checks it does not alone exceed the structure budget. D-017 records the choice
  to give module specs their own validator rather than extending `validate_spec.py`.
- Every module file also adds three things `phone/spec/device.yaml`'s bay entry has no room for:
  an identity descriptor block (MOD-007 fields), removal data (tool, time target, order
  dependency — MOD-004/MOD-005), and repairability data (fastener count, adhesive — MOD-005/
  MOD-006). All rail-draw and mass-budget figures are `[UNVERIFIED]` placeholders, order-of-
  magnitude only, flagged per-field; none of them feed a real decision yet.
  `phone/spec/modules/radio.yaml` and `phone/spec/modules/port.yaml` each flag one MOD-005
  nuance the requirement doesn't fully cover (the radio's RF coax pigtail disconnect step; the
  port's USB-C shell being frame-mounted, not bay-board-mounted) — not resolved here, left for
  P4/P5 (U8).
- `python3 -m unittest discover -s phone/tests` passes (76 tests: 29 from U4, 15 from U5's
  `phone/tests/test_modules.py`, 32 new from U6's `phone/tests/test_reports.py`).
- `phone/tools/specload.py` (stdlib YAML-subset loader), `validate_spec.py` (schema + totals-
  arithmetic gate) and `fit_check.py` (per-bay report, recomputes volume from dims rather than
  trusting the declared figure) all exist and pass against `phone/spec/device.yaml`.
- `validate_spec.py`'s first run against `phone/spec/device.yaml` found two real bugs from U3's hand-written
  spec, not parser bugs: `port` bay's `lanes` referenced `USB3` where `phone/spec/bus.md` defines the lane
  group id as `USB3/PCIe`; `compute` bay's `lanes` list wrongly included `I2C:1`/`GPIO:1`, which
  `phone/spec/bus.md` defines as always-present pin groups, not per-bay high-speed-lane entries. Both fixed
  in `phone/spec/device.yaml`, logged as D-016. The P2 gate numbers (66,934.0mm³ bay + 15,796.4mm³ structure
  = 82,730.4mm³ used against 131,637.0mm³ envelope, 37.2% margin) are unchanged by this fix.
- The CadQuery venv `.venv/` (Python 3.11, cadquery 2.8, build123d 0.13, pyyaml) is installed on
  this host, not in git. Nothing uses it yet; U7 will. Holding (D042) now lists it as shared
  tooling other portfolio repos may reuse.
- `phone/spec/device.yaml` and `phone/spec/bus.md` exist (U3); `phone/spec/modules/` now holds the
  eight module YAMLs (U5). `phone/docs/adr/` has 001 and 002. `phone/build/` now holds five
  generated `.md` reports (U6) — regenerate with `python3 phone/tools/report.py` after any spec
  change, never hand-edit them. `phone/hardware/`, `phone/software/`, `phone/docs/research/`
  remain empty; do not trust any path under them until their unit creates it.
- `phone/spec/device.yaml`'s bay+structure volume is 82,730.4mm³ against a 131,637.0mm³ envelope: 37.2%
  margin, deliberately unallocated for the BC-Bus backbone board, antenna keep-outs (P5) and
  thermal solution (P7). Battery bay footprint and the connector family are both `[UNVERIFIED]`
  pending DP-06 and DP-03. Envelope thickness raised from PRD-004's ≤10mm target to 11.8mm
  actual (D-014) — flagged for Rae to veto.
- The team mailbox is at `/Users/raejeong/agentmail` (server on 127.0.0.1:7777, started with
  nohup, not launchd: the launchd install was denied; Rae can install `/Users/raejeong/agentmail/com.rae.agentmail.plist`).
  Peers registered: second-brain, termphone, consolegenie, standard-literature-review, holding.
  A **Holding** layer now sits above all four side-venture repos (charter at
  `/Users/raejeong/dev/holding/charter.md`); it has asked bettercomputer for a `COMPANY.md`, to
  confirm platform ownership (agentmail, services/commerce pattern, hardware supply chain, CAD
  tooling), and to open a shared hardware/supply-chain research folder termphone can read — all
  PROPOSED, chairman veto by 2026-09-29. Not yet actioned this run; see mailbox inbox.
- The .NET scaffold in `src/` is untouched except build artifacts leaving the index.
- Remote `origin` is `github.com/rj0130/bettercomputer`; nothing pushed by Claude (Q4). Holding
  now also mirrors this repo locally at `/Users/raejeong/backups/git/bettercomputer.git` each
  CEO check-in (D038); push to origin is still Holding ask A001.

## Next

1. **U7** (P4, mechanical): the CadQuery frame generator, module dummies, exploded-view SVG and
   driver script named in `project/plan.md`'s U7 row (not yet written — see that file), producing
   STEP/STL/SVG exports plus a fasteners-and-tolerances doc. Needs the `.venv/` CadQuery
   environment (already installed on this host, see below). This is what finally derives the
   frame's own real volume and mass — every place that currently reads
   `phone/spec/modules/frame.yaml`'s `null` footprint/mass and `repairability.py`'s
   "fasteners unknown" flag should be revisited once U7 lands real geometry.
2. U8 (P5, electrical) can start in parallel once U7 or independently of it — it's what actually
   sets rail budgets, which is the missing piece `phone/tools/power_budget.py` (U6) explicitly
   flagged rather than gated on. It also owns resolving `phone/spec/modules/radio.yaml`'s
   RF-pigtail removal-order nuance that `phone/tools/repairability.py` now surfaces as a real
   flag.
3. U11 (research) can still run in parallel and should replace every `[UNVERIFIED]` flag: battery
   footprint (DP-06), connector family (DP-03), structure volume fraction, every module's
   rail-draw and mass-budget placeholder. It should also be the source that lets a real `cost`
   block get added to each module YAML, so `bom_rollup.py`'s BOM report stops saying "not
   computable" (currently 0/8 modules have cost data; see D-019).
4. Open questions Q1–Q5 in `project/open-questions.md` carry defaults; nothing waits on Rae.
5. Holding's requests to this repo (COMPANY.md, platform confirmation, shared research folder,
   D-007..D-009 dangling-reference housekeeping) remain unactioned; pick up next run or hand to a
   parallel session — they don't block U7. This run's mailbox also carries three new Holding
   notes not yet acted on: A002 (KiCad install authorized, install only when a unit needs a board
   layout — not yet, so not installed), A001 (push to `origin` authorized in principle, but
   Holding will only actually push after Rae says the single word "push" in the live board
   thread — no push happened this run, none should until that word arrives), and an alignment
   note that no day-job (McMaster-Carr SEO) artifact work happens on this Mac (not relevant to
   this repo's own work, no action needed here). Holding's obligation 5 (D037) — running
   `python3 /Users/raejeong/dev/holding/tools/heal.py --repo /Users/raejeong/dev/bettercomputer`
   at cold start — is still outstanding, same as last run; pick it up interactively.

## Absent files (work in flight)

None in flight. Every path in this file and `CLAUDE.md` exists; `check.py` enforces it. The
files listed against pending units in `project/plan.md` do not exist yet by design.
