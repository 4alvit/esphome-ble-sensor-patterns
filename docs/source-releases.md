# Source releases and RC qualification

The release product is `esphome-ble-sensor-patterns-VERSION.tar.gz`: the explicit
`source-files.json` inventory of reusable configurations, the production Inkbird
header, synthetic tests, dependency locks and build/release instructions. The
archive is not firmware. `SOURCE_VERSION` versions this source collection;
ESPHome and external-component revisions retain their independent pinned versions.
Real `secrets.yaml`, local build directories and operator state are excluded.

Normal pull requests retain all eight ESPHome 2026.10.0b1 compile checks, existing
security and workflow checks, and add required native parser/source contracts.
These use Linux CPython 3.12 for ESPHome and Clang 18 for host native tests. Firmware
compilation can download locked dependencies and upstream native toolchains;
fully offline repetition requires preparing those toolchains and caches first.
See [dependency locks](DEPENDENCY_LOCKS.md). Compile success is not hardware
acceptance. The compile adapter only invokes `config` and `compile`, never upload.

## Local host validation

With Python 3.12, Clang with ASan/UBSan, Git and the locked PyYAML prerequisite:

```sh
python3 -m pip install --require-hashes --only-binary=:all: -r .github/requirements-workflow-contracts.txt
CXX=clang++-18 python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/patterns_source.py build 0.1.1 rc release-dist
CXX=clang++-18 python3 scripts/patterns_source.py verify release-dist/esphome-ble-sensor-patterns-*.tar.gz
```

Use the installed `clang++` name on hosts that do not suffix compiler versions.
After prerequisites are installed, these tests and source archive acceptance run
offline using only synthetic data. The verifier compares every member's name,
regular-file type, exact bytes, normalized metadata and executable mode against
the reviewed inventory before extracting. It runs all repository tests from the
extracted source. The package command requires inventoried inputs to be tracked.
A local base-version build is a smoke test, not a qualified candidate.

## Candidate lifecycle

The shared release workflow is pinned to an immutable merged toolkit commit.
A default-branch push can publish beta after every required check and archive
acceptance pass. RC is an explicit `release-pipeline.yml` dispatch with channel
`rc`. It additionally requires a successful real mutation campaign and records
positive libFuzzer execution counts. Routine PR, push and nightly runs do not run
mutation campaigns. The README badge describes that schedule, not a passing
status for the current branch. Each report belongs to its exact source SHA/tag.

The workflow freezes a version plan before building. The build synchronizes
`SOURCE_VERSION`, verifies the package, stages checksums and creates the input
receipt binding the exact source overlay and asset bytes. Beta embeds its full
beta version; the `promote-bytes` RC profile embeds the numeric base and retains
its RC identity in the plan/manifest. The release includes archive, SHA256SUMS,
version receipt, manifest and immutable source-bound evidence; an RC additionally
includes its fuzz report. Nothing is published to a package registry.

To reproduce a published beta, restore its saved `version_plan` as
`.release-plan.json` in a disposable checkout of the exact source, then run:

```sh
python3 scripts/version_plan.py sync --root . --plan .release-plan.json
python3 scripts/release.py package 0.1.1 beta
```

See [VERSIONING.md](VERSIONING.md) and the generated release runbook for the full
receipt contract. Stable publication remains a separate protected operation and
is not part of this rollout. No release authorizes hardware installation,
Bluetooth traffic, MQTT communication, flashing or deployment.
