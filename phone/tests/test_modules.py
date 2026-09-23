#!/usr/bin/env python3
"""Tests for phone/tools/validate_modules.py.

Run: python3 -m unittest discover -s phone/tests
"""
import copy
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "phone", "tools"))

import specload  # noqa: E402
import validate_modules  # noqa: E402

DEVICE_YAML = os.path.join(ROOT, "phone", "spec", "device.yaml")
MODULES_DIR = os.path.join(ROOT, "phone", "spec", "modules")


def minimal_device_spec():
    """Mirrors test_tools.minimal_spec()'s shape: one bay, one rail, one lane group."""
    return {
        "schema_version": 1,
        "device": {"name": "TEST"},
        "envelope": {"length_mm": 10.0, "width_mm": 10.0, "thickness_mm": 10.0, "volume_mm3": 1000.0, "mass_ceiling_g": 100},
        "structure": {"volume_budget_mm3": 100.0, "volume_budget_fraction_of_envelope": 0.1},
        "bays": [
            {
                "id": "a",
                "module_class": "a",
                "length_mm": 5.0,
                "width_mm": 5.0,
                "height_mm": 4.0,
                "volume_mm3": 100.0,
                "clearance_mm": 0.1,
                "zone": "z",
                "connector": "c",
                "lanes": ["DSI:1"],
                "rails": ["3V3"],
                "source": ["X-001"],
            }
        ],
        "totals": {
            "bay_volume_mm3": 100.0,
            "structure_volume_mm3": 100.0,
            "used_volume_mm3": 200.0,
            "envelope_volume_mm3": 1000.0,
            "margin_mm3": 800.0,
            "margin_fraction": 0.8,
        },
        "bus": {"lane_groups": [{"id": "DSI", "protocol": "MIPI DSI", "consumers": ["a"]}]},
        "rails": [{"id": "3V3", "description": "logic rail", "consumers": ["a"], "source": "X-001"}],
        "ceilings": {"bom_usd": 1, "retail_usd": 2, "mass_g": 100, "thickness_mm": 10.0},
    }


def minimal_module_spec():
    """A module spec matching minimal_device_spec()'s bay 'a', for negative tests."""
    return {
        "schema_version": 1,
        "module": {
            "id": "a",
            "bay_id": "a",
            "name": "A module",
            "description": "d",
            "status": "architecture-stage",
            "source": ["X-001"],
        },
        "footprint": {"length_mm": 5.0, "width_mm": 5.0, "height_mm": 4.0, "volume_mm3": 100.0, "mass_budget_g": 1},
        "lanes": ["DSI:1"],
        "power": [{"rail_id": "3V3", "direction": "load", "typical_ma": 1, "max_ma": 2, "source": ["X-001"]}],
        "removal": {"tool": "none", "time_target_s": 60, "order_dependency": "none", "source": ["X-001"]},
        "repairability": {"fasteners": 0, "adhesive": False, "source": ["X-001"]},
        "descriptor": {"medium": "eeprom", "fields": ["vendor"], "source": ["X-001"]},
    }


class TestRealModuleSpecs(unittest.TestCase):
    def test_all_eight_validate_and_fit(self):
        device_spec = specload.load(DEVICE_YAML)
        errors, warnings = validate_modules.validate_all(MODULES_DIR, device_spec)
        self.assertEqual(errors, [])

    def test_frame_has_no_bay(self):
        device_spec = specload.load(DEVICE_YAML)
        frame = specload.load(os.path.join(MODULES_DIR, "frame.yaml"))
        self.assertIsNone(frame["module"]["bay_id"])
        bay_ids = {b["id"] for b in device_spec["bays"]}
        self.assertNotIn("frame", bay_ids)

    def test_every_bay_mapped_module_matches_its_bay_dims(self):
        device_spec = specload.load(DEVICE_YAML)
        bays = {b["id"]: b for b in device_spec["bays"]}
        for module_id, bay_id in [
            ("compute", "compute"),
            ("display", "display"),
            ("battery", "battery"),
            ("camera-rear", "camera-rear"),
            ("sensor-front", "sensor-front"),
            ("port", "port"),
            ("radio", "radio"),
        ]:
            spec = specload.load(os.path.join(MODULES_DIR, f"{module_id}.yaml"))
            fp = spec["footprint"]
            bay = bays[bay_id]
            self.assertAlmostEqual(fp["length_mm"], bay["length_mm"], delta=1e-6)
            self.assertAlmostEqual(fp["width_mm"], bay["width_mm"], delta=1e-6)
            self.assertAlmostEqual(fp["height_mm"], bay["height_mm"], delta=1e-6)
            self.assertEqual(spec["lanes"], bay["lanes"])


class TestValidateModule(unittest.TestCase):
    def test_minimal_module_is_valid(self):
        errors, warnings = validate_modules.validate_module("a", minimal_module_spec(), minimal_device_spec())
        self.assertEqual(errors, [])

    def test_filename_id_mismatch(self):
        spec = minimal_module_spec()
        errors, _ = validate_modules.validate_module("wrong-name", spec, minimal_device_spec())
        self.assertTrue(any("does not match filename" in e for e in errors))

    def test_unexpected_module_file_reported_by_validate_all(self):
        device_spec = specload.load(DEVICE_YAML)
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(MODULES_DIR, tmp, dirs_exist_ok=True)
            shutil.copy(os.path.join(tmp, "frame.yaml"), os.path.join(tmp, "extra.yaml"))
            errors, _ = validate_modules.validate_all(tmp, device_spec)
            self.assertTrue(any("unexpected module spec" in e for e in errors))

    def test_missing_bay_reference(self):
        spec = minimal_module_spec()
        spec["module"]["bay_id"] = "nonexistent"
        errors, _ = validate_modules.validate_module("a", spec, minimal_device_spec())
        self.assertTrue(any("does not exist in device.yaml bays" in e for e in errors))

    def test_footprint_volume_mismatch(self):
        spec = minimal_module_spec()
        spec["footprint"]["volume_mm3"] = 999.0
        errors, _ = validate_modules.validate_module("a", spec, minimal_device_spec())
        self.assertTrue(any("does not match length*width*height" in e for e in errors))

    def test_footprint_dim_does_not_match_bay(self):
        spec = minimal_module_spec()
        spec["footprint"]["length_mm"] = 6.0
        spec["footprint"]["volume_mm3"] = 120.0
        errors, _ = validate_modules.validate_module("a", spec, minimal_device_spec())
        self.assertTrue(any("does not match bay" in e for e in errors))

    def test_lanes_do_not_match_bay(self):
        spec = minimal_module_spec()
        spec["lanes"] = ["CSI:1"]
        errors, _ = validate_modules.validate_module("a", spec, minimal_device_spec())
        self.assertTrue(any("does not match bay" in e and "lanes" in e for e in errors))

    def test_power_rail_not_on_bay(self):
        spec = minimal_module_spec()
        spec["power"][0]["rail_id"] = "1V8"
        errors, _ = validate_modules.validate_module("a", spec, minimal_device_spec())
        self.assertTrue(any("is not declared for bay" in e for e in errors))

    def test_power_rail_unknown_to_device(self):
        spec = minimal_module_spec()
        spec["power"][0]["rail_id"] = "NOPE"
        device_spec = minimal_device_spec()
        device_spec["bays"][0]["rails"].append("NOPE")
        errors, _ = validate_modules.validate_module("a", spec, device_spec)
        self.assertTrue(any("unknown rail" in e for e in errors))

    def test_frame_like_module_no_bay_within_structure_budget(self):
        device_spec = minimal_device_spec()
        spec = copy.deepcopy(minimal_module_spec())
        spec["module"]["id"] = "frame"
        spec["module"]["bay_id"] = None
        spec["lanes"] = []
        spec["power"] = []
        spec["footprint"] = {"length_mm": None, "width_mm": None, "height_mm": None, "volume_mm3": 50.0, "mass_budget_g": None}
        errors, _ = validate_modules.validate_module("frame", spec, device_spec)
        self.assertEqual(errors, [])

    def test_frame_like_module_exceeds_structure_budget(self):
        device_spec = minimal_device_spec()
        spec = copy.deepcopy(minimal_module_spec())
        spec["module"]["id"] = "frame"
        spec["module"]["bay_id"] = None
        spec["lanes"] = []
        spec["power"] = []
        spec["footprint"] = {"length_mm": None, "width_mm": None, "height_mm": None, "volume_mm3": 500.0, "mass_budget_g": None}
        errors, _ = validate_modules.validate_module("frame", spec, device_spec)
        self.assertTrue(any("exceeds structure.volume_budget_mm3" in e for e in errors))

    def test_missing_module_spec_file_is_reported(self):
        device_spec = specload.load(DEVICE_YAML)
        errors, _ = validate_modules.validate_all("/nonexistent/dir", device_spec)
        self.assertEqual(len(errors), len(validate_modules.EXPECTED_MODULE_IDS))


if __name__ == "__main__":
    unittest.main()
