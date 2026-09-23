# State

**Updated:** 2026-09-22 (end of run 1, before a model switch and `/clear`)
**Branch:** main
**Cold start:** follow the numbered block at the top of `CLAUDE.md`.

## Current position

Phase **P1 (Product definition & plan) is complete on paper**; nothing after it has started.
Units U1 and U2 are done. **The next unit is U3**: the master spec (device.yaml) and the
BC-Bus standard (bus.md) under phone/spec/, plus two ADRs; exact filenames are in the plan. `project/plan.md` is the authority on
units; this table mirrors it.

| Unit | What | Status |
|---|---|---|
| U1 | Cold-start scaffold, tracker, checker | done |
| U2 | Planning corpus: roadmap, design path, README, principles, personas, requirements, decision points, risks, plan | done |
| U3 | Master spec + bus standard + ADRs | **next** |
| U4–U15 | Tools, modules, CAD, electrical, software, thermal, research, DFM, cost, platform, build plan | pending; see `project/plan.md` |

## What is true right now

- `python3 phone/tools/check.py` passes at the end of run 1. Re-run it; it is the authority.
- The CadQuery venv `.venv/` (Python 3.11, cadquery 2.8, build123d 0.13, pyyaml) is installed on
  this host, not in git. Nothing uses it yet; U7 will.
- `phone/spec/`, `phone/hardware/`, `phone/software/`, `phone/docs/research/`, `phone/build/` are
  **empty directories**: the plan names the files that will live there; none exist yet. Do not
  trust any path under them until U3+ creates it.
- The team mailbox is at `/Users/raejeong/agentmail` (server on 127.0.0.1:7777, started with
  nohup, not launchd: the launchd install was denied; Rae can install `/Users/raejeong/agentmail/com.rae.agentmail.plist`).
  Peers registered: second-brain, termphone, consolegenie. Their intro messages are acked in
  `data/mailboxes/bettercomputer/acked/` and worth one read: consolegenie offers a sanitizer;
  second-brain answered which tools exist on this Mac; termphone is the sibling phone.
- The .NET scaffold in `src/` is untouched except build artifacts leaving the index.
- Remote `origin` is `github.com/rj0130/bettercomputer`; nothing pushed by Claude (Q4).

## Next

1. U3. Envelope from PRD-004, bays from MOD-002, lane allocation per BUS-002, rails, ceilings
   from PRD-003. Keep it small enough for the stdlib loader U4 will write (flat maps, lists, no
   anchors).
2. U11 (research) can run in parallel with U3–U6 and should replace the [UNVERIFIED] flags in
   `phone/design/requirements.md` and `decision-points.md`.
3. Open questions Q1–Q5 in `project/open-questions.md` carry defaults; nothing waits on Rae.

## Absent files (work in flight)

None in flight. Every path in this file and `CLAUDE.md` exists; `check.py` enforces it. The
files listed against pending units in `project/plan.md` do not exist yet by design.
