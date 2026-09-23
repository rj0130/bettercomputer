#!/usr/bin/env python3
"""Tests for phone/tools/{power_budget,bom_rollup,repairability,report}.py.

Run: python3 -m unittest discover -s phone/tests
"""
import contextlib
import io
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "phone", "tools"))

import bom_rollup  # noqa: E402
import power_budget  # noqa: E402
import repairability  # noqa: E402
import report  # noqa: E402
import specload  # noqa: E402

DEVICE_YAML = os.path.join(ROOT, "phone", "spec", "device.yaml")
MODULES_DIR = os.path.join(ROOT, "phone", "spec", "modules")

REAL_MODULE_IDS = [
    "battery", "camera-rear", "compute", "display", "frame", "port", "radio", "sensor-front",
]


def load_real_modules():
    return power_budget.load_modules(MODULES_DIR)


def load_real_device():
    return specload.load(DEVICE_YAML)


def synthetic_modules():
    """A small, self-consistent set of module specs covering load/source/passthrough directions."""
    return {
        "load-mod": {
            "module": {"id": "load-mod", "bay_id": "a"},
            "footprint": {"mass_budget_g": 10},
            "power": [
                {"rail_id": "3V3", "direction": "load", "typical_ma": 100, "max_ma": 300},
            ],
            "removal": {"tool": "Torx T5", "order_dependency": "none, other than the back cover"},
            "repairability": {"fasteners": 0, "adhesive": False},
        },
        "src-mod": {
            "module": {"id": "src-mod", "bay_id": "b"},
            "footprint": {"mass_budget_g": 20},
            "power": [
                {"rail_id": "VBAT", "direction": "source", "capacity_mah": 4000},
            ],
            "removal": {"tool": "none", "order_dependency": "none"},
            "repairability": {"fasteners": 0, "adhesive": False},
        },
        "pass-mod": {
            "module": {"id": "pass-mod", "bay_id": None},
            "footprint": {"mass_budget_g": None},
            "power": [
                {"rail_id": "VBUS", "direction": "passthrough", "max_ma": 3000},
            ],
            "removal": {"tool": "full teardown", "order_dependency": "removed last, everything else first"},
            "repairability": {"fasteners": None, "adhesive": True},
        },
    }


class TestPowerBudget(unittest.TestCase):
    def test_load_direction_only_counted(self):
        modules = synthetic_modules()
        rails = power_budget.scenario_rail_totals("idle", {"load-mod": modules["load-mod"]})
        self.assertIn("3V3", rails)

    def test_source_direction_excluded(self):
        modules = synthetic_modules()
        rails = power_budget.scenario_rail_totals("idle", {"src-mod": modules["src-mod"]})
        self.assertEqual(rails, {})

    def test_passthrough_direction_excluded(self):
        modules = synthetic_modules()
        rails = power_budget.scenario_rail_totals("idle", {"pass-mod": modules["pass-mod"]})
        self.assertEqual(rails, {})

    def test_module_missing_from_scenario_defaults_off(self):
        modules = {"unlisted-mod": synthetic_modules()["load-mod"]}
        rails = power_budget.scenario_rail_totals("idle", modules)
        self.assertEqual(rails["3V3"]["total_ma"], 0.0)

    def test_max_level_uses_max_ma(self):
        power_budget.SCENARIOS["idle"]["load-mod"] = "max"
        try:
            rails = power_budget.scenario_rail_totals("idle", {"load-mod": synthetic_modules()["load-mod"]})
        finally:
            del power_budget.SCENARIOS["idle"]["load-mod"]
        self.assertEqual(rails["3V3"]["total_ma"], 300.0)

    def test_typical_level_uses_typical_ma(self):
        power_budget.SCENARIOS["idle"]["load-mod"] = "typical"
        try:
            rails = power_budget.scenario_rail_totals("idle", {"load-mod": synthetic_modules()["load-mod"]})
        finally:
            del power_budget.SCENARIOS["idle"]["load-mod"]
        self.assertEqual(rails["3V3"]["total_ma"], 100.0)

    def test_all_scenarios_covers_every_scenario_name(self):
        results = power_budget.all_scenarios(load_real_modules())
        self.assertEqual(set(results.keys()), set(power_budget.SCENARIO_ORDER))

    def test_real_modules_every_rail_total_nonnegative(self):
        results = power_budget.all_scenarios(load_real_modules())
        for rails in results.values():
            for row in rails.values():
                self.assertGreaterEqual(row["total_ma"], 0.0)

    def test_load_modules_finds_all_real_modules(self):
        modules = power_budget.load_modules(MODULES_DIR)
        self.assertEqual(sorted(modules.keys()), sorted(REAL_MODULE_IDS))


class TestBomRollup(unittest.TestCase):
    def test_mass_rollup_sums_known_masses(self):
        modules = {"load-mod": synthetic_modules()["load-mod"], "src-mod": synthetic_modules()["src-mod"]}
        result = bom_rollup.mass_rollup(modules, {"ceilings": {"mass_g": 100}})
        self.assertEqual(result["total_g"], 30)
        self.assertEqual(result["missing"], [])

    def test_mass_rollup_excludes_missing_from_total(self):
        modules = synthetic_modules()  # includes pass-mod with mass_budget_g: None
        result = bom_rollup.mass_rollup(modules, {"ceilings": {"mass_g": 100}})
        self.assertEqual(result["total_g"], 30)  # only load-mod (10) + src-mod (20)
        self.assertEqual(result["missing"], ["pass-mod"])

    def test_cost_rollup_none_when_any_module_missing_cost(self):
        modules = synthetic_modules()
        result = bom_rollup.cost_rollup(modules, {"ceilings": {"bom_usd": 260}})
        self.assertIsNone(result["total_usd"])
        self.assertEqual(len(result["missing"]), 3)

    def test_cost_rollup_sums_when_all_present(self):
        modules = {
            "a": {"cost": {"usd": 10}},
            "b": {"cost": {"usd": 20}},
        }
        result = bom_rollup.cost_rollup(modules, {"ceilings": {"bom_usd": 260}})
        self.assertEqual(result["total_usd"], 30)

    def test_real_modules_mass_total_under_ceiling(self):
        device_spec = load_real_device()
        result = bom_rollup.mass_rollup(load_real_modules(), device_spec)
        self.assertLessEqual(result["total_g"], device_spec["ceilings"]["mass_g"])
        self.assertIn("frame", result["missing"])

    def test_real_modules_cost_not_yet_computable(self):
        device_spec = load_real_device()
        result = bom_rollup.cost_rollup(load_real_modules(), device_spec)
        self.assertIsNone(result["total_usd"])
        self.assertEqual(sorted(result["missing"]), sorted(REAL_MODULE_IDS))

    def test_main_fails_when_mass_exceeds_ceiling(self):
        tmpdir = tempfile.mkdtemp()
        try:
            module_dir = os.path.join(tmpdir, "modules")
            os.makedirs(module_dir)
            shutil.copy(os.path.join(MODULES_DIR, "battery.yaml"), module_dir)
            device_path = os.path.join(tmpdir, "device.yaml")
            # A tiny self-consistent device spec with a mass ceiling below battery's mass_budget_g (55g).
            with open(device_path, "w") as f:
                f.write(
                    "schema_version: 1\n"
                    "device:\n  name: TEST\n"
                    "envelope:\n  length_mm: 10.0\n  width_mm: 10.0\n  thickness_mm: 10.0\n"
                    "  volume_mm3: 1000.0\n  mass_ceiling_g: 1\n"
                    "structure:\n  volume_budget_mm3: 27744.0\n  volume_budget_fraction_of_envelope: 0.1\n"
                    "bays:\n"
                    "  - id: battery\n    module_class: battery\n    length_mm: 68.0\n    width_mm: 68.0\n"
                    "    height_mm: 6.0\n    volume_mm3: 27744.0\n    clearance_mm: 0.3\n    zone: z\n"
                    "    connector: c\n    lanes: []\n    rails: [VBAT]\n    source: [X-001]\n"
                    "totals:\n  bay_volume_mm3: 27744.0\n  structure_volume_mm3: 27744.0\n"
                    "  used_volume_mm3: 55488.0\n  envelope_volume_mm3: 1000.0\n  margin_mm3: -54488.0\n"
                    "  margin_fraction: -54.5\n"
                    "bus:\n  lane_groups: []\n"
                    "rails:\n  - id: VBAT\n    description: d\n    consumers: [battery]\n    source: X-001\n"
                    "ceilings:\n  bom_usd: 1\n  retail_usd: 2\n  mass_g: 1\n  thickness_mm: 10.0\n"
                )
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                with self.assertRaises(SystemExit) as ctx:
                    sys.argv = ["bom_rollup.py", module_dir, device_path]
                    bom_rollup.main()
            self.assertEqual(ctx.exception.code, 1)
        finally:
            shutil.rmtree(tmpdir)


class TestRepairability(unittest.TestCase):
    def test_tool_score_allows_torx_t5_and_none(self):
        score, flag = repairability.tool_score({"tool": "Torx T5"})
        self.assertEqual(score, 3.0)
        self.assertIsNone(flag)
        score, flag = repairability.tool_score({"tool": "none"})
        self.assertEqual(score, 3.0)
        self.assertIsNone(flag)

    def test_tool_score_flags_unexpected_tool(self):
        score, flag = repairability.tool_score({"tool": "full teardown"})
        self.assertEqual(score, 0.0)
        self.assertIsNotNone(flag)

    def test_fastener_score_scales_down(self):
        zero, _ = repairability.fastener_score({"fasteners": 0})
        three, _ = repairability.fastener_score({"fasteners": repairability.FASTENER_SCALE_MAX})
        over, _ = repairability.fastener_score({"fasteners": repairability.FASTENER_SCALE_MAX + 10})
        self.assertEqual(zero, 3.0)
        self.assertEqual(three, 0.0)
        self.assertEqual(over, 0.0)

    def test_fastener_score_unknown_flags(self):
        score, flag = repairability.fastener_score({"fasteners": None})
        self.assertEqual(score, 0.0)
        self.assertIsNotNone(flag)

    def test_adhesive_score(self):
        self.assertEqual(repairability.adhesive_score({"adhesive": False})[0], 2.0)
        self.assertEqual(repairability.adhesive_score({"adhesive": True})[0], 0.0)

    def test_order_dependency_score_none_prefix(self):
        score, flag = repairability.order_dependency_score({"order_dependency": "none, other than the back cover"})
        self.assertEqual(score, 2.0)
        self.assertIsNone(flag)

    def test_order_dependency_score_flags_real_dependency(self):
        score, flag = repairability.order_dependency_score({"order_dependency": "the RF coax pigtail must be detached first"})
        self.assertEqual(score, 0.0)
        self.assertIsNotNone(flag)

    def test_module_score_totals_out_of_ten(self):
        s = repairability.module_score(synthetic_modules()["load-mod"])
        self.assertEqual(s["total"], 10.0)
        self.assertEqual(s["flags"], [])

    def test_frame_excluded_from_device_average(self):
        modules = load_real_modules()
        scores, average, scored_ids = repairability.score_all(modules)
        self.assertNotIn("frame", scored_ids)
        self.assertEqual(len(scored_ids), 7)
        self.assertIn("frame", scores)  # still scored individually, just excluded from the average

    def test_radio_flagged_for_order_dependency(self):
        modules = load_real_modules()
        scores, _, _ = repairability.score_all(modules)
        self.assertTrue(any("order_dependency" in f for f in scores["radio"]["flags"]))

    def test_device_average_in_range(self):
        modules = load_real_modules()
        _, average, _ = repairability.score_all(modules)
        self.assertGreater(average, 0.0)
        self.assertLessEqual(average, 10.0)


class TestReport(unittest.TestCase):
    def test_render_fit_md_reports_gate(self):
        device_spec = load_real_device()
        md, fits = report.render_fit_md(device_spec)
        self.assertTrue(fits)
        self.assertIn("P2 gate", md)

    def test_render_power_md_has_every_scenario(self):
        md = report.render_power_md(load_real_modules())
        for name in power_budget.SCENARIO_ORDER:
            self.assertIn(f"## {name}", md)

    def test_render_bom_md_states_cost_not_computable(self):
        md, mass_fail = report.render_bom_md(load_real_modules(), load_real_device())
        self.assertFalse(mass_fail)
        self.assertIn("Not computable", md)

    def test_render_repairability_md_has_device_score(self):
        md = report.render_repairability_md(load_real_modules())
        self.assertIn("disassembly sub-score", md)

    def test_main_writes_all_five_files(self):
        tmpdir = tempfile.mkdtemp()
        try:
            build_dir = os.path.join(tmpdir, "build")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                with self.assertRaises(SystemExit) as ctx:
                    sys.argv = ["report.py", MODULES_DIR, DEVICE_YAML, build_dir]
                    report.main()
            self.assertEqual(ctx.exception.code, 0)
            for filename in ("fit.md", "power-budget.md", "bom.md", "repairability.md", "report.md"):
                self.assertTrue(os.path.isfile(os.path.join(build_dir, filename)), filename)
        finally:
            shutil.rmtree(tmpdir)


if __name__ == "__main__":
    unittest.main()
