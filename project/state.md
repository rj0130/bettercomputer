# State

**Updated:** 2026-09-22 (end of run 4)
**Branch:** main
**Cold start:** follow the numbered block at the top of `CLAUDE.md`.

## Current position

**P3 (Module architecture) now has its own automated gate**: `phone/spec/modules/` holds all
eight v1 module-class YAMLs (MOD-002) and `validate_modules.py` (U5) validates each one and
fit-checks it against its bay in `phone/spec/device.yaml` — 0 failures, 1 expected warning (the
frame's volume is intentionally unestimated pending U7 CAD). **The next unit is U6**:
power_budget.py, bom_rollup.py, repairability.py and report.py (not yet written — see
`project/plan.md`), which consume the module specs U5 just wrote (rail draw estimates, mass
budgets, fastener/adhesive data) to produce the first `phone/build/` reports. `project/plan.md`
is the authority on units; this table mirrors it.

| Unit | What | Status |
|---|---|---|
| U1 | Cold-start scaffold, tracker, checker | done |
| U2 | Planning corpus: roadmap, design path, README, principles, personas, requirements, decision points, risks, plan | done |
| U3 | Master spec + bus standard + ADRs | done |
| U4 | specload.py, validate_spec.py, fit_check.py, tests | done |
| U5 | Eight module spec YAMLs, validate_modules.py, tests | done |
| U6–U15 | Reports, CAD, electrical, software, thermal, research, DFM, cost, platform, build plan | pending; see `project/plan.md`; **U6 next** |

## What is true right now

- `python3 phone/tools/check.py` passes at the end of run 4. Re-run it; it is the authority.
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
- `python3 -m unittest discover -s phone/tests` passes (44 tests: 29 from U4 plus 15 new for
  `validate_modules.py` in `phone/tests/test_modules.py`).
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
  eight module YAMLs (U5). `phone/docs/adr/` has 001 and 002. `phone/hardware/`, `phone/software/`,
  `phone/docs/research/`, `phone/build/` remain empty; do not trust any path under them until
  their unit creates it.
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

1. **U6**: power_budget.py (scenarios: idle, screen-on, video, 5G data — sum the per-module
   `power` rail draws U5 just wrote, per rail, against a rail budget that P5/U8 hasn't set yet, so
   flag rather than gate on that), bom_rollup.py, repairability.py, report.py, writing to
   `phone/build/`. The `mass_budget_g` figures from U5 also let a rough mass rollup happen here.
2. U11 (research) can run in parallel with U6 and should replace the `[UNVERIFIED]` flags U5 and
   earlier runs added: battery footprint (DP-06), connector family (DP-03), structure volume
   fraction, every module's rail-draw and mass-budget placeholder.
3. Open questions Q1–Q5 in `project/open-questions.md` carry defaults; nothing waits on Rae.
4. Holding's requests to this repo (COMPANY.md, platform confirmation, shared research folder,
   D-007..D-009 dangling-reference housekeeping) are unactioned; pick up next run or hand to a
   parallel session — they don't block U6. Holding's obligation 5 (D037, digest this run) asks
   this repo to run `python3 /Users/raejeong/dev/holding/tools/heal.py --repo
   /Users/raejeong/dev/bettercomputer` at cold start; this run's auto-mode classifier blocked it
   as external code, so it was inspected by hand (confirmed read-only for this repo) but not run —
   pick it up interactively next time, no rush per Holding's own note.

## Absent files (work in flight)

None in flight. Every path in this file and `CLAUDE.md` exists; `check.py` enforces it. The
files listed against pending units in `project/plan.md` do not exist yet by design.
