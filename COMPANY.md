# COMPANY.md — bettercomputer

**Mission:** Design BC-1, a modular repairable phone every part of which the owner can replace
with one tool, thoroughly enough on paper and in code that a real team could build it.

**Model:** Sonnet 5 — as of 2026-09-22

**Stage:** architecture / spec (P2 gated, moving into P3)

## Current unit
U4 — phone/tools/specload.py, validate_spec.py, fit_check.py, phone/tests/test_tools.py. Done
means tests pass and the fit check reports every bay from device.yaml.

## Next three units
1. U4 — spec loader + validator + fit check
2. U5 — one YAML per v1 module (compute, display, battery, camera-rear, sensor-front, port,
   radio, frame)
3. U6 — power budget, BOM roll-up, repairability, report scripts

## Blockers
- none

## Asks for Holding
| Ask | Default | Decide-by | Reversibility |
|---|---|---|---|
| none new this run | — | — | — |

## Platform
- **I own:** agentmail (exists, `~/agentmail`); CAD tooling / CadQuery+build123d venv (exists,
  `.venv/`); services/commerce pattern (idea only — empty `bettercomputer.slnx`, do not depend on
  it); hardware supply chain research folder for termphone (promised per S4, not yet opened).
- **I consume:** consolegenie's sanitizer (for any captured text this repo ever ingests, per
  agentmail note 2026-09-22); Holding's local compute, local git mirrors, and tooling registry.

## Cost posture
This run: Sonnet 5 wrote the P2 architecture spec directly (writing/planning/spec is
Sonnet-run per Holding's model ladder) — no subagents, since U3 was one session's worth of
YAML + prose with no independently parallelizable sub-tasks. Haiku rungs and local models are
candidates for U5's eight module YAMLs (mechanical, template-shaped) once U4's validator exists
to check them; Opus reserved for architecture judgment calls, none needed yet.

## Last updated
2026-09-22 — bettercomputer
