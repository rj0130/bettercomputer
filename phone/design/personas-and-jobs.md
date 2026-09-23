# Personas and jobs to be done

**Status: [UNVERIFIED].** Derived from `PRODUCT_VISION.md` and the circular-tech thesis, not from
interviews. P1 gate accepts this with the flag; M1 must replace it with at least ten interviews
per primary persona (see `risk-register.md` R1).

## Personas

| Persona | Why they buy | First job | What they will not accept |
|---|---|---|---|
| **The keeper** (primary) | Wants one phone for eight to ten years; hates the upgrade treadmill | Replace the battery on year two, the screen on year three, the compute module on year five, alone, in ten minutes | A locked bootloader, a glued battery, a part that goes out of stock |
| **The repair shop / refurbisher** (primary; the platform's user) | Turns returned devices into sellable units at yield | Grade a returned BC-1 by reading module identities, swap failing modules, resell | Parts without identity, bespoke cables, calibration locked to the vendor |
| **The institution buyer** (school, NGO, field programme) | Fleet cost per year, not sticker price; wants pooled spares | Keep 200 phones alive with a box of ten modules of each class | Per-device pairing, cloud dependence, short support windows |
| **The privacy / Linux user** | Wants a phone that runs a real OS they can audit | Boot a mainline Linux image with working modem, camera and GPU | Vendor kernel forks, binary-only boot chains without an owner key path |
| **The developer** (secondary) | Wants to build a module for the bus | Read the bus spec, get a descriptor signed, ship a module | An undocumented connector, a closed descriptor format |

## Jobs to be done (numbered so requirements can cite them)

| JTBD | Job | Served by |
|---|---|---|
| J1 | Replace a worn battery in under a minute without a tool | MOD-, MECH-, PWR- requirements |
| J2 | Replace a cracked display in under ten minutes with one driver | MOD-, DISP- |
| J3 | Upgrade compute without changing anything else | MOD-003, ADR-001 |
| J4 | Know exactly what is in a device from software or a scanner, for grading | SEC-, SW- descriptor requirements |
| J5 | Run a mainline OS with all radios, cameras and sensors working | SW- |
| J6 | Keep a fleet alive from a small spares pool | MOD- (bay classes), BIZ- |
| J7 | Design and sell a third-party module | BUS-, SW- descriptor, BIZ- |
| J8 | Buy a phone, later sell it back, and see it resold | BIZ-, platform integration |

## Non-users (deliberately)
Flagship camera buyers; thinness buyers; people who need IP68 for work; gamers wanting the newest
GPU. They are served better elsewhere and saying so keeps the spec honest.
