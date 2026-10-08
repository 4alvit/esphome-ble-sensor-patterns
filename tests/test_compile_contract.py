"""Offline contracts for firmware CLI selection and filesystem confinement."""

import base64
import importlib.util

import yaml
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "compile_adapter", Path(__file__).parents[1] / "scripts/compile-esphome.py"
)
ADAPTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ADAPTER)


class ConfigSelectionTests(unittest.TestCase):
    """Reject unsafe file selection before any compiler or network access."""

    def test_declared_regular_yaml_is_selected(self):
        """Return declared paths only, with the original order retained."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "firmware.yaml").write_text("esphome: {}\n", encoding="utf-8")
            policy = {"esphome_configs": ["firmware.yaml"]}
            self.assertEqual(
                ADAPTER.selected_configs(root, policy, []), ["firmware.yaml"]
            )
            self.assertEqual(
                ADAPTER.confined_config(root, "firmware.yaml"),
                (root / "firmware.yaml").resolve(),
            )

    def test_traversal_options_absolute_paths_and_wrong_extensions_are_rejected(self):
        """Untrusted CLI or policy entries cannot become compiler arguments."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for value in (
                "../secret.yaml",
                "/tmp/secret.yaml",
                "--help.yaml",
                "a/-x.yaml",
                "a.txt",
                "a\ny.yaml",
            ):
                with (
                    self.subTest(value=value),
                    self.assertRaises((ValueError, OSError)),
                ):
                    ADAPTER.confined_config(root, value)

    def test_symlinks_and_undeclared_configs_are_rejected(self):
        """Keep compiler input inside the reviewed source inventory."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "firmware.yaml").write_text("esphome: {}\n", encoding="utf-8")
            (root / "link.yaml").symlink_to(root / "firmware.yaml")
            with self.assertRaises(ValueError):
                ADAPTER.confined_config(root, "link.yaml")
            with self.assertRaises(ValueError):
                ADAPTER.selected_configs(
                    root, {"esphome_configs": ["firmware.yaml"]}, ["other.yaml"]
                )


class SecureFirmwareDefaultsTests(unittest.TestCase):
    """Check actual examples cannot expose plaintext management by accident."""

    def test_complete_examples_require_a_private_noise_key(self):
        root = Path(__file__).parents[1]
        checked = []
        for path in sorted((root / "patterns").glob("*/*.yaml")):
            document = yaml.compose(path.read_text())
            fields = {key.value: value for key, value in document.value}
            if "esphome" not in fields:
                continue
            checked.append(path)
            with self.subTest(path=path.relative_to(root)):
                api = {key.value: value for key, value in fields["api"].value}
                encryption = {key.value: value for key, value in api["encryption"].value}
                self.assertEqual(encryption["key"].tag, "!secret")
                self.assertEqual(encryption["key"].value, "api_encryption_key")
                self.assertNotIn("ota", fields)
                self.assertNotIn("web_server", fields)
                example = yaml.safe_load((path.parent / "secrets.example.yaml").read_text())
                self.assertEqual(example["api_encryption_key"], "")
        self.assertEqual(len(checked), 8)

    def test_xiaomi_uses_supported_builtin_parsers(self):
        root = Path(__file__).parents[1]
        for relative, platform in (
            ("patterns/xiaomi-mi-flora/mi-flora.yaml", "xiaomi_hhccjcy01"),
            ("patterns/ble-temp-sensor/xiaomi-lywsd03mmc.yaml", "xiaomi_lywsd03mmc"),
        ):
            with self.subTest(path=relative):
                document = yaml.compose((root / relative).read_text())
                fields = {key.value: value for key, value in document.value}
                self.assertNotIn("external_components", fields)
                sensors = [{key.value: value for key, value in sensor.value}
                           for sensor in fields["sensor"].value]
                self.assertEqual(sensors[0]["platform"].value, platform)
                self.assertEqual(sensors[0]["mac_address"].tag, "!secret")
                self.assertNotIn("lambda", (root / relative).read_text())

    def test_ci_stages_only_synthetic_api_credentials(self):
        root = Path(__file__).parents[1]
        policy = {"esphome_configs": ["patterns/jbd-bms/single-bms.yaml"]}
        with tempfile.TemporaryDirectory() as temporary:
            stage = Path(temporary)
            ADAPTER.stage_configs(root, stage, policy["esphome_configs"])
            data = yaml.safe_load((stage / "patterns/jbd-bms/secrets.yaml").read_text())
            self.assertEqual(len(base64.b64decode(data["api_encryption_key"], validate=True)), 32)
            self.assertEqual(data["wifi_ssid"], "ci-validation")
            self.assertEqual(data["mqtt_pass"], "ci-validation-password")


if __name__ == "__main__":
    unittest.main()
