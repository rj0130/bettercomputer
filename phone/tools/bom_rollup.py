#!/usr/bin/env python3
"""Roll up mass and cost across every module spec. P3's mass/BOM report.

Mass: sums footprint.mass_budget_g from phone/spec/modules/*.yaml against device.yaml's
ceilings.mass_g. Every mass figure in the spec today is an [UNVERIFIED] placeholder from U5; this
script sums what exists and states the gap rather than treating the total as measured. The frame
module's mass is null (its footprint is deliberately unestimated pending U7 CAD, see
phone/spec/modules/frame.yaml), so the modules total here is a lower bound on device mass, not a
full accounting: it excludes the frame itself, the back cover and fasteners that share
device.yaml's structure.volume_budget_mm3. If the modules-only total already exceeds the ceiling
that is a definite violation and this script fails loudly, same policy as fit_check.py; staying
under it is reported as provisional, not PASS, because the missing frame mass could still push
the real total over.

Cost: design-path.md's P3 method names "cost estimate with flag" as part of a module YAML, but no
phone/spec/modules/*.yaml file declares a `cost` block — U5 did not add one, and evidence hygiene
(CLAUDE.md) forbids inventing a price with no source to flag. This script looks for an optional
`cost.usd` field on each module and, since none exist yet, reports the BOM as not yet computable
against ceilings.bom_usd and says so explicitly. Real figures are P10/U13
(phone/hardware/bom/bom.csv).

Usage: python3 phone/tools/bom_rollup.py [modules-dir] [device.yaml path]
Exit 1 on a spec load/validate failure, or if the modules-only mass total exceeds the ceiling.
"""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from specload import SpecLoadError, load  # noqa: E402
from validate_modules import validate_all  # noqa: E402
from validate_spec import validate as validate_device  # noqa: E402

DEFAULT_MODULES_DIR = "phone/spec/modules"
DEFAULT_DEVICE_PATH = "phone/spec/device.yaml"


def load_modules(modules_dir):
    """Return {module_id: spec} for every *.yaml in modules_dir."""
    modules = {}
    for path in sorted(glob.glob(os.path.join(modules_dir, "*.yaml"))):
        name = os.path.splitext(os.path.basename(path))[0]
        modules[name] = load(path)
    return modules


def mass_rollup(modules, device_spec):
    """Return {"rows": [...], "total_g": x, "missing": [...], "ceiling_g": x}."""
    rows = []
    missing = []
    total = 0.0
    for module_id in sorted(modules):
        footprint = modules[module_id].get("footprint", {})
        mass = footprint.get("mass_budget_g")
        rows.append({"module_id": module_id, "mass_budget_g": mass})
        if mass is None:
            missing.append(module_id)
        else:
            total += mass
    ceiling = device_spec.get("ceilings", {}).get("mass_g")
    return {"rows": rows, "total_g": total, "missing": missing, "ceiling_g": ceiling}


def cost_rollup(modules, device_spec):
    """Return {"rows": [...], "total_usd": None|x, "missing": [...], "ceiling_usd": x}.

    total_usd is None whenever any module lacks cost data, since a partial sum would misstate
    the BOM as smaller than it is.
    """
    rows = []
    missing = []
    total = 0.0
    for module_id in sorted(modules):
        cost = (modules[module_id].get("cost") or {}).get("usd")
        rows.append({"module_id": module_id, "cost_usd": cost})
        if cost is None:
            missing.append(module_id)
        else:
            total += cost
    ceiling = device_spec.get("ceilings", {}).get("bom_usd")
    total_usd = None if missing else total
    return {"rows": rows, "total_usd": total_usd, "missing": missing, "ceiling_usd": ceiling}


def main():
    modules_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODULES_DIR
    device_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DEVICE_PATH

    try:
        device_spec = load(device_path)
    except (SpecLoadError, OSError) as e:
        print(f"FAIL {device_path}: {e}")
        print("bom_rollup.py: FAIL (1 failures)")
        sys.exit(1)

    device_errors, _ = validate_device(device_spec)
    module_errors, _ = validate_all(modules_dir, device_spec)
    if device_errors or module_errors:
        for e in device_errors + module_errors:
            print("FAIL", e)
        print("bom_rollup.py: FAIL (spec did not validate, rollup numbers below are not trustworthy)")
        sys.exit(1)

    modules = load_modules(modules_dir)
    mass = mass_rollup(modules, device_spec)
    cost = cost_rollup(modules, device_spec)

    print("mass rollup (modules only — excludes frame, back cover, fasteners: see this file's docstring)")
    for row in mass["rows"]:
        g = row["mass_budget_g"]
        print(f"  {row['module_id']:<14} {g if g is not None else 'UNVERIFIED':>10}")
    print(f"  {'total':<14} {mass['total_g']:>10.1f} g   (ceiling {mass['ceiling_g']} g)")
    if mass["missing"]:
        print(f"  missing mass data: {', '.join(mass['missing'])} (excluded from total, not zero)")

    mass_fail = mass["ceiling_g"] is not None and mass["total_g"] > mass["ceiling_g"]
    if mass_fail:
        print(f"  FAIL: modules-only total ({mass['total_g']:.1f}g) already exceeds the {mass['ceiling_g']}g ceiling")
    elif mass["missing"]:
        headroom = mass["ceiling_g"] - mass["total_g"] if mass["ceiling_g"] is not None else None
        print(f"  provisional: {headroom:.1f} g headroom left for {', '.join(mass['missing'])} + structure; not a confirmed PASS")
    else:
        print("  PASS (all module mass data present and under ceiling)")

    print()
    print(f"BOM (cost) rollup: {len(modules) - len(cost['missing'])}/{len(modules)} modules carry cost data")
    if cost["total_usd"] is None:
        print(f"  BOM not computable: {', '.join(cost['missing'])} have no `cost.usd` field.")
        print(f"  ceilings.bom_usd ({cost['ceiling_usd']}) cannot be checked until P10/U13 supplies real figures.")
    else:
        print(f"  total: ${cost['total_usd']:.2f}  (ceiling ${cost['ceiling_usd']})")
        print("  PASS" if cost["total_usd"] <= cost["ceiling_usd"] else "  FAIL: BOM exceeds ceiling")

    print()
    print("bom_rollup.py:", "FAIL" if mass_fail else "OK", f"({1 if mass_fail else 0} failures)")
    sys.exit(1 if mass_fail else 0)


if __name__ == "__main__":
    main()
