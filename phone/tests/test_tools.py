#!/usr/bin/env python3
"""Tests for phone/tools/specload.py, validate_spec.py, fit_check.py.

Run: python3 -m unittest discover -s phone/tests
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "phone", "tools"))

import fit_check  # noqa: E402
import specload  # noqa: E402
import validate_spec  # noqa: E402

DEVICE_YAML = os.path.join(ROOT, "phone", "spec", "device.yaml")


def minimal_spec():
    """A small, self-consistent spec matching device.yaml's shape, for negative tests."""
    return {
        "schema_version": 1,
        "device": {"name": "TEST"},
        "envelope": {
            "length_mm": 10.0,
            "width_mm": 10.0,
            "thickness_mm": 10.0,
            "volume_mm3": 1000.0,
            "mass_ceiling_g": 100,
        },
        "structure": {
            "volume_budget_mm3": 100.0,
            "volume_budget_fraction_of_envelope": 0.1,
        },
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
            },
            {
                "id": "b",
                "module_class": "b",
                "length_mm": 5.0,
                "width_mm": 5.0,
                "height_mm": 8.0,
                "volume_mm3": 200.0,
                "clearance_mm": 0.1,
                "zone": "z",
                "connector": "c",
                "lanes": [],
                "rails": ["3V3"],
                "source": ["X-001"],
            },
        ],
        "totals": {
            "bay_volume_mm3": 300.0,
            "structure_volume_mm3": 100.0,
            "used_volume_mm3": 400.0,
            "envelope_volume_mm3": 1000.0,
            "margin_mm3": 600.0,
            "margin_fraction": 0.6,
        },
        "bus": {
            "lane_groups": [
                {"id": "DSI", "protocol": "MIPI DSI", "consumers": ["a"]},
            ],
        },
        "rails": [
            {"id": "3V3", "description": "logic rail", "consumers": ["a", "b"], "source": "X-001"},
        ],
        "ceilings": {"bom_usd": 1, "retail_usd": 2, "mass_g": 100, "thickness_mm": 10.0},
    }


class TestSpecload(unittest.TestCase):
    def test_flat_mapping(self):
        text = "a: 1\nb: 2.5\nc: hello\n"
        self.assertEqual(specload.loads(text), {"a": 1, "b": 2.5, "c": "hello"})

    def test_nested_mapping(self):
        text = "a:\n  b: 1\n  c: 2\n"
        self.assertEqual(specload.loads(text), {"a": {"b": 1, "c": 2}})

    def test_flow_list(self):
        text = 'a: [1, 2, "three"]\n'
        self.assertEqual(specload.loads(text), {"a": [1, 2, "three"]})

    def test_empty_flow_list(self):
        self.assertEqual(specload.loads("a: []\n"), {"a": []})

    def test_sequence_of_scalars(self):
        text = "a:\n  - one\n  - two\n"
        self.assertEqual(specload.loads(text), {"a": ["one", "two"]})

    def test_sequence_of_mappings(self):
        text = "a:\n  - id: x\n    n: 1\n  - id: y\n    n: 2\n"
        self.assertEqual(specload.loads(text), {"a": [{"id": "x", "n": 1}, {"id": "y", "n": 2}]})

    def test_quoted_string_with_embedded_colon(self):
        text = 'k: "host connector: carries everything"\n'
        self.assertEqual(specload.loads(text), {"k": "host connector: carries everything"})

    def test_quoted_string_in_flow_list_with_colon(self):
        text = 'lanes: ["DSI:4", "CSI:2"]\n'
        self.assertEqual(specload.loads(text), {"lanes": ["DSI:4", "CSI:2"]})

    def test_comment_stripped(self):
        text = "a: 1  # a comment\n# full line comment\nb: 2\n"
        self.assertEqual(specload.loads(text), {"a": 1, "b": 2})

    def test_hash_inside_string_not_stripped(self):
        text = 'a: "value # not a comment"\n'
        self.assertEqual(specload.loads(text), {"a": "value # not a comment"})

    def test_booleans_and_null(self):
        text = "a: true\nb: false\nc: null\n"
        self.assertEqual(specload.loads(text), {"a": True, "b": False, "c": None})

    def test_tabs_rejected(self):
        with self.assertRaises(specload.SpecLoadError):
            specload.loads("a:\n\tb: 1\n")

    def test_bad_indent_raises(self):
        with self.assertRaises(specload.SpecLoadError):
            specload.loads("a: 1\n   b: 2\n")

    def test_loads_real_device_yaml(self):
        spec = specload.load(DEVICE_YAML)
        self.assertEqual(spec["schema_version"], 1)
        self.assertEqual(len(spec["bays"]), 7)
        bay_ids = [b["id"] for b in spec["bays"]]
        self.assertEqual(
            bay_ids,
            ["display", "battery", "compute", "camera-rear", "sensor-front", "port", "radio"],
        )
        self.assertEqual(
            spec["bays"][2]["connector"],
            "BC-Bus host connector: carries every lane group and every rail",
        )


class TestValidateSpec(unittest.TestCase):
    def test_real_device_yaml_is_valid(self):
        spec = specload.load(DEVICE_YAML)
        errors, warnings = validate_spec.validate(spec)
        self.assertEqual(errors, [])

    def test_minimal_spec_is_valid(self):
        errors, warnings = validate_spec.validate(minimal_spec())
        self.assertEqual(errors, [])

    def test_missing_top_level_key(self):
        spec = minimal_spec()
        del spec["rails"]
        errors, _ = validate_spec.validate(spec)
        self.assertTrue(any("rails" in e for e in errors))

    def test_bay_volume_mismatch(self):
        spec = minimal_spec()
        spec["bays"][0]["volume_mm3"] = 999.0
        errors, _ = validate_spec.validate(spec)
        self.assertTrue(any("bay a: volume_mm3" in e for e in errors))

    def test_duplicate_bay_id(self):
        spec = minimal_spec()
        spec["bays"][1]["id"] = "a"
        errors, _ = validate_spec.validate(spec)
        self.assertTrue(any("not unique" in e for e in errors))

    def test_unknown_lane_group_reference(self):
        spec = minimal_spec()
        spec["bays"][0]["lanes"] = ["CSI:1"]
        errors, _ = validate_spec.validate(spec)
        self.assertTrue(any("unknown lane group" in e for e in errors))

    def test_unknown_rail_reference(self):
        spec = minimal_spec()
        spec["bays"][0]["rails"] = ["1V8"]
        errors, _ = validate_spec.validate(spec)
        self.assertTrue(any("unknown rail" in e for e in errors))

    def test_totals_bay_volume_mismatch(self):
        spec = minimal_spec()
        spec["totals"]["bay_volume_mm3"] = 1.0
        errors, _ = validate_spec.validate(spec)
        self.assertTrue(any("totals.bay_volume_mm3" in e for e in errors))

    def test_gate_failure_when_used_exceeds_envelope(self):
        spec = minimal_spec()
        spec["totals"]["used_volume_mm3"] = 2000.0
        spec["totals"]["margin_mm3"] = -1000.0
        spec["totals"]["margin_fraction"] = -1.0
        errors, _ = validate_spec.validate(spec)
        self.assertTrue(any("P2 gate failed" in e for e in errors))

    def test_envelope_volume_mismatch(self):
        spec = minimal_spec()
        spec["envelope"]["volume_mm3"] = 5.0
        errors, _ = validate_spec.validate(spec)
        self.assertTrue(any("envelope.volume_mm3" in e for e in errors))


class TestFitCheck(unittest.TestCase):
    def test_bay_report_covers_every_bay(self):
        spec = specload.load(DEVICE_YAML)
        rows = fit_check.bay_report(spec)
        self.assertEqual(len(rows), len(spec["bays"]))
        self.assertEqual([r["id"] for r in rows], [b["id"] for b in spec["bays"]])

    def test_bay_report_computed_volume_matches_declared(self):
        spec = specload.load(DEVICE_YAML)
        for row in fit_check.bay_report(spec):
            self.assertAlmostEqual(row["computed_volume_mm3"], row["declared_volume_mm3"], delta=0.1)

    def test_footprint_volume_larger_than_bay_volume(self):
        spec = specload.load(DEVICE_YAML)
        for row in fit_check.bay_report(spec):
            self.assertGreater(row["footprint_volume_mm3"], row["computed_volume_mm3"])

    def test_totals_report_fits_real_device(self):
        spec = specload.load(DEVICE_YAML)
        totals = fit_check.totals_report(spec)
        self.assertTrue(totals["fits"])
        self.assertEqual(totals["bay_count"], 7)

    def test_totals_report_flags_overflow(self):
        spec = minimal_spec()
        spec["totals"]["used_volume_mm3"] = 2000.0
        totals = fit_check.totals_report(spec)
        self.assertFalse(totals["fits"])


if __name__ == "__main__":
    unittest.main()
