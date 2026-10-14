"""Compile the production parser and actual YAML lambda with synthetic host data."""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG = "patterns/ble-temp-sensor/inkbird-ibs-th1.yaml"


def mapping(node):
    return {key.value: value for key, value in node.value}


class InkbirdNativeTests(unittest.TestCase):
    def test_production_parser_and_actual_lambda_under_sanitizers(self):
        document = mapping(yaml.compose((ROOT / CONFIG).read_text()))
        tracker = mapping(document["esp32_ble_tracker"])
        self.assertEqual(mapping(tracker["scan_parameters"])["active"].value, "false")
        trigger = mapping(tracker["on_ble_advertise"].value[0])
        self.assertEqual(trigger["mac_address"].tag, "!secret")
        self.assertEqual(trigger["mac_address"].value, "inkbird_th1_mac")
        body = mapping(trigger["then"].value[0])["lambda"].value
        self.assertIn("decode_inkbird_th1_internal", body)
        includes = mapping(document["esphome"])["includes"]
        self.assertEqual([item.value for item in includes.value], ["inkbird_th1_parser.h"])
        compiler = shutil.which(os.environ.get("CXX", "clang++"))
        self.assertIsNotNone(compiler, "Install a Clang compiler with ASan and UBSan")
        with tempfile.TemporaryDirectory(prefix="inkbird-host-") as temporary:
            work = Path(temporary)
            source = work / "test.cpp"
            source.write_text((ROOT / "tests/inkbird_native.cpp").read_text().replace("// ACTUAL_YAML_LAMBDA", body))
            binary = work / "test"
            subprocess.run([compiler, "-std=c++17", "-O1", "-g", "-Wall", "-Wextra", "-Werror",
                            "-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-I", str(ROOT),
                            str(source), "-o", str(binary)], check=True)
            subprocess.run([str(binary)], check=True, timeout=30)

    def test_compile_staging_includes_exact_parser_and_synthetic_mac(self):
        spec = importlib.util.spec_from_file_location("compile_adapter", ROOT / "scripts/compile-esphome.py")
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        with tempfile.TemporaryDirectory() as temporary:
            stage = Path(temporary)
            adapter.stage_configs(ROOT, stage, [CONFIG])
            relative = "patterns/ble-temp-sensor/inkbird_th1_parser.h"
            self.assertEqual((stage / relative).read_bytes(), (ROOT / relative).read_bytes())
            secrets = yaml.safe_load((stage / "patterns/ble-temp-sensor/secrets.yaml").read_text())
            self.assertEqual(secrets["inkbird_th1_mac"], "AA:BB:CC:DD:EE:FF")

    def test_all_eight_firmware_compile_checks_remain_required(self):
        policy = json.loads((ROOT / ".release-policy.json").read_text())
        jobs = mapping(mapping(yaml.compose((ROOT / ".github/workflows/ci.yml").read_text()))["jobs"])
        matrix = mapping(mapping(mapping(jobs["compile"])["strategy"])["matrix"])
        self.assertEqual([item.value for item in matrix["pattern"].value], policy["esphome_configs"])
        self.assertEqual(len(policy["esphome_configs"]), 8)
        needs = mapping(jobs["summary"])["needs"]
        self.assertIn("native-parser", [item.value for item in needs.value])


if __name__ == "__main__":
    unittest.main()
