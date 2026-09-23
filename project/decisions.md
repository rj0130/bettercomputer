# Decisions

One row per decision in force. Status: PROPOSED (Claude, reversible, Rae may veto) ·
AGREED (Rae confirmed) · SUPERSEDED (points at replacement). Reasons are one line; longer
reasoning lives in `project/briefs/` or `phone/docs/adr/`.

| ID | Date | Decision | Status | Reason / where |
|---|---|---|---|---|
| D-001 | 2026-09-22 | The repo's product is a phone, working name **BC-1**; the .NET services in `src/` are the platform that sells and refurbishes it | PROPOSED | Rae's instruction 2026-09-22; fits the circular-tech vision in `PRODUCT_VISION.md` |
| D-002 | 2026-09-22 | File-based state (`project/state.md`) with a checker gate, mirroring the pattern from `standard-literature-review` and `termphone` | PROPOSED | Cold-start survival across context resets |
| D-003 | 2026-09-22 | Every module attaches through one connector standard, the **BC-Bus** (`phone/spec/bus.md`), never a bespoke flex | PROPOSED | The one principle; a bespoke flex is a part the owner cannot source |
| D-004 | 2026-09-22 | One fastener type for the whole phone: **Torx T5**, captive where possible; zero adhesive except display cover-glass lamination | PROPOSED | Repairability rubric; one driver in the box |
| D-005 | 2026-09-22 | Mechanical CAD as code (CadQuery, `.venv/`), STEP/STL exports; no proprietary CAD | PROPOSED | Reviewable diffs, agent-scriptable, no licence wall; matches termphone D-CAD-01 |
| D-006 | 2026-09-22 | Electrical architecture expressed as YAML power tree + text block diagrams; KiCad deferred until a board is actually laid out | PROPOSED | A 1 GB GUI install buys nothing at architecture stage |
| D-007 | 2026-09-22 | Core compute is a **removable compute module** (SoC + RAM + storage on one carrier) so the phone's silicon can be upgraded without replacing the chassis, display or battery | PROPOSED | Longevity is the product; see `phone/docs/adr/001-compute-module.md` |
| D-008 | 2026-09-22 | SoC candidate for BC-1 v1: a Qualcomm QCM6490-class part, chosen for its upstream Linux support and its long industrial availability window; alternatives tracked in research | PROPOSED | `phone/docs/research/01-soc-candidates.md`; numbers there are flagged |
| D-009 | 2026-09-22 | Software: mainline-Linux-first (Debian/postmarketOS-class userland) with AOSP as a second supported image on the same kernel; no vendor kernel forks | PROPOSED | An OS the community can keep alive outlives any vendor; `phone/software/os-stack.md` |
| D-010 | 2026-09-22 | Battery is a user-swappable pouch pack in a hard shell with a slide latch, standardised footprint in `phone/spec/modules/battery.yaml`, no tools needed | PROPOSED | EU 2023/1670 ecodesign line and the principle |
| D-011 | 2026-09-22 | Display is a screw-mounted MIPI-DSI module with the cover glass laminated to the panel; the display module is replaced as one part | PROPOSED | Lamination is the one adhesive we keep; replacing panel+glass as a unit is what repair shops actually do |
| D-012 | 2026-09-22 | Every module carries an I2C identity EEPROM with a signed descriptor; the OS refuses nothing but warns on unsigned or unknown modules | PROPOSED | Owner freedom over vendor lock; provenance for the refurbish pipeline |
| D-013 | 2026-09-22 | Nothing is pushed to `origin` by Claude; commits are local until Rae pushes | PROPOSED | Reaching a third party is Rae's call |
| D-014 | 2026-09-22 | Envelope thickness raised from PRD-004's ≤10mm target to 11.8mm actual | PROPOSED | Bay clearances plus the BC-Bus connector stack do not fit 10mm; `phone/spec/device.yaml` envelope block; mass ceiling (215g) and footprint (152.4×73.2mm) unchanged |
| D-015 | 2026-09-22 | DP-02 closed: the eight v1 module classes (MOD-002) fit the envelope with 37.2% margin | PROPOSED | `phone/spec/device.yaml` totals block; margin reserved for BC-Bus backbone, antenna keep-outs (P5) and thermal solution (P7), expected to shrink once U7 CAD runs |
