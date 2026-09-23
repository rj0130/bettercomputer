# CLAUDE.md

Orientation for any Claude session working in this repo, cold or warm. **Read this file, then
`project/state.md`, then run `python3 phone/tools/check.py`.** That is the whole cold-start.

## What this is

BetterComputer is a circular-tech engine: collect, grade, refactor and resell modular, repairable
personal computing devices. The repo now has two halves:

| Half | Path | What |
|---|---|---|
| **The product** | `phone/` | The **BC-1**, a modular, repairable, long-lived phone designed here as files: machine-readable spec, code-CAD, electrical architecture, BOM, software stack, research. This is where the work is. |
| **The platform** | `src/` | The .NET 10 service scaffold (Orders, Inventory, Staff, Operations, RnD, Management, Workers) that sells, refurbishes and tracks the product. Skeleton only; see `TECHNICAL_DESIGN.md`. |

Owner: Rae (he/him). Exploratory: no technical capital is committed. The aim is a phone designed
thoroughly enough on paper and in code that a real team could pick it up.

A sibling repo, `../termphone`, designs a *different* phone (text-first, e-ink, CLI). BC-1 is the
general-purpose modular handset; the two share the platform pattern and nothing else. Do not merge
them.

## The one principle

> Every part of the phone can be replaced by its owner, with one tool, without breaking anything else.

If a design choice makes the phone thinner, cheaper or faster but takes a part out of the owner's
hands, it is the wrong choice. Modularity is the product; everything else is a spec line.

## How we work

- **File-based state.** `project/state.md` is the truth about where the work is. Chat does not
  count. A session that ends without updating it has not finished.
- **Every decision is a row** in `project/decisions.md` with an ID (D-NNN), status and reason.
  Reversible choices proceed as PROPOSED; expensive or irreversible ones become a brief in
  `project/briefs/` and a row in `project/open-questions.md` with a default and a decide-by date.
- **Async by default.** Never idle waiting on Rae. Past the decide-by date the default executes.
- **Determinism where possible.** Fit checks, power budgets, BOM roll-ups, repairability scores and
  CAD are scripts in `phone/tools/`, driven by the YAML in `phone/spec/`. A model proposes; a script
  decides.
- **Evidence hygiene.** Every number in `phone/docs/research/` carries a source and an `as-of`
  date. Unconfirmed is **[UNVERIFIED]**; disputed is **[CONTESTED]**. Never invent a part number,
  a datasheet figure, a regulation clause or a price. If you cannot verify it, flag it.
- **Never reference a file that does not exist.** `check.py` fails on dangling links in
  `state.md` and `CLAUDE.md`.
- **Run the checker** at the start and end of every run: `python3 phone/tools/check.py`.
  Tests: `python3 -m unittest discover -s phone/tests`. A new process rule belongs in the checker
  or nowhere.
- **Git.** Commit at the end of each unit of work with a message that says what changed and why.
  Do not push; the remote is Rae's call (see `project/asks.md`).

## Where things are

| Path | What |
|---|---|
| `project/state.md` | Current position, what is done, what is next. **Update at end of run.** |
| `project/decisions.md` | Decision log, one row per decision in force |
| `project/open-questions.md` | Queue for Rae: default, decide-by, reversibility |
| `project/asks.md` | Things only a human can do (money, access, accounts) |
| `project/glossary.md` | Every term, one line |
| `project/log/` | Append-only run logs |
| `phone/README.md` | The product: what BC-1 is, how the spec tree is organised |
| `phone/spec/device.yaml` | **The master spec.** Envelope, bays, bus, rails. Everything derives from it. |
| `phone/spec/modules/*.yaml` | One file per module: dims, mass, power, connector, cost, fasteners |
| `phone/spec/bus.md` | The BC-Bus: the one connector every module uses |
| `phone/design/` | Requirements (`REQ-` ids), principles, industrial design, ergonomics |
| `phone/hardware/` | `cad/` CadQuery generators, `electrical/` power tree and block diagrams, `bom/` |
| `phone/software/` | OS stack, module descriptor format, update model, firmware notes |
| `phone/tools/` | `check.py`, `validate_spec.py`, `fit_check.py`, `power_budget.py`, `bom_rollup.py`, `repairability.py`, `gen_cad.py`, `report.py` |
| `phone/docs/research/` | Sourced research with `as-of` dates; `phone/docs/adr/` for architecture decisions |
| `phone/build/` | Generated outputs (reports, SVG, STEP/STL). Regenerate with `phone/tools/report.py`. |

**Python.** `phone/tools/*.py` run on system `python3` with the standard library only, except
`gen_cad.py`, which needs the CadQuery venv: `.venv/bin/python phone/tools/gen_cad.py`
(created with `/opt/homebrew/opt/python@3.11/bin/python3.11 -m venv .venv && .venv/bin/pip install cadquery build123d pyyaml`).
The spec is YAML but the stdlib tools parse it with the tiny loader in `phone/tools/specload.py`,
so nothing but CAD needs the venv.
