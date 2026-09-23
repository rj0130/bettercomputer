#!/usr/bin/env python3
"""Module dummies: where each of the seven bay-mapped modules sits in 3D, and their raw boxes.

Stdlib only — no cadquery import at module load time — so phone/tests/test_cad.py can exercise
the layout and collision logic under plain system python3, same as every other phone/tools/
script. cadquery is only imported lazily inside build_solid(), which frame.py/gen_cad.py call
from the venv.

Coordinate frame (mm), matching phone/spec/device.yaml's envelope:
  x: 0..length_mm,   0 = top edge (radio, camera, sensor end)
  y: 0..width_mm,    0..width_mm across the short axis
  z: 0..thickness_mm, 0 = front face (display side), thickness_mm = rear face (back cover side)

LAYOUT is a hand-authored floorplan, not sourced from any requirement or datasheet — the same
kind of flagged modeling sketch power_budget.py's SCENARIOS table already is (D-018). No prior
unit ever placed bays in 3D; U7 is the first time real positions are needed at all, so this file
invents them, verified by hand (and by phone/tests/test_cad.py) to be collision-free among the
seven bay modules' own raw volumes. `rotate_xy: True` means the bay's length_mm runs along y and
width_mm runs along x (used only by radio, whose zone is "top edge, spanning width").
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from specload import load  # noqa: E402

DEVICE_YAML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "spec", "device.yaml")

LAYOUT = {
    "display": {"x0": 1.9, "y0": 1.5, "z0": 0.0, "rotate_xy": False},
    "sensor-front": {"x0": 2.0, "y0": 60.0, "z0": 0.0, "rotate_xy": False},
    "radio": {"x0": 0.3, "y0": 14.1, "z0": 2.6, "rotate_xy": True},
    "compute": {"x0": 16.0, "y0": 25.0, "z0": 2.6, "rotate_xy": False},
    "camera-rear": {"x0": 16.0, "y0": 1.5, "z0": 5.3, "rotate_xy": False},
    "battery": {"x0": 59.0, "y0": 2.6, "z0": 2.6, "rotate_xy": False},
    "port": {"x0": 128.0, "y0": 31.6, "z0": 2.9, "rotate_xy": False},
}

# The one intentional overlap: sensor-front is a notch cut into the display module (a front
# camera poking through the display's own footprint, taller than the display panel is thick).
# Not a collision — display.py/frame.py treat it as a documented cutout, not a defect.
EXPECTED_OVERLAPS = [frozenset({"display", "sensor-front"})]


def bay_dims(bay):
    """(dx, dy, dz) for one device.yaml bay entry, honoring LAYOUT's rotate_xy flag."""
    rotate = LAYOUT[bay["id"]]["rotate_xy"]
    length, width, height = bay["length_mm"], bay["width_mm"], bay["height_mm"]
    return (width, length, height) if rotate else (length, width, height)


def bay_bbox(bay, clearance=0.0):
    """(x0,x1,y0,y1,z0,z1) for one bay, optionally expanded by `clearance` on every face."""
    pos = LAYOUT[bay["id"]]
    dx, dy, dz = bay_dims(bay)
    x0, y0, z0 = pos["x0"] - clearance, pos["y0"] - clearance, pos["z0"] - clearance
    return (x0, x0 + dx + 2 * clearance, y0, y0 + dy + 2 * clearance, z0, z0 + dz + 2 * clearance)


def all_bboxes(spec, clearance_field=None):
    """{bay_id: bbox} for every bay in spec['bays']. clearance_field='clearance_mm' expands
    each bay's box by its own declared clearance; None (default) uses raw module dims."""
    out = {}
    for bay in spec.get("bays", []):
        clearance = bay.get(clearance_field, 0.0) if clearance_field else 0.0
        out[bay["id"]] = bay_bbox(bay, clearance)
    return out


def boxes_overlap(a, b):
    ax0, ax1, ay0, ay1, az0, az1 = a
    bx0, bx1, by0, by1, bz0, bz1 = b
    return ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1 and az0 < bz1 and bz0 < az1


def check_collisions(bboxes, exceptions=None):
    """Return a list of (id_a, id_b) pairs whose boxes overlap, skipping declared exceptions."""
    exceptions = exceptions or []
    ids = sorted(bboxes)
    collisions = []
    for i, a in enumerate(ids):
        for b in ids[i + 1 :]:
            if frozenset({a, b}) in exceptions:
                continue
            if boxes_overlap(bboxes[a], bboxes[b]):
                collisions.append((a, b))
    return collisions


def build_solid(bay):
    """Return a cadquery solid for one bay's raw module box, positioned per LAYOUT. Lazy
    cadquery import: only frame.py/gen_cad.py (run under .venv/) ever call this."""
    import cadquery as cq

    pos = LAYOUT[bay["id"]]
    dx, dy, dz = bay_dims(bay)
    box = cq.Workplane("XY").box(dx, dy, dz, centered=(False, False, False))
    return box.translate((pos["x0"], pos["y0"], pos["z0"]))


def main():
    spec = load(DEVICE_YAML)
    bboxes = all_bboxes(spec)
    collisions = check_collisions(bboxes, EXPECTED_OVERLAPS)
    for bay_id in sorted(bboxes):
        x0, x1, y0, y1, z0, z1 = bboxes[bay_id]
        print(f"{bay_id:<14} x[{x0:6.1f},{x1:6.1f}] y[{y0:6.1f},{y1:6.1f}] z[{z0:5.1f},{z1:5.1f}]")
    if collisions:
        print("COLLISIONS:", collisions)
    else:
        print("no bay-to-bay collisions (raw module volumes)")


if __name__ == "__main__":
    main()
