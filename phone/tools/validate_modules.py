#!/usr/bin/env python3
"""Validate phone/spec/modules/*.yaml and fit-check them against phone/spec/device.yaml.

This is U5's answer to the open call state.md and project/plan.md left from U4: module specs
get their own thin validator rather than an extension of validate_spec.py's device-shaped
schema. "Fit" for a module means the same thing fit_check.py means for a bay: recompute the
module's own volume from its declared dimensions rather than trusting the figure, and confirm
it actually matches the bay it claims to occupy — for the seven bay-mapped modules that is an
exact match against phone/spec/device.yaml's bay of the same id; for the frame (MOD-002's eighth
module class, not a bay) it is an upper bound against structure.volume_budget_mm3, since the
frame shares that budget with the back cover and the BC-Bus backbone board.

Usage: python3 phone/tools/validate_modules.py [modules-dir] [device.yaml path]
Exit 1 on any error.
"""
import glob
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from specload import SpecLoadError, load  # noqa: E402
from validate_spec import validate as validate_device  # noqa: E402

DEFAULT_MODULES_DIR = "phone/spec/modules"
DEFAULT_DEVICE_PATH = "phone/spec/device.yaml"

EXPECTED_MODULE_IDS = [
    "compute",
    "display",
    "battery",
    "camera-rear",
    "sensor-front",
    "port",
    "radio",
    "frame",
]

TOP_LEVEL_KEYS = ["schema_version", "module", "footprint", "lanes", "power", "removal", "repairability", "descriptor"]
MODULE_KEYS = ["id", "bay_id", "name", "description", "status", "source"]
FOOTPRINT_KEYS = ["length_mm", "width_mm", "height_mm", "volume_mm3", "mass_budget_g"]
REMOVAL_KEYS = ["tool", "time_target_s", "order_dependency", "source"]
REPAIRABILITY_KEYS = ["fasteners", "adhesive", "source"]
DESCRIPTOR_KEYS = ["medium", "fields", "source"]
POWER_LOAD_KEYS = ["rail_id", "direction", "typical_ma", "max_ma"]
POWER_SOURCE_KEYS = ["rail_id", "direction", "capacity_mah"]
POWER_PASSTHROUGH_KEYS = ["rail_id", "direction", "max_ma"]

REL_TOL = 1e-3


def close(a, b, rel_tol=REL_TOL, abs_tol=1e-6):
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


def validate_module(name, spec, device_spec):
    """Return (errors, warnings) for one module spec against the loaded device spec."""
    errors = []
    warnings = []

    def err(msg):
        errors.append(f"{name}: {msg}")

    def warn(msg):
        warnings.append(f"{name}: {msg}")

    for key in TOP_LEVEL_KEYS:
        if key not in spec:
            err(f"missing top-level key: {key}")
    if errors:
        return errors, warnings

    module = spec["module"]
    for key in MODULE_KEYS:
        if key not in module:
            err(f"module: missing key {key}")
    module_id = module.get("id")
    if module_id != name:
        err(f"module.id {module_id!r} does not match filename {name!r}.yaml")

    bay_id = module.get("bay_id")
    device_bays = {b["id"]: b for b in device_spec.get("bays", []) if "id" in b}
    bay = device_bays.get(bay_id) if bay_id is not None else None
    if bay_id is not None and bay is None:
        err(f"module.bay_id {bay_id!r} does not exist in device.yaml bays")

    footprint = spec["footprint"]
    for key in FOOTPRINT_KEYS:
        if key not in footprint:
            err(f"footprint: missing key {key}")
    dims_present = all(footprint.get(k) is not None for k in ("length_mm", "width_mm", "height_mm", "volume_mm3"))
    if dims_present:
        computed = footprint["length_mm"] * footprint["width_mm"] * footprint["height_mm"]
        if not close(computed, footprint["volume_mm3"]):
            err(f"footprint.volume_mm3 declared {footprint['volume_mm3']} does not match length*width*height = {computed}")
    elif footprint.get("volume_mm3") is None:
        warn("footprint has no computed volume yet (pending CAD)")

    if bay is not None:
        if dims_present:
            for dim in ("length_mm", "width_mm", "height_mm"):
                if not close(footprint[dim], bay.get(dim, float("nan"))):
                    err(f"footprint.{dim} ({footprint[dim]}) does not match bay {bay_id!r} {dim} ({bay.get(dim)})")
        if spec.get("lanes") != bay.get("lanes"):
            err(f"lanes {spec.get('lanes')!r} does not match bay {bay_id!r} lanes {bay.get('lanes')!r}")
        power_rail_ids = {p.get("rail_id") for p in spec.get("power", []) if p.get("direction") != "passthrough"}
        bay_rail_ids = set(bay.get("rails", []))
        for rail_id in power_rail_ids - bay_rail_ids:
            err(f"power rail {rail_id!r} is not declared for bay {bay_id!r} (bay.rails = {bay.get('rails')!r})")
    elif footprint.get("volume_mm3") is not None:
        structure = device_spec.get("structure", {})
        budget = structure.get("volume_budget_mm3")
        if budget is not None and footprint["volume_mm3"] > budget:
            err(
                f"footprint.volume_mm3 ({footprint['volume_mm3']}) exceeds structure.volume_budget_mm3 "
                f"({budget}) even though this module shares that budget with other parts"
            )

    rail_ids = {r["id"] for r in device_spec.get("rails", []) if "id" in r}
    for entry in spec.get("power", []):
        direction = entry.get("direction")
        if direction == "source":
            keys = POWER_SOURCE_KEYS
        elif direction == "passthrough":
            keys = POWER_PASSTHROUGH_KEYS
        elif direction == "load":
            keys = POWER_LOAD_KEYS
        else:
            err(f"power entry has unknown direction {direction!r}: {entry}")
            continue
        for key in keys:
            if key not in entry:
                err(f"power entry {entry.get('rail_id', '?')!r}: missing key {key} for direction {direction!r}")
        if entry.get("rail_id") not in rail_ids:
            err(f"power entry references unknown rail {entry.get('rail_id')!r}")

    for key in REMOVAL_KEYS:
        if key not in spec["removal"]:
            err(f"removal: missing key {key}")

    repairability = spec["repairability"]
    for key in REPAIRABILITY_KEYS:
        if key not in repairability:
            err(f"repairability: missing key {key}")
    if "adhesive" in repairability and not isinstance(repairability["adhesive"], bool):
        err(f"repairability.adhesive should be true/false, got {repairability['adhesive']!r}")

    descriptor = spec["descriptor"]
    for key in DESCRIPTOR_KEYS:
        if key not in descriptor:
            err(f"descriptor: missing key {key}")
    if isinstance(descriptor.get("fields"), list) and not descriptor["fields"]:
        err("descriptor.fields is empty")

    return errors, warnings


def validate_all(modules_dir, device_spec):
    """Return (errors, warnings) across every *.yaml file in modules_dir."""
    errors = []
    warnings = []
    paths = sorted(glob.glob(os.path.join(modules_dir, "*.yaml")))
    found_ids = []
    for path in paths:
        name = os.path.splitext(os.path.basename(path))[0]
        try:
            spec = load(path)
        except SpecLoadError as e:
            errors.append(f"{name}: {e}")
            continue
        found_ids.append(name)
        mod_errors, mod_warnings = validate_module(name, spec, device_spec)
        errors.extend(mod_errors)
        warnings.extend(mod_warnings)

    missing = [m for m in EXPECTED_MODULE_IDS if m not in found_ids]
    extra = [m for m in found_ids if m not in EXPECTED_MODULE_IDS]
    for m in missing:
        errors.append(f"missing module spec for {m!r} (MOD-002's eight v1 module classes)")
    for m in extra:
        errors.append(f"unexpected module spec {m!r} is not one of MOD-002's eight v1 module classes")

    return errors, warnings


def main():
    modules_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODULES_DIR
    device_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DEVICE_PATH

    try:
        device_spec = load(device_path)
    except (SpecLoadError, OSError) as e:
        print(f"FAIL {device_path}: {e}")
        print("validate_modules.py: FAIL (1 failures, 0 warnings)")
        sys.exit(1)

    device_errors, _ = validate_device(device_spec)
    if device_errors:
        for e in device_errors:
            print("FAIL", f"device.yaml: {e}")
        print("validate_modules.py: FAIL (device.yaml did not validate, module fit numbers below are not trustworthy)")
        sys.exit(1)

    errors, warnings = validate_all(modules_dir, device_spec)
    for w in warnings:
        print("WARN", w)
    for e in errors:
        print("FAIL", e)

    n_found = len(EXPECTED_MODULE_IDS) - sum(1 for e in errors if "missing module spec" in e)
    print(f"fit: {n_found}/{len(EXPECTED_MODULE_IDS)} module specs present and checked against their bay")
    print(
        "validate_modules.py:",
        "FAIL" if errors else "OK",
        f"({len(errors)} failures, {len(warnings)} warnings)",
    )
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
