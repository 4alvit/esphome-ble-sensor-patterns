"""Run the real repository validator against immutable-reference regressions."""

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "pin_contracts", ROOT / "scripts/workflow_contracts.py"
)
contracts = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(contracts)


class ImmutableActionsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        shutil.copytree(ROOT / ".github/workflows", self.root / ".github/workflows")
        shutil.copyfile(
            ROOT / ".release-policy.json", self.root / ".release-policy.json"
        )

    def change_reference(self, reference, *, reusable=False):
        workflow_name = "ci.yml"
        path = self.root / ".github/workflows" / workflow_name
        # BaseLoader constructs only strings, lists and dictionaries.
        source = ROOT / ".github/workflows" / workflow_name
        workflow = yaml.load(source.read_text(), Loader=yaml.BaseLoader)  # nosec B506
        if reusable:
            workflow["jobs"]["external_probe"] = {"uses": reference}
        else:
            job = next(job for job in workflow["jobs"].values() if "steps" in job)
            step = next(step for step in job["steps"] if "uses" in step)
            step["uses"] = reference
        path.write_text(yaml.safe_dump(workflow))

    def test_actual_workflows_pass_without_optional_pin_manifest(self):
        self.assertFalse((self.root / ".github/action-pins.json").exists())
        contracts.validate(self.root)

    def test_mutable_step_action_is_rejected(self):
        self.change_reference("actions/checkout@main")
        with self.assertRaisesRegex(ValueError, "immutable SHA"):
            contracts.validate(self.root)

    def test_mutable_reusable_workflow_is_rejected(self):
        self.change_reference("owner/repo/.github/workflows/ci.yml@v1", reusable=True)
        with self.assertRaisesRegex(ValueError, "immutable SHA"):
            contracts.validate(self.root)

    def test_docker_action_requires_content_digest(self):
        self.change_reference("docker://alpine:latest")
        with self.assertRaisesRegex(ValueError, "immutable SHA"):
            contracts.validate(self.root)
        self.change_reference("docker://alpine@sha256:" + "a" * 64)
        contracts.validate(self.root)

    def test_malformed_action_is_rejected(self):
        self.change_reference(42)
        with self.assertRaisesRegex(ValueError, "immutable SHA"):
            contracts.validate(self.root)

    def test_local_action_remains_permitted(self):
        self.change_reference("./.github/actions/local")
        contracts.validate(self.root)
