# BC-1 — the BetterComputer phone

A general-purpose smartphone whose every part the owner can replace with one tool. Designed here
as files: a machine-readable spec, code-generated CAD, an electrical and software architecture,
sourced research and a plan. Nothing here has been fabricated; see `project/roadmap.md` for what
is paper (M0) and what needs capital (M1+).

## What makes it different

| Ordinary phone | BC-1 |
|---|---|
| Glued sandwich; battery and screen are the last things you can reach | Frame with named **bays**; battery and display are the first things you reach, no tools for the battery, one Torx T5 for everything else |
| Bespoke flex cable per part, per model, per year | One connector standard, the **BC-Bus**, for every module; a module from BC-1 fits BC-2 if its bay class matches |
| SoC soldered to a mainboard that carries everything | Removable **compute module** (SoC + RAM + storage); upgrade the brain, keep the body |
| Support ends when the vendor kernel fork stops | Mainline Linux first; AOSP as a second image on the same kernel |
| Parts identified by nothing; refurbishers guess | Every module carries a signed identity descriptor the OS and the refurbish line both read |
| Thinness wins every trade-off | Replaceability wins every trade-off; thickness is a spec line, not a virtue |

## How the spec tree is organised (once P2/P3 exist)

```
phone/spec/device.yaml        envelope, bays, bus, rails, ceilings      (parent of everything)
phone/spec/modules/*.yaml     one per module: dims, mass, power, cost, fasteners, service class
phone/spec/bus.md             the BC-Bus connector standard
phone/design/                 requirements (REQ-ids), principles, personas, decision points, risks
phone/hardware/               cad/ electrical/ bom/ dfm
phone/software/               os stack, module descriptors, update model, boot/security
phone/tools/                  the scripts that read the spec and say yes or no
phone/docs/                   research (sourced, dated) and ADRs
phone/build/                  generated reports and geometry
```

Start with `project/state.md` for where the work is, `phone/design/requirements.md` for what the
phone must do, and `phone/design/decision-points.md` for what is still open and what closes it.
