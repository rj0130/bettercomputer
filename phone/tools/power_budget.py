#!/usr/bin/env python3
"""Report per-rail current draw across four usage scenarios. P3's power report.

Sums each module's power.typical_ma/max_ma (phone/spec/modules/*.yaml) per rail, per scenario,
against the rails phone/spec/device.yaml declares. No rail carries a budget yet — that is P5
(phone/hardware/electrical/power-tree.md, U8) — so this script has nothing to gate on: it prints
totals and flags, and only fails on a spec load/validate error, same policy as fit_check.py.

SCENARIOS below is a first-order modeling sketch, not a sourced requirement: each module is
assigned "off"/"typical"/"max" per scenario to approximate a rough device-level case. Replace it
with a real per-scenario model in P7 (phone/tools/thermal.py, U10) once chipset datasheets (U11)
exist. Every mA figure it sums is itself a [UNVERIFIED] placeholder from phone/spec/modules/
*.yaml (U5) until U11 replaces it — this script does not change that, only totals it.

Usage: python3 phone/tools/power_budget.py [modules-dir] [device.yaml path]
Exit 1 only on a spec load/validate failure.
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

# module_id -> load level per scenario. Modules with only "source" or "passthrough" power
# entries (battery, port's VBUS) don't need an entry here: source/passthrough rows are never
# counted as rail load (see scenario_rail_totals). A module missing from a scenario's dict
# defaults to "off".
SCENARIOS = {
    "idle": {
        "compute": "typical",
        "display": "off",
        "camera-rear": "off",
        "sensor-front": "typical",
        "port": "off",
        "radio": "typical",
    },
    "screen-on": {
        "compute": "typical",
        "display": "typical",
        "camera-rear": "off",
        "sensor-front": "typical",
        "port": "off",
        "radio": "typical",
    },
    "video": {
        "compute": "max",
        "display": "max",
        "camera-rear": "off",
        "sensor-front": "typical",
        "port": "off",
        "radio": "typical",
    },
    "5g-data": {
        "compute": "typical",
        "display": "typical",
        "camera-rear": "off",
        "sensor-front": "typical",
        "port": "off",
        "radio": "max",
    },
}
SCENARIO_ORDER = ["idle", "screen-on", "video", "5g-data"]


def load_modules(modules_dir):
    """Return {module_id: spec} for every *.yaml in modules_dir."""
    modules = {}
    for path in sorted(glob.glob(os.path.join(modules_dir, "*.yaml"))):
        name = os.path.splitext(os.path.basename(path))[0]
        modules[name] = load(path)
    return modules


def scenario_rail_totals(scenario_name, modules):
    """Return {rail_id: {"total_ma": x, "modules": [(module_id, level, ma), ...]}} for one scenario.

    Only power entries with direction == "load" count toward a rail total: "source" (the
    battery feeding VBAT) and "passthrough" (the port's VBUS input) are not device-rail draw.
    """
    levels = SCENARIOS.get(scenario_name, {})
    rails = {}
    for module_id in sorted(modules):
        spec = modules[module_id]
        level = levels.get(module_id, "off")
        for entry in spec.get("power") or []:
            if entry.get("direction") != "load":
                continue
            rail_id = entry.get("rail_id")
            if level == "off":
                ma = 0.0
            elif level == "max":
                ma = entry.get("max_ma", entry.get("typical_ma", 0.0))
            else:
                ma = entry.get("typical_ma", 0.0)
            row = rails.setdefault(rail_id, {"total_ma": 0.0, "modules": []})
            row["total_ma"] += ma
            row["modules"].append((module_id, level, ma))
    return rails


def all_scenarios(modules):
    """Return {scenario_name: scenario_rail_totals(...)} for every scenario in SCENARIO_ORDER."""
    return {name: scenario_rail_totals(name, modules) for name in SCENARIO_ORDER}


def main():
    modules_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODULES_DIR
    device_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DEVICE_PATH

    try:
        device_spec = load(device_path)
    except (SpecLoadError, OSError) as e:
        print(f"FAIL {device_path}: {e}")
        print("power_budget.py: FAIL (1 failures)")
        sys.exit(1)

    device_errors, _ = validate_device(device_spec)
    module_errors, _ = validate_all(modules_dir, device_spec)
    if device_errors or module_errors:
        for e in device_errors + module_errors:
            print("FAIL", e)
        print("power_budget.py: FAIL (spec did not validate, power numbers below are not trustworthy)")
        sys.exit(1)

    modules = load_modules(modules_dir)
    results = all_scenarios(modules)

    for name in SCENARIO_ORDER:
        print(f"\nscenario: {name}")
        rails = results[name]
        for rail_id in sorted(rails):
            row = rails[rail_id]
            detail = ", ".join(f"{m}={lvl}:{ma:.0f}mA" for m, lvl, ma in row["modules"] if ma)
            line = f"  {rail_id:<6} {row['total_ma']:>8.0f} mA"
            print(f"{line}   ({detail})" if detail else line)

    print()
    print("No rail carries a budget in phone/spec/device.yaml yet (P5); nothing above is a")
    print("pass/fail gate. Scenario module-activity levels are a modeling sketch (see this")
    print("file's SCENARIOS), not a sourced requirement, and every mA figure traces back to a")
    print("[UNVERIFIED] placeholder in phone/spec/modules/*.yaml (U5) until U11 replaces it.")
    print("power_budget.py: OK (0 failures, informational only)")
    sys.exit(0)


if __name__ == "__main__":
    main()
