#!/usr/bin/env python3
"""Score each module's disassembly ease from its own spec data. P3's repairability report.

REQ REG-003 asks for "a repairability score computed by the same rubric as the EU index." The
real EU/French repairability index scores five criteria: documentation, disassembly (tools,
fasteners, time), spare-parts availability, spare-parts price, and product-specific criteria.
phone/spec/modules/*.yaml only carries data for the disassembly criterion today (removal.tool,
removal.order_dependency, repairability.fasteners, repairability.adhesive) — documentation
(P6/P9), spare-parts availability and price (P9/P10) are not data yet. This script computes the
disassembly sub-score only, out of 10, and says so: it is not the device's real EU-index score.
REQ REG-003 stays open until P9/U12 reviews the full rubric with the other four criteria filled
in (project/plan.md's U12 acceptance: "no 'unknown' rubric fields").

Per-module disassembly sub-score (10 points), all deterministic from the spec:
  - 3 pts: a single, common tool — "Torx T5" or "none" (tool-less). D-004 mandates one fastener
    type for the whole phone, so every v1 module should already qualify; this line mostly checks
    the constraint hasn't drifted, and flags loudly if it has.
  - 3 pts: fastener count, scaled linearly from 3 pts at 0 fasteners down to 0 pts at
    FASTENER_SCALE_MAX or more. Unknown (null, pending CAD) scores 0 and is flagged as unknown,
    not guessed.
  - 2 pts: zero adhesive (repairability.adhesive is false).
  - 2 pts: no removal-order dependency beyond the back cover MOD-005 already exempts. Any other
    dependency text (e.g. radio.yaml's RF coax pigtail disconnect) scores 0 and is flagged.

The frame module (bay_id: null) is excluded from the device-level average: MOD-005 already
carves it out ("removed last... full teardown"), so per-owner field disassembly is not what it
is being scored for, and its fastener count is unknown pending CAD besides.

Usage: python3 phone/tools/repairability.py [modules-dir] [device.yaml path]
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

FASTENER_SCALE_MAX = 6
ALLOWED_TOOLS = {"torx t5", "none"}


def tool_score(removal):
    tool = (removal.get("tool") or "").strip().lower()
    if tool in ALLOWED_TOOLS:
        return 3.0, None
    return 0.0, f"unexpected tool {removal.get('tool')!r} (D-004 mandates Torx T5 or none)"


def fastener_score(repairability):
    fasteners = repairability.get("fasteners")
    if fasteners is None:
        return 0.0, "fastener count unknown (pending CAD, U7)"
    score = max(0.0, 3.0 * (1 - fasteners / FASTENER_SCALE_MAX))
    return round(score, 2), None


def adhesive_score(repairability):
    adhesive = repairability.get("adhesive")
    if adhesive is None:
        return 0.0, "adhesive flag missing"
    return (0.0 if adhesive else 2.0), None


def order_dependency_score(removal):
    dep = (removal.get("order_dependency") or "").strip().lower()
    if dep.startswith("none"):
        return 2.0, None
    return 0.0, f"removal-order dependency declared: {removal.get('order_dependency')!r}"


def module_score(spec):
    """Return {"total": x, "parts": {...}, "flags": [...]} for one module spec."""
    removal = spec.get("removal", {})
    repairability = spec.get("repairability", {})
    parts = {}
    flags = []
    for key, (score, flag) in {
        "tool": tool_score(removal),
        "fasteners": fastener_score(repairability),
        "adhesive": adhesive_score(repairability),
        "order_dependency": order_dependency_score(removal),
    }.items():
        parts[key] = score
        if flag:
            flags.append(f"{key}: {flag}")
    return {"total": round(sum(parts.values()), 2), "parts": parts, "flags": flags}


def score_all(modules):
    """Return {module_id: module_score(...)} for every module, and the bay-mapped-only average."""
    scores = {module_id: module_score(spec) for module_id, spec in modules.items()}
    scored_ids = [m for m in scores if modules[m].get("module", {}).get("bay_id") is not None]
    average = round(sum(scores[m]["total"] for m in scored_ids) / len(scored_ids), 2) if scored_ids else None
    return scores, average, scored_ids


def load_modules(modules_dir):
    """Return {module_id: spec} for every *.yaml in modules_dir."""
    modules = {}
    for path in sorted(glob.glob(os.path.join(modules_dir, "*.yaml"))):
        name = os.path.splitext(os.path.basename(path))[0]
        modules[name] = load(path)
    return modules


def main():
    modules_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODULES_DIR
    device_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DEVICE_PATH

    try:
        device_spec = load(device_path)
    except (SpecLoadError, OSError) as e:
        print(f"FAIL {device_path}: {e}")
        print("repairability.py: FAIL (1 failures)")
        sys.exit(1)

    device_errors, _ = validate_device(device_spec)
    module_errors, _ = validate_all(modules_dir, device_spec)
    if device_errors or module_errors:
        for e in device_errors + module_errors:
            print("FAIL", e)
        print("repairability.py: FAIL (spec did not validate, scores below are not trustworthy)")
        sys.exit(1)

    modules = load_modules(modules_dir)
    scores, average, scored_ids = score_all(modules)

    print(f"{'module':<14}{'tool':>6}{'fastn':>7}{'adhes':>7}{'order':>7}{'total/10':>10}")
    for module_id in sorted(scores):
        s = scores[module_id]
        p = s["parts"]
        print(
            f"{module_id:<14}{p['tool']:>6.1f}{p['fasteners']:>7.1f}{p['adhesive']:>7.1f}"
            f"{p['order_dependency']:>7.1f}{s['total']:>10.2f}"
        )
        for f in s["flags"]:
            print(f"    flag: {f}")

    print()
    print(f"device disassembly sub-score (mean of {len(scored_ids)} bay-mapped modules, frame excluded): {average}/10")
    print("This is a disassembly-only sub-score, not the full EU-index score REQ REG-003 asks for —")
    print("documentation, spare-parts availability and spare-parts price are not spec data yet.")
    print("repairability.py: OK (0 failures, informational only)")
    sys.exit(0)


if __name__ == "__main__":
    main()
