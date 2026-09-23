# State

**Updated:** 2026-09-22 (run 1)
**Branch:** main
**Next session starts here:** read `CLAUDE.md`, then this file, then run `python3 phone/tools/check.py`.

## Current position

Run 1 turned the repo from a .NET service scaffold into a product-design repo. The product is
**BC-1**, a modular repairable phone. Work proceeds in numbered units; each unit ends with a commit
and a row below.

| Unit | What | Status |
|---|---|---|
| U1 | Cold-start scaffold: `CLAUDE.md`, `project/`, checker | done |
| U2 | Master spec `phone/spec/device.yaml` + module YAMLs + bus spec | done |
| U3 | Deterministic tools: validate, fit check, power budget, BOM roll-up, repairability, report | done |
| U4 | Code-CAD: chassis frame with module bays, STEP/STL, exploded SVG | done |
| U5 | Design docs: requirements, principles, industrial design, ergonomics | done |
| U6 | Electrical architecture: power tree, block diagram, module identity | done |
| U7 | Software stack: OS choice, module descriptors, update model | done |
| U8 | Research with sources: SoC candidates, battery, regulation, display | done |
| U9 | Platform hook: how BC-1 BOM and recipes feed `src/` services | done |

## What is true right now

- `phone/tools/check.py` passes (run it to confirm; it is the authority, not this line).
- The CadQuery venv at `.venv/` exists on this host only. It is not in git. Rebuild per `CLAUDE.md`.
- The .NET scaffold in `src/` is untouched from the August commit except for `.gitignore`
  dropping `obj/` and `bin/`.
- Remote `origin` is `github.com/rj0130/bettercomputer`; nothing has been pushed by Claude.

## Next

1. Rae reviews `project/open-questions.md` (defaults execute past decide-by dates).
2. Next run: U10 thermal model (SoC TDP vs chassis surface), U11 antenna keep-outs in the CAD,
   U12 module EEPROM descriptor schema as JSON Schema + signing design.

## Absent files (work in flight)

None. Every path referenced in this file and in `CLAUDE.md` exists; `check.py` enforces it.
