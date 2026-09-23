# Mass / BOM report

Source: `phone/tools/bom_rollup.py`.

## Mass (modules only — excludes frame, back cover, fasteners)

| module | mass_budget_g |
|---|---:|
| battery | 55 |
| camera-rear | 6 |
| compute | 12 |
| display | 28 |
| frame | UNVERIFIED |
| port | 4 |
| radio | 8 |
| sensor-front | 1 |
| **total** | **114.0** (ceiling 215) |

Missing mass data: frame (excluded from total, not zero).

Provisional: 101.0g headroom left for frame + structure. Not a confirmed PASS.

## Cost (BOM)

Not computable: battery, camera-rear, compute, display, frame, port, radio, sensor-front carry no `cost.usd` field yet.
`ceilings.bom_usd` (260) cannot be checked until P10/U13 supplies real figures.
