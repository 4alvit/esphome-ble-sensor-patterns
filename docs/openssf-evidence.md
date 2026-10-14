# OpenSSF Best Practices evidence

This index describes this repository's code and engineering practices. It is not a third-party audit or a claim of an awarded badge. The public OpenSSF record is authoritative. The [governance](../GOVERNANCE.md), [conduct policy](../CODE_OF_CONDUCT.md) and [roadmap](../ROADMAP.md) explain participation and current continuity limitations.

## Project and interfaces

The [README](../README.md) and each `patterns/*/README.md` document reusable ESPHome BLE configurations, setup, sensor compatibility and configuration interfaces. The source includes the owned Inkbird decoder, YAML lambdas and Python build/release helpers. The project is MIT licensed; pinned ESPHome and other dependencies retain their own licenses. [CONTRIBUTING.md](../CONTRIBUTING.md) describes changes, tests and required checks. [SECURITY.md](../SECURITY.md) describes private reporting, response, reporter credit and the plaintext BLE/MQTT boundaries.

## Verified baseline and test scope

At source `f972ed79fe9ad60d72cabc4b36fe47263f4d5734`, [RC run 38504846632](https://github.com/4alvit/esphome-ble-sensor-patterns/actions/runs/38504846632) passed all eight ESPHome 2026.10.0b1 compile configurations, Python/Actions CodeQL, the source-contract suite, security checks and release-tool tests. Compiler success does not establish radio performance, all sensor revisions, or safe operation of connected equipment.

`tests/test_inkbird_native.py` compiles the actual production parser and extracted YAML lambda with AddressSanitizer, UndefinedBehaviorSanitizer and active C++ assertions. It checks malformed/truncated inputs, supported marker values, numeric boundaries and publication behavior using host-side doubles. This covers the Inkbird code path; it is not sanitizer coverage of every ESPHome dependency or all JBD/Daly lambdas.

The same [v0.1.1-rc.1 release](https://github.com/4alvit/esphome-ble-sensor-patterns/releases/tag/v0.1.1-rc.1) contains `fuzz-report.json`: the `inkbird-internal` libFuzzer target completed its 60-second isolated campaign at that exact source. This is additional dynamic analysis, not exhaustive input coverage. Repeat the documented fuzz and native tests when changing those paths.

The required Ruff/Bandit checks reject scanner errors and findings; CodeQL analyzes the Python and Actions source. C++ compiler warnings and the native harness provide separate evidence. Full warning strictness and complete-project statement coverage have not been established. Do not report old test totals or thresholds as current coverage measurements.

## Delivery and history

[RELEASING.md](../RELEASING.md), [source-release guidance](source-releases.md), and [CHANGELOG.md](../CHANGELOG.md) describe unique versions, source inventory, acceptance and upgrade/security notes. GitHub HTTPS provides authenticated source and release transport. The current release inventory has checksums and provenance records; checksums alone are not a cryptographic publisher signature.

On 2026-10-14, GitHub private vulnerability reporting was enabled. The inspected repository had no ordinary GitHub issues or published security advisories; the primary maintainer also confirmed no outside bug, enhancement or vulnerability reports in the preceding 12 months. The maintainer personally confirmed knowledge of secure design and common implementation vulnerabilities. These are dated facts, not promises about future response history.

## Remaining Silver work

There is no backup maintainer or tested one-week access-recovery mechanism. Complete-source coverage, a six-month defect/regression ledger, complete release-signature evidence, a structured whole-project security assurance case and maximally strict warnings remain unverified or incomplete. Keep those criteria unmet until actual evidence exists. Do not infer full-project or physical-device assurance from a passing hosted gate.
