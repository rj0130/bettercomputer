# Risk register

| R | Risk | Likelihood | Impact | Mitigation | Owner phase |
|---|---|---|---|---|---|
| R1 | Personas are unvalidated; the keeper persona may not exist at volume | high | high | Interviews in M1; do not size the pilot before | P12 |
| R2 | Bus connector cannot carry MIPI DSI + CSI + USB3 at the cycle rating we need | medium | high | Two candidate families in P8; lane allocation per bay, not per connector | P2/P8 |
| R3 | SoC vendor drops mainline support or availability | medium | high | Compute module is swappable by design; second SoC candidate tracked | P8 |
| R4 | Modular thickness/mass makes it unsellable | medium | medium | Envelope targets are explicit; the fit check reports the number, Rae decides | P2/P4 |
| R5 | Antenna performance suffers from removable metal modules | medium | high | Keep-outs in CAD; radio front-end near the frame antennas; M1.5 measurement | P5 |
| R6 | Repairability claims fail the EU index on a detail (e.g. software pairing) | low | medium | Rubric script runs on every change | P3/P9 |
| R7 | BOM exceeds ceiling once real quotes arrive | high | medium | Every cost is flagged [UNVERIFIED] until quoted; ceiling is a decision row | P10 |
| R8 | Design drifts between prose docs and YAML | medium | medium | Principle 4: scripts read the spec; checker fails on dangling references | all |
| R9 | The .NET platform and the product diverge in data model | medium | low | P11 maps module IDs to SKUs early | P11 |
| R10 | Context resets lose work | high | high | File-based state, per-unit commits, checker at start and end | all |
