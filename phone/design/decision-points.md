# Decision points

The open design decisions, in the order they must close, each with the evidence that closes it
and a working default so no phase idles. Closed ones become rows in `project/decisions.md`.

| DP | Decision | Working default | Closes when | Phase |
|---|---|---|---|---|
| DP-01 | Price band and BOM ceiling | USD 260 BOM / 549 retail (Q2) | Rae answers Q2 or 2026-10-15 passes | P1 |
| DP-02 | Module class list v1 | The eight classes in MOD-002 | **Closed 2026-09-22** — D-015, `phone/spec/device.yaml` totals block (37.2% margin) | P2 |
| DP-03 | BC-Bus connector family and pin groups | 0.35 mm-pitch board-to-board, two-vendor catalogue part; exact family chosen in P8 | Two vendors' datasheets confirm cycle rating and lane count [UNVERIFIED until then] | P2/P8 |
| DP-04 | SoC for the v1 compute module | Qualcomm QCM6490-class (D-008) | P8 research confirms upstream driver state and availability window | P8 |
| DP-05 | Display technology | OLED 6.1" 1080p 90 Hz | Cost from P10 vs ceiling; supplier availability | P3/P10 |
| DP-06 | Battery format | Hard-shell pouch, ~60 × 80 × 6 mm, ≥ 4,000 mAh | Fit check passes and a cell vendor lists the footprint | P3/P8 |
| DP-07 | Radio front-end on its own module vs on compute | Own module (region SKUs) | Antenna study in P5 says the split does not cost > 2 dB | P5 |
| DP-08 | OS default image | AOSP for consumers, Linux one command away (Q3) | Rae answers Q3 or date passes | P6 |
| DP-09 | Ingress rating | IP54 | Gasket study in P4 shows whether IP55+ is free | P4/P9 |
| DP-10 | Frame material | Aluminium unibody with polymer antenna windows | DFM review in P9 | P4/P9 |
| DP-11 | Fastener | Torx T5 captive (D-004) | Stays unless DFM finds a reason | P4 |
| DP-12 | Descriptor signing scheme | Ed25519, vendor key + owner key slot | P6 security design | P6 |
| DP-13 | Target markets for v1 certification | EU + US | Regulatory cost in P9 | P9 |
| DP-14 | Pilot run size | 2,000 units | Unit economics in P10 | P12 |
