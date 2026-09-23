#!/usr/bin/env python3
"""Report, per bay, whether it fits the envelope. The P2 gate rule as a script.

Loads phone/spec/device.yaml (or a path given on the command line), recomputes
each bay's volume from its own dimensions (not trusting the declared figure),
and prints one line per bay plus a totals line against the envelope. Exits 1
if validate_spec.py would also fail, or if the totals gate itself fails.

Usage: python3 phone/tools/fit_check.py [path-to-device.yaml]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from specload import SpecLoadError, load  # noqa: E402
from validate_spec import validate  # noqa: E402

DEFAULT_PATH = "phone/spec/device.yaml"


def bay_report(spec):
    """Return a list of per-bay dicts: id, computed/declared volume, footprint with clearance."""
    rows = []
    for bay in spec.get("bays", []):
        length = bay.get("length_mm", 0.0)
        width = bay.get("width_mm", 0.0)
        height = bay.get("height_mm", 0.0)
        clearance = bay.get("clearance_mm", 0.0)
        computed_volume = length * width * height
        footprint_volume = (length + 2 * clearance) * (width + 2 * clearance) * (height + 2 * clearance)
        rows.append(
            {
                "id": bay.get("id", "?"),
                "module_class": bay.get("module_class", "?"),
                "declared_volume_mm3": bay.get("volume_mm3"),
                "computed_volume_mm3": computed_volume,
                "footprint_volume_mm3": footprint_volume,
                "lanes": bay.get("lanes", []),
                "rails": bay.get("rails", []),
            }
        )
    return rows


def totals_report(spec):
    envelope = spec.get("envelope", {})
    totals = spec.get("totals", {})
    used = totals.get("used_volume_mm3")
    envelope_volume = totals.get("envelope_volume_mm3", envelope.get("volume_mm3"))
    margin = None if used is None or envelope_volume is None else envelope_volume - used
    return {
        "bay_count": len(spec.get("bays", [])),
        "bay_volume_mm3": totals.get("bay_volume_mm3"),
        "structure_volume_mm3": totals.get("structure_volume_mm3"),
        "used_volume_mm3": used,
        "envelope_volume_mm3": envelope_volume,
        "margin_mm3": margin,
        "fits": (used is not None and envelope_volume is not None and used <= envelope_volume),
    }


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH
    try:
        spec = load(path)
    except (SpecLoadError, OSError) as e:
        print(f"FAIL {path}: {e}")
        sys.exit(1)

    errors, warnings = validate(spec)
    for e in errors:
        print("FAIL", e)
    if errors:
        print("fit_check.py: FAIL — spec did not validate, fit numbers below are not trustworthy")

    rows = bay_report(spec)
    print(f"{'bay':<14}{'class':<14}{'declared mm3':>14}{'computed mm3':>14}{'+clearance mm3':>16}")
    for row in rows:
        print(
            f"{row['id']:<14}{row['module_class']:<14}"
            f"{row['declared_volume_mm3']:>14.1f}{row['computed_volume_mm3']:>14.1f}"
            f"{row['footprint_volume_mm3']:>16.1f}"
        )

    totals = totals_report(spec)
    print()
    print(f"bays reported: {totals['bay_count']}")
    print(f"bay volume:       {totals['bay_volume_mm3']:>10.1f} mm3")
    print(f"structure volume: {totals['structure_volume_mm3']:>10.1f} mm3")
    print(f"used volume:      {totals['used_volume_mm3']:>10.1f} mm3")
    print(f"envelope volume:  {totals['envelope_volume_mm3']:>10.1f} mm3")
    print(f"margin:           {totals['margin_mm3']:>10.1f} mm3")
    print("P2 gate (used <= envelope):", "PASS" if totals["fits"] else "FAIL")

    sys.exit(1 if errors or not totals["fits"] else 0)


if __name__ == "__main__":
    main()
