#!/usr/bin/env python3
"""CadQuery frame generator: MECH-001's structural shell, built from phone/spec/device.yaml.

Needs the .venv/ CadQuery environment (CLAUDE.md's one stdlib exception). Run as:
  .venv/bin/python3.11 phone/hardware/cad/frame.py

Model (a first CAD pass, not DFM-final — every constant below is a flagged, hand-chosen
placeholder, same status as power_budget.py's SCENARIOS table, D-018):
  - a perimeter RING: the envelope box minus an inner box shrunk by WALL_MM on x/y, full
    thickness — the four side walls every bay's edge connector reaches through.
  - a BACKBONE board: a WALL_MM-to-WALL_MM slab at BACKBONE_Z, the depth right behind the
    display, with a cutout wherever a bay's *raw* (no-clearance) z-range actually reaches that
    depth — display and camera-rear don't reach it (display ends before it, camera-rear starts
    after it) so the board is NOT cut for them.
  - a BACK COVER: a slab across the rear COVER_MM thick, cut only where camera-rear's raw
    z-range reaches the rear face (MOD-005's own back-cover-comes-off exemption, MECH-002).
  - every bay pocket (module raw dims + its own clearance_mm, expanded on all 6 faces) is then
    also cut from the union of the three pieces above, as a defensive final pass — this is what
    "no bay collision" against the frame itself means, on top of modules.py's module-to-module
    check.

Ribs between bays are NOT modeled (no data drives their placement yet); flagged in
phone/hardware/fasteners-and-tolerances.md, not hidden. DENSITY_G_PER_CM3 is a hand-chosen
ABS/PC-blend placeholder (frame + cover are plastic; BACKBONE_MM's PCB is really ~1.85 g/cm3
FR4, blended here into one density for a first-pass mass, both flagged) pending P9/U12 material
selection.

Usage: python3 frame.py [device.yaml path]   (only for the report; STEP/STL export needs
cadquery, use gen_cad.py which drives frame.py + modules.py + exploded.py together.)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from specload import load  # noqa: E402

import modules  # noqa: E402

DEVICE_YAML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "spec", "device.yaml")

WALL_MM = 1.0
BACKBONE_MM = 0.6
COVER_MM = 0.8
DENSITY_G_PER_CM3 = 1.2  # [UNVERIFIED] ABS/PC-blend placeholder; see module docstring


def _pocket_box(cq, bay):
    dx, dy, dz = modules.bay_dims(bay)
    pos = modules.LAYOUT[bay["id"]]
    c = bay.get("clearance_mm", 0.0)
    box = cq.Workplane("XY").box(dx + 2 * c, dy + 2 * c, dz + 2 * c, centered=(False, False, False))
    return box.translate((pos["x0"] - c, pos["y0"] - c, pos["z0"] - c))


def _raw_z_range(bay):
    pos = modules.LAYOUT[bay["id"]]
    _, _, dz = modules.bay_dims(bay)
    return pos["z0"], pos["z0"] + dz


def build_frame_shape(spec):
    """Return (cadquery Shape, volume_mm3) for the frame's structural material."""
    import cadquery as cq

    envelope = spec["envelope"]
    length, width, thickness = envelope["length_mm"], envelope["width_mm"], envelope["thickness_mm"]
    bays = spec["bays"]

    outer = cq.Workplane("XY").box(length, width, thickness, centered=(False, False, False))
    inner = cq.Workplane("XY").box(
        length - 2 * WALL_MM, width - 2 * WALL_MM, thickness, centered=(False, False, False)
    ).translate((WALL_MM, WALL_MM, 0))
    ring = outer.cut(inner)

    backbone_z0 = 2.6  # right behind the display (envelope-thickness-independent, display's own height_mm)
    backbone = cq.Workplane("XY").box(
        length, width, BACKBONE_MM, centered=(False, False, False)
    ).translate((0, 0, backbone_z0))
    for bay in bays:
        z0, z1 = _raw_z_range(bay)
        if z0 < backbone_z0 + BACKBONE_MM and z1 > backbone_z0:
            backbone = backbone.cut(_pocket_box(cq, bay))

    cover_z0 = thickness - COVER_MM
    cover = cq.Workplane("XY").box(
        length, width, COVER_MM, centered=(False, False, False)
    ).translate((0, 0, cover_z0))
    for bay in bays:
        z0, z1 = _raw_z_range(bay)
        if z0 < thickness and z1 > cover_z0:
            cover = cover.cut(_pocket_box(cq, bay))

    structure = ring.union(backbone).union(cover)
    for bay in bays:
        structure = structure.cut(_pocket_box(cq, bay))

    solid = structure.val()
    return solid, solid.Volume()


def frame_volume_and_mass(spec):
    _, volume_mm3 = build_frame_shape(spec)
    mass_g = (volume_mm3 / 1000.0) * DENSITY_G_PER_CM3  # mm3 -> cm3 -> g
    return volume_mm3, mass_g


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEVICE_YAML
    spec = load(path)
    volume_mm3, mass_g = frame_volume_and_mass(spec)
    budget = spec["structure"]["volume_budget_mm3"]
    print(f"frame structure volume: {volume_mm3:.1f} mm3 (budget in device.yaml: {budget} mm3)")
    print(f"frame mass @ {DENSITY_G_PER_CM3} g/cm3 (flagged placeholder density): {mass_g:.2f} g")
    print("PASS" if volume_mm3 <= budget else "OVER BUDGET — see decisions.md for the follow-up")


if __name__ == "__main__":
    main()
