#!/usr/bin/env python3
"""Validate phone/spec/device.yaml against the schema its own header describes.

This is the automated P2 gate that project/plan.md's U4 row promises: it turns
U3's hand-verified arithmetic (bay volumes + structure <= envelope) into a
re-runnable check, plus structural checks (required fields, unique bay ids,
lane/rail references resolve, totals arithmetic matches the per-bay data).

Usage: python3 phone/tools/validate_spec.py [path-to-device.yaml]
Exit 1 on any error.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from specload import SpecLoadError, load  # noqa: E402

DEFAULT_PATH = "phone/spec/device.yaml"

TOP_LEVEL_KEYS = [
    "schema_version",
    "device",
    "envelope",
    "structure",
    "bays",
    "totals",
    "bus",
    "rails",
    "ceilings",
]
ENVELOPE_KEYS = ["length_mm", "width_mm", "thickness_mm", "volume_mm3", "mass_ceiling_g"]
BAY_KEYS = [
    "id",
    "module_class",
    "length_mm",
    "width_mm",
    "height_mm",
    "volume_mm3",
    "clearance_mm",
    "zone",
    "connector",
    "lanes",
    "rails",
    "source",
]
RAIL_KEYS = ["id", "description", "consumers", "source"]
LANE_GROUP_KEYS = ["id", "protocol", "consumers"]

REL_TOL = 1e-3


def close(a, b, rel_tol=REL_TOL, abs_tol=1e-6):
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


def validate(spec):
    """Return (errors, warnings), each a list of strings."""
    errors = []
    warnings = []

    def err(msg):
        errors.append(msg)

    for key in TOP_LEVEL_KEYS:
        if key not in spec:
            err(f"missing top-level key: {key}")
    if errors:
        return errors, warnings  # nothing below is safe to inspect

    if spec["schema_version"] != 1:
        err(f"schema_version: expected 1, got {spec['schema_version']!r}")

    envelope = spec["envelope"]
    for key in ENVELOPE_KEYS:
        if key not in envelope:
            err(f"envelope: missing key {key}")
    if all(k in envelope for k in ("length_mm", "width_mm", "thickness_mm", "volume_mm3")):
        computed = envelope["length_mm"] * envelope["width_mm"] * envelope["thickness_mm"]
        if not close(computed, envelope["volume_mm3"]):
            err(
                f"envelope.volume_mm3: declared {envelope['volume_mm3']} does not match "
                f"length*width*thickness = {computed}"
            )

    structure = spec["structure"]
    for key in ["volume_budget_mm3", "volume_budget_fraction_of_envelope"]:
        if key not in structure:
            err(f"structure: missing key {key}")
    if "volume_budget_mm3" in structure and "volume_mm3" in envelope:
        computed_fraction = structure["volume_budget_mm3"] / envelope["volume_mm3"]
        if not close(computed_fraction, structure["volume_budget_fraction_of_envelope"], abs_tol=5e-4):
            err(
                "structure.volume_budget_fraction_of_envelope: declared "
                f"{structure['volume_budget_fraction_of_envelope']} does not match "
                f"volume_budget_mm3/envelope.volume_mm3 = {computed_fraction:.6f}"
            )

    bays = spec["bays"]
    if not isinstance(bays, list) or not bays:
        err("bays: expected a non-empty list")
        bays = []

    rail_ids = set()
    if isinstance(spec.get("rails"), list):
        for rail in spec["rails"]:
            for key in RAIL_KEYS:
                if key not in rail:
                    err(f"rails: entry missing key {key}: {rail}")
            if "id" in rail:
                rail_ids.add(rail["id"])
    else:
        err("rails: expected a list")

    lane_group_ids = set()
    bus = spec.get("bus", {})
    lane_groups = bus.get("lane_groups") if isinstance(bus, dict) else None
    if isinstance(lane_groups, list):
        for lg in lane_groups:
            for key in LANE_GROUP_KEYS:
                if key not in lg:
                    err(f"bus.lane_groups: entry missing key {key}: {lg}")
            if "id" in lg:
                lane_group_ids.add(lg["id"])
    else:
        err("bus.lane_groups: expected a list")

    seen_ids = set()
    bay_volume_sum = 0.0
    for bay in bays:
        for key in BAY_KEYS:
            if key not in bay:
                err(f"bay {bay.get('id', '?')}: missing key {key}")
        bay_id = bay.get("id")
        if bay_id is not None:
            if bay_id in seen_ids:
                err(f"bay id {bay_id!r} is not unique")
            seen_ids.add(bay_id)

        if all(k in bay for k in ("length_mm", "width_mm", "height_mm", "volume_mm3")):
            computed = bay["length_mm"] * bay["width_mm"] * bay["height_mm"]
            if not close(computed, bay["volume_mm3"]):
                err(
                    f"bay {bay_id}: volume_mm3 declared {bay['volume_mm3']} does not match "
                    f"length*width*height = {computed}"
                )
            bay_volume_sum += bay.get("volume_mm3", 0.0)

        for lane in bay.get("lanes", []):
            group_id = lane.rsplit(":", 1)[0] if ":" in lane else lane
            if group_id not in lane_group_ids:
                err(f"bay {bay_id}: lane {lane!r} references unknown lane group {group_id!r}")

        for rail_id in bay.get("rails", []):
            if rail_id not in rail_ids:
                err(f"bay {bay_id}: rail {rail_id!r} references unknown rail")

    totals = spec.get("totals", {})
    if not isinstance(totals, dict):
        err("totals: expected a mapping")
        totals = {}
    else:
        required_totals = [
            "bay_volume_mm3",
            "structure_volume_mm3",
            "used_volume_mm3",
            "envelope_volume_mm3",
            "margin_mm3",
            "margin_fraction",
        ]
        for key in required_totals:
            if key not in totals:
                err(f"totals: missing key {key}")

    if bays and "bay_volume_mm3" in totals:
        if not close(bay_volume_sum, totals["bay_volume_mm3"]):
            err(
                f"totals.bay_volume_mm3: declared {totals['bay_volume_mm3']} does not match "
                f"sum of bay volume_mm3 = {bay_volume_sum}"
            )

    if "volume_budget_mm3" in structure and "structure_volume_mm3" in totals:
        if not close(structure["volume_budget_mm3"], totals["structure_volume_mm3"]):
            err(
                f"totals.structure_volume_mm3: declared {totals['structure_volume_mm3']} does "
                f"not match structure.volume_budget_mm3 = {structure['volume_budget_mm3']}"
            )

    if all(k in totals for k in ("bay_volume_mm3", "structure_volume_mm3", "used_volume_mm3")):
        computed_used = totals["bay_volume_mm3"] + totals["structure_volume_mm3"]
        if not close(computed_used, totals["used_volume_mm3"]):
            err(
                f"totals.used_volume_mm3: declared {totals['used_volume_mm3']} does not match "
                f"bay_volume_mm3 + structure_volume_mm3 = {computed_used}"
            )

    if "volume_mm3" in envelope and "envelope_volume_mm3" in totals:
        if not close(envelope["volume_mm3"], totals["envelope_volume_mm3"]):
            err(
                f"totals.envelope_volume_mm3: declared {totals['envelope_volume_mm3']} does not "
                f"match envelope.volume_mm3 = {envelope['volume_mm3']}"
            )

    if all(k in totals for k in ("used_volume_mm3", "envelope_volume_mm3", "margin_mm3")):
        computed_margin = totals["envelope_volume_mm3"] - totals["used_volume_mm3"]
        if not close(computed_margin, totals["margin_mm3"]):
            err(
                f"totals.margin_mm3: declared {totals['margin_mm3']} does not match "
                f"envelope_volume_mm3 - used_volume_mm3 = {computed_margin}"
            )
        # The P2 gate itself: bay volumes plus structure must fit the envelope.
        if totals["used_volume_mm3"] > totals["envelope_volume_mm3"]:
            err(
                f"P2 gate failed: used_volume_mm3 ({totals['used_volume_mm3']}) exceeds "
                f"envelope_volume_mm3 ({totals['envelope_volume_mm3']})"
            )

    if all(k in totals for k in ("margin_mm3", "envelope_volume_mm3", "margin_fraction")):
        computed_fraction = totals["margin_mm3"] / totals["envelope_volume_mm3"]
        if not close(computed_fraction, totals["margin_fraction"], abs_tol=5e-4):
            err(
                f"totals.margin_fraction: declared {totals['margin_fraction']} does not match "
                f"margin_mm3/envelope_volume_mm3 = {computed_fraction:.6f}"
            )

    ceilings = spec.get("ceilings", {})
    if isinstance(ceilings, dict):
        if "mass_g" in ceilings and "mass_ceiling_g" in envelope and ceilings["mass_g"] != envelope["mass_ceiling_g"]:
            err(
                f"ceilings.mass_g ({ceilings['mass_g']}) does not match "
                f"envelope.mass_ceiling_g ({envelope['mass_ceiling_g']})"
            )
        if (
            "thickness_mm" in ceilings
            and "thickness_mm" in envelope
            and ceilings["thickness_mm"] != envelope["thickness_mm"]
        ):
            err(
                f"ceilings.thickness_mm ({ceilings['thickness_mm']}) does not match "
                f"envelope.thickness_mm ({envelope['thickness_mm']})"
            )
    else:
        err("ceilings: expected a mapping")

    return errors, warnings


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH
    try:
        spec = load(path)
    except (SpecLoadError, OSError) as e:
        print(f"FAIL {path}: {e}")
        print("validate_spec.py: FAIL (1 failures, 0 warnings)")
        sys.exit(1)

    errors, warnings = validate(spec)
    for w in warnings:
        print("WARN", w)
    for e in errors:
        print("FAIL", e)
    print(
        "validate_spec.py:",
        "FAIL" if errors else "OK",
        f"({len(errors)} failures, {len(warnings)} warnings)",
    )
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
