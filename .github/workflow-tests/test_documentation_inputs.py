"""Keep source inventory and pattern documentation checks on every CI path."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts import patterns_source


class DocumentationInputsTests(unittest.TestCase):
    def test_source_inventory_is_present(self):
        patterns_source.inventory(ROOT)

    def test_pattern_structure_and_required_comparison_are_present(self):
        for directory in (ROOT / "patterns").glob("*/"):
            with self.subTest(pattern=directory.name):
                self.assertTrue((directory / "README.md").is_file())
                self.assertTrue((directory / "secrets.example.yaml").is_file())
                self.assertTrue(list(directory.glob("*.yaml")))
        for name in (
            "patterns/common/esp32-ble-config.yaml",
            "patterns/common/ble-client-template.yaml",
            "patterns/common/mqtt-template.yaml",
            "comparison/ble-vs-uart-vs-can.md",
        ):
            with self.subTest(path=name):
                self.assertTrue((ROOT / name).is_file())


if __name__ == "__main__":
    unittest.main()
