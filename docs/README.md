# Documentation

Reusable ESPHome patterns for BLE sensors: installing an example from a browser,
the decoding contract for an Inkbird sensor, and the source release process.

## Use a pattern

- [Install a BLE sensor example from your browser](browser-installation.md) — the Device Builder and ESPHome Web path over USB.
- [Inkbird internal-sensor decoding contract](inkbird-contract.md) — how the internal sensor payload is decoded.

## Release operation

- [CI and source release workflow](CI_WORKFLOW.md) — the Quality gate and the validation workflows it retains.
- [CI orchestration](CI-ORCHESTRATION.md) — how the quality gate and release pipeline divide the events.
- [Source releases and RC qualification](source-releases.md) — the release archive and what qualifies it.
- [Version plans and manifest synchronization](VERSIONING.md) — the versioning opt-in.
- [Dependency locks](DEPENDENCY_LOCKS.md) — the exact versions the firmware checks pin.

## Evidence

- [OpenSSF Best Practices evidence](openssf-evidence.md) — the evidence index, explicitly not a third-party audit.
- [Release-candidate fuzz testing](rc-fuzzing.md) — the reusable bounded fuzz workflow.
- [Release read recovery and rerun validation](release-read-safety.md) — the two fixes carried from the shared toolkit.
- [Early final-build runner check](runner-preflight.md) — why the check runs before the final build.
