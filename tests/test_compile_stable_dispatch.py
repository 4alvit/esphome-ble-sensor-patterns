"""Exercise the exact inline relay without HTTP, credentials, or a live dispatch."""
import contextlib
import io
from pathlib import Path
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / '.github/workflows/release.yml'
if not WORKFLOW.exists():  # The standalone review artifact uses the same file bytes.
    WORKFLOW = Path(__file__).with_name('after.yml')
YAML = WORKFLOW.read_text()
SOURCE = textwrap.dedent(YAML.split("          python3 - <<'PY_RELAY'\n", 1)[1].rsplit('          PY_RELAY\n', 1)[0])
NAMESPACE = {'__name__': 'reviewed_stable_relay'}
exec(compile(SOURCE, str(WORKFLOW), 'exec'), NAMESPACE)
SHA = 'a' * 40


class StableDispatchTests(unittest.TestCase):
    def setUp(self):
        self.env = dict(GITHUB_EVENT_NAME='workflow_dispatch',
                        GITHUB_REPOSITORY='4alvit/esphome-ble-sensor-patterns',
                        GITHUB_ACTOR='4alvit', GITHUB_TRIGGERING_ACTOR='4alvit',
                        GITHUB_RUN_ATTEMPT='1', RC_TAG='v0.1.1-rc.2', EXPECTED_SHA=SHA,
                        GITHUB_REF='refs/heads/main', GITHUB_SHA=SHA)
        self.calls = []
        self.override = {}

    def api(self, path, payload=None, missing=False):
        self.calls.append((path, payload))
        if path in self.override:
            value = self.override[path]
            if isinstance(value, Exception):
                raise value
            return value
        if payload is not None:
            return {'workflow_run_id': 123, 'html_url':
                    'https://github.com/4alvit/esphome-ble-sensor-patterns/actions/runs/123'}
        if path == 'user':
            return {'login': 'californiantiramisu'}
        if path == 'repos/4alvit/esphome-ble-sensor-patterns':
            return {'default_branch': 'main', 'private': False, 'archived': False}
        if path.endswith('/git/ref/heads/main'):
            return {'object': {'sha': SHA}}
        if path.endswith('/releases/tags/v0.1.1-rc.2'):
            return {'tag_name': 'v0.1.1-rc.2', 'prerelease': True, 'draft': False}
        if missing:
            return None
        if path.endswith('/environments/release'):
            return {'protection_rules': [{'type': 'required_reviewers',
                    'prevent_self_review': True, 'reviewers': [
                        {'type': 'User', 'reviewer': {'login': '4alvit'}}]}]}
        if '/runs?per_page=1&status=' in path:
            return {'total_count': 0}
        raise AssertionError(path)

    def invoke(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return NAMESPACE['dispatch'](self.api, self.env, io.StringIO())

    def test_exact_single_bot_dispatch(self):
        self.invoke()
        writes = [(p, x) for p, x in self.calls if x is not None]
        self.assertEqual(writes, [('repos/4alvit/esphome-ble-sensor-patterns/actions/workflows/release-pipeline.yml/dispatches',
                         {'ref': 'main', 'inputs': {'channel': 'stable', 'rc_tag': 'v0.1.1-rc.2', 'expected_sha': SHA}})])
        self.assertNotIn('actions/checkout', YAML)
        self.assertIn('permissions: {}', YAML)

    def test_rejects_untrusted_context_and_input_before_write(self):
        cases = {'GITHUB_ACTOR': 'someone', 'GITHUB_TRIGGERING_ACTOR': 'someone',
                 'GITHUB_EVENT_NAME': 'pull_request', 'GITHUB_REPOSITORY': 'fork/repo',
                 'GITHUB_RUN_ATTEMPT': '2', 'GITHUB_REF': 'refs/heads/other',
                 'GITHUB_SHA': 'b' * 40, 'EXPECTED_SHA': 'main',
                 'RC_TAG': 'v0.1.1-rc.2\nmalicious'}
        for key, value in cases.items():
            with self.subTest(key=key):
                original = self.env[key]
                self.env[key] = value
                self.calls.clear()
                with self.assertRaises(RuntimeError):
                    self.invoke()
                self.assertFalse(any(p is not None for _, p in self.calls))
                self.env[key] = original

    def test_rejects_wrong_bot(self):
        self.override['user'] = {'login': '4alvit'}
        with self.assertRaisesRegex(RuntimeError, 'separate bot'):
            self.invoke()
        self.assertFalse(any(p is not None for _, p in self.calls))

    def test_rejects_weakened_environment(self):
        self.override['repos/4alvit/esphome-ble-sensor-patterns/environments/release'] = {
            'protection_rules': [{'type': 'required_reviewers', 'prevent_self_review': False,
                                 'reviewers': [{'type': 'User', 'reviewer': {'login': '4alvit'}}]}]}
        with self.assertRaisesRegex(RuntimeError, 'prevent self-review'):
            self.invoke()
        self.assertFalse(any(p is not None for _, p in self.calls))

    def test_rejects_active_pipeline_and_existing_stable(self):
        for path, value in [
            ('repos/4alvit/esphome-ble-sensor-patterns/actions/workflows/release-pipeline.yml/runs?per_page=1&status=waiting', {'total_count': 1}),
            ('repos/4alvit/esphome-ble-sensor-patterns/releases/tags/v0.1.1', {'id': 1}),
            ('repos/4alvit/esphome-ble-sensor-patterns/git/ref/tags/v0.1.1', {'object': {'sha': SHA}}),
        ]:
            with self.subTest(path=path):
                self.override = {path: value}
                self.calls.clear()
                with self.assertRaises(RuntimeError):
                    self.invoke()
                self.assertFalse(any(p is not None for _, p in self.calls))

    def test_rechecks_head_before_write(self):
        original = self.api
        count = 0
        def moved(path, payload=None, missing=False):
            nonlocal count
            value = original(path, payload, missing)
            if path.endswith('/git/ref/heads/main'):
                count += 1
                if count == 2:
                    return {'object': {'sha': 'b' * 40}}
            return value
        self.api = moved
        with self.assertRaisesRegex(RuntimeError, 'moved during preflight'):
            self.invoke()
        self.assertFalse(any(p is not None for _, p in self.calls))

    def test_unknown_dispatch_outcome_never_retries(self):
        self.override['repos/4alvit/esphome-ble-sensor-patterns/actions/workflows/release-pipeline.yml/dispatches'] = TimeoutError('unknown')
        with self.assertRaises(TimeoutError):
            self.invoke()
        self.assertEqual(sum(p is not None for _, p in self.calls), 1)


if __name__ == '__main__':
    unittest.main()
