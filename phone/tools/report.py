#!/usr/bin/env python3
"""Write phone/build/*.md: the first generated reports (P3 gate, design-path.md).

Runs fit_check, power_budget, bom_rollup and repairability against the real spec tree and
renders each as a markdown file under phone/build/, plus a report.md index that links them and
states the P3 gate condition. Every number in these files still traces back to whatever
[UNVERIFIED] flag its source module/device YAML carries; report.py does not add confidence, only
formatting.

Writes:
  phone/build/fit.md            (from fit_check.py)
  phone/build/power-budget.md   (from power_budget.py)
  phone/build/bom.md            (mass + cost, from bom_rollup.py)
  phone/build/repairability.md  (from repairability.py)
  phone/build/report.md         (index + P3 gate statement)

Usage: python3 phone/tools/report.py [modules-dir] [device.yaml path] [build-dir]
Exit 1 on a spec load/validate failure, or if fit_check's envelope gate or bom_rollup's mass
gate fails. power_budget and repairability never fail the gate (see their own docstrings).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bom_rollup  # noqa: E402
import fit_check  # noqa: E402
import power_budget  # noqa: E402
import repairability  # noqa: E402
from specload import SpecLoadError, load  # noqa: E402
from validate_modules import validate_all  # noqa: E402
from validate_spec import validate as validate_device  # noqa: E402

DEFAULT_MODULES_DIR = "phone/spec/modules"
DEFAULT_DEVICE_PATH = "phone/spec/device.yaml"
DEFAULT_BUILD_DIR = "phone/build"


def render_fit_md(spec):
    rows = fit_check.bay_report(spec)
    totals = fit_check.totals_report(spec)
    lines = ["# Fit report", "", "Source: `phone/tools/fit_check.py` against `phone/spec/device.yaml`.", ""]
    lines.append("| bay | class | declared mm3 | computed mm3 | +clearance mm3 |")
    lines.append("|---|---|---:|---:|---:|")
    for row in rows:
        lines.append(
            f"| {row['id']} | {row['module_class']} | {row['declared_volume_mm3']:.1f} | "
            f"{row['computed_volume_mm3']:.1f} | {row['footprint_volume_mm3']:.1f} |"
        )
    lines += [
        "",
        f"- bays reported: {totals['bay_count']}",
        f"- bay volume: {totals['bay_volume_mm3']:.1f} mm3",
        f"- structure volume: {totals['structure_volume_mm3']:.1f} mm3",
        f"- used volume: {totals['used_volume_mm3']:.1f} mm3",
        f"- envelope volume: {totals['envelope_volume_mm3']:.1f} mm3",
        f"- margin: {totals['margin_mm3']:.1f} mm3",
        f"- P2 gate (used <= envelope): {'PASS' if totals['fits'] else 'FAIL'}",
        "",
    ]
    return "\n".join(lines), totals["fits"]


def render_power_md(modules):
    results = power_budget.all_scenarios(modules)
    lines = ["# Power budget report", "", "Source: `phone/tools/power_budget.py`.", ""]
    lines.append(
        "No rail carries a budget in `phone/spec/device.yaml` yet (P5); this report is "
        "informational, not a gate. Scenario module-activity levels are a modeling sketch "
        "(see `power_budget.py`'s `SCENARIOS`), and every mA figure traces back to an "
        "`[UNVERIFIED]` placeholder in `phone/spec/modules/*.yaml` (U5)."
    )
    for name in power_budget.SCENARIO_ORDER:
        lines.append("")
        lines.append(f"## {name}")
        lines.append("")
        lines.append("| rail | total mA | detail |")
        lines.append("|---|---:|---|")
        rails = results[name]
        for rail_id in sorted(rails):
            row = rails[rail_id]
            detail = ", ".join(f"{m}={lvl}:{ma:.0f}mA" for m, lvl, ma in row["modules"] if ma) or "—"
            lines.append(f"| {rail_id} | {row['total_ma']:.0f} | {detail} |")
    lines.append("")
    return "\n".join(lines)


def render_bom_md(modules, device_spec):
    mass = bom_rollup.mass_rollup(modules, device_spec)
    cost = bom_rollup.cost_rollup(modules, device_spec)
    mass_fail = mass["ceiling_g"] is not None and mass["total_g"] > mass["ceiling_g"]

    lines = ["# Mass / BOM report", "", "Source: `phone/tools/bom_rollup.py`.", ""]
    lines.append("## Mass (modules only — excludes frame, back cover, fasteners)")
    lines.append("")
    lines.append("| module | mass_budget_g |")
    lines.append("|---|---:|")
    for row in mass["rows"]:
        g = row["mass_budget_g"]
        lines.append(f"| {row['module_id']} | {g if g is not None else 'UNVERIFIED'} |")
    lines.append(f"| **total** | **{mass['total_g']:.1f}** (ceiling {mass['ceiling_g']}) |")
    if mass["missing"]:
        lines.append("")
        lines.append(f"Missing mass data: {', '.join(mass['missing'])} (excluded from total, not zero).")
    lines.append("")
    if mass_fail:
        lines.append(f"**FAIL**: modules-only total ({mass['total_g']:.1f}g) already exceeds the {mass['ceiling_g']}g ceiling.")
    elif mass["missing"]:
        headroom = mass["ceiling_g"] - mass["total_g"]
        lines.append(f"Provisional: {headroom:.1f}g headroom left for {', '.join(mass['missing'])} + structure. Not a confirmed PASS.")
    else:
        lines.append("PASS (all module mass data present and under ceiling).")

    lines.append("")
    lines.append("## Cost (BOM)")
    lines.append("")
    if cost["total_usd"] is None:
        lines.append(f"Not computable: {', '.join(cost['missing'])} carry no `cost.usd` field yet.")
        lines.append(f"`ceilings.bom_usd` ({cost['ceiling_usd']}) cannot be checked until P10/U13 supplies real figures.")
    else:
        lines.append(f"Total: ${cost['total_usd']:.2f} (ceiling ${cost['ceiling_usd']}).")
        lines.append("PASS" if cost["total_usd"] <= cost["ceiling_usd"] else "**FAIL**: BOM exceeds ceiling.")
    lines.append("")
    return "\n".join(lines), mass_fail


def render_repairability_md(modules):
    scores, average, scored_ids = repairability.score_all(modules)
    lines = ["# Repairability report", "", "Source: `phone/tools/repairability.py`.", ""]
    lines.append(
        "Disassembly-only sub-score out of 10, not the full EU-index score REQ REG-003 asks for — "
        "documentation, spare-parts availability and spare-parts price are not spec data yet. See "
        "`repairability.py`'s docstring for the rubric."
    )
    lines.append("")
    lines.append("| module | tool | fasteners | adhesive | order dep. | total/10 |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for module_id in sorted(scores):
        s = scores[module_id]
        p = s["parts"]
        lines.append(
            f"| {module_id} | {p['tool']:.1f} | {p['fasteners']:.1f} | {p['adhesive']:.1f} | "
            f"{p['order_dependency']:.1f} | {s['total']:.2f} |"
        )
    lines.append("")
    for module_id in sorted(scores):
        for f in scores[module_id]["flags"]:
            lines.append(f"- `{module_id}`: {f}")
    lines.append("")
    lines.append(f"Device disassembly sub-score (mean of {len(scored_ids)} bay-mapped modules, frame excluded): **{average}/10**.")
    lines.append("")
    return "\n".join(lines)


def render_index_md(fit_fits, mass_fail):
    p3_pass = fit_fits and not mass_fail
    lines = [
        "# BC-1 build reports",
        "",
        "Generated by `phone/tools/report.py`. Re-run it after any spec change; do not hand-edit these files.",
        "",
        "- [fit.md](fit.md) — P2 gate: bay + structure volume fits the envelope",
        "- [power-budget.md](power-budget.md) — per-rail current draw across four scenarios (informational, no budget set yet)",
        "- [bom.md](bom.md) — mass rollup against the mass ceiling; BOM cost rollup (not yet computable)",
        "- [repairability.md](repairability.md) — disassembly-only sub-score per module",
        "",
        "## P3 gate (design-path.md)",
        "",
        "> `report.py` produces fit, mass, power, cost and repairability reports with zero failures; tests pass.",
        "",
        f"- fit.md envelope gate: {'PASS' if fit_fits else 'FAIL'}",
        f"- bom.md mass gate: {'FAIL' if mass_fail else 'PASS (or provisional, see bom.md)'}",
        f"- power-budget.md and repairability.md: informational only, no gate to fail (see each file)",
        "",
        f"**Reports generated with zero script failures: {'yes' if p3_pass else 'no — see FAIL lines above'}.**",
        "",
        "Cost is not yet computable (no module spec carries a `cost` block); the BOM-vs-ceiling",
        "gate design-path.md assigns to P10 stays open until P10/U13.",
        "",
    ]
    return "\n".join(lines), p3_pass


def main():
    modules_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODULES_DIR
    device_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DEVICE_PATH
    build_dir = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_BUILD_DIR

    try:
        device_spec = load(device_path)
    except (SpecLoadError, OSError) as e:
        print(f"FAIL {device_path}: {e}")
        print("report.py: FAIL (1 failures)")
        sys.exit(1)

    device_errors, _ = validate_device(device_spec)
    module_errors, _ = validate_all(modules_dir, device_spec)
    if device_errors or module_errors:
        for e in device_errors + module_errors:
            print("FAIL", e)
        print("report.py: FAIL (spec did not validate, no reports written)")
        sys.exit(1)

    modules = power_budget.load_modules(modules_dir)

    fit_md, fit_fits = render_fit_md(device_spec)
    power_md = render_power_md(modules)
    bom_md, mass_fail = render_bom_md(modules, device_spec)
    repair_md = render_repairability_md(modules)
    index_md, p3_pass = render_index_md(fit_fits, mass_fail)

    os.makedirs(build_dir, exist_ok=True)
    files = {
        "fit.md": fit_md,
        "power-budget.md": power_md,
        "bom.md": bom_md,
        "repairability.md": repair_md,
        "report.md": index_md,
    }
    for filename, content in files.items():
        with open(os.path.join(build_dir, filename), "w") as f:
            f.write(content)
        print(f"wrote {os.path.join(build_dir, filename)}")

    print()
    print("report.py:", "OK" if (fit_fits and not mass_fail) else "FAIL", f"(P3 gate {'PASS' if p3_pass else 'FAIL'})")
    sys.exit(0 if (fit_fits and not mass_fail) else 1)


if __name__ == "__main__":
    main()
