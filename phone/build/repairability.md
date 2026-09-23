# Repairability report

Source: `phone/tools/repairability.py`.

Disassembly-only sub-score out of 10, not the full EU-index score REQ REG-003 asks for — documentation, spare-parts availability and spare-parts price are not spec data yet. See `repairability.py`'s docstring for the rubric.

| module | tool | fasteners | adhesive | order dep. | total/10 |
|---|---:|---:|---:|---:|---:|
| battery | 3.0 | 3.0 | 2.0 | 2.0 | 10.00 |
| camera-rear | 3.0 | 2.0 | 2.0 | 2.0 | 9.00 |
| compute | 3.0 | 1.0 | 2.0 | 2.0 | 8.00 |
| display | 3.0 | 1.0 | 2.0 | 2.0 | 8.00 |
| frame | 0.0 | 0.0 | 2.0 | 0.0 | 2.00 |
| port | 3.0 | 2.0 | 2.0 | 2.0 | 9.00 |
| radio | 3.0 | 2.0 | 2.0 | 0.0 | 7.00 |
| sensor-front | 3.0 | 2.0 | 2.0 | 2.0 | 9.00 |

- `frame`: tool: unexpected tool 'full teardown' (D-004 mandates Torx T5 or none)
- `frame`: fasteners: fastener count unknown (pending CAD, U7)
- `frame`: order_dependency: removal-order dependency declared: 'removed last: every bay module and the back cover must be vacated first (device.yaml structure.description); this is the one exception MOD-005 already carves out for the back cover, extended here to the frame itself'
- `radio`: order_dependency: removal-order dependency declared: "the RF coax pigtail to the frame's antenna windows must be detached first (RADIO-002); not yet counted against MOD-005's no-removal-order-dependency claim, flagged here for P4/P5 (U8) to resolve"

Device disassembly sub-score (mean of 7 bay-mapped modules, frame excluded): **8.57/10**.
