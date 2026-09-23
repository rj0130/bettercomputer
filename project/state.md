# State

**Updated:** 2026-09-22 (end of run 3)
**Branch:** main
**Cold start:** follow the numbered block at the top of `CLAUDE.md`.

## Current position

Phase **P2 (System architecture) now has an automated gate**: `validate_spec.py` (U4) parses
`phone/spec/device.yaml` and re-derives every bay volume and the totals arithmetic instead of
trusting the hand calc from run 2 — it currently passes with 0 failures. **The next unit is U5**:
the eight per-module spec YAMLs under `phone/spec/modules/`, which is what actually gates P3 (P3
needs module specs plus tools; U4 only supplied the tools). `project/plan.md` is the authority on
units; this table mirrors it.

| Unit | What | Status |
|---|---|---|
| U1 | Cold-start scaffold, tracker, checker | done |
| U2 | Planning corpus: roadmap, design path, README, principles, personas, requirements, decision points, risks, plan | done |
| U3 | Master spec + bus standard + ADRs | done |
| U4 | specload.py, validate_spec.py, fit_check.py, tests | done |
| U5–U15 | Modules, CAD, electrical, software, thermal, research, DFM, cost, platform, build plan | pending; see `project/plan.md`; **U5 next** |

## What is true right now

- `python3 phone/tools/check.py` passes at the end of run 3. Re-run it; it is the authority.
- `phone/tools/specload.py` (stdlib YAML-subset loader), `validate_spec.py` (schema + totals-
  arithmetic gate) and `fit_check.py` (per-bay report, recomputes volume from dims rather than
  trusting the declared figure) all exist and pass against `phone/spec/device.yaml`.
  `python3 -m unittest discover -s phone/tests` passes (29 tests).
- `validate_spec.py`'s first run against `phone/spec/device.yaml` found two real bugs from U3's hand-written
  spec, not parser bugs: `port` bay's `lanes` referenced `USB3` where `phone/spec/bus.md` defines the lane
  group id as `USB3/PCIe`; `compute` bay's `lanes` list wrongly included `I2C:1`/`GPIO:1`, which
  `phone/spec/bus.md` defines as always-present pin groups, not per-bay high-speed-lane entries. Both fixed
  in `phone/spec/device.yaml`, logged as D-016. The P2 gate numbers (66,934.0mm³ bay + 15,796.4mm³ structure
  = 82,730.4mm³ used against 131,637.0mm³ envelope, 37.2% margin) are unchanged by this fix.
- The CadQuery venv `.venv/` (Python 3.11, cadquery 2.8, build123d 0.13, pyyaml) is installed on
  this host, not in git. Nothing uses it yet; U7 will. Holding (D042) now lists it as shared
  tooling other portfolio repos may reuse.
- `phone/spec/device.yaml` and `phone/spec/bus.md` exist (U3); `phone/spec/modules/` is still an
  **empty directory** until U5. `phone/docs/adr/` has 001 and 002. `phone/hardware/`,
  `phone/software/`, `phone/docs/research/`, `phone/build/` remain empty; do not trust any path
  under them until their unit creates it.
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

1. **U5**: `phone/spec/modules/{compute,display,battery,camera-rear,sensor-front,port,radio,frame}.yaml`,
   one per v1 module class. `validate_spec.py` and `fit_check.py` exist now (U4) but only look at
   `phone/spec/device.yaml`'s bays; whether they need extending to also load and cross-check the module
   files, or whether module specs get their own thin validator, is a U5 call.
2. U11 (research) can run in parallel with U5–U6 and should replace the `[UNVERIFIED]` flags this
   run added: battery bay footprint (DP-06), connector family (DP-03), structure volume fraction.
3. Open questions Q1–Q5 in `project/open-questions.md` carry defaults; nothing waits on Rae.
4. Holding's requests to this repo (COMPANY.md, platform confirmation, shared research folder,
   D-007..D-009 dangling-reference housekeeping) are unactioned; pick up next run or hand to a
   parallel session — they don't block U5.

## Absent files (work in flight)

None in flight. Every path in this file and `CLAUDE.md` exists; `check.py` enforces it. The
files listed against pending units in `project/plan.md` do not exist yet by design.
