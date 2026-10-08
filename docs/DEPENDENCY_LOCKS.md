# Dependency locks

The dependency files used by ESPHome firmware checks pin exact package versions and
SHA-256 distribution hashes. CI installs build tools from
`.github/requirements-build.txt` before installing source distributions or this
project with `--no-build-isolation`. This prevents pip from resolving a separate,
unlocked build environment. Application dependencies remain installed from their
full locks; `--no-deps` is used only for the subsequent local project install.

The first two comment lines in each generated lock record its `uv pip compile`
command. Run that command from the repository root with uv 0.12.7 to regenerate
the lock, review version and hash changes, then repeat the corresponding CI
checks before merging. Hashes establish the selected artifact identity; they do
not establish that a package is free of vulnerabilities. Keep dependency
security scanning and update review enabled.

The compile-only matrix uses upstream [ESPHome 2026.10.0b1](https://pypi.org/project/esphome/2026.10.0b1/), a prerelease.
It declares PlatformIO 6.2.0, whose supported dependency range includes the
Starlette security fixes. Stable ESPHome 2026.9.1 pins PlatformIO 6.1.19 and
therefore cannot resolve those fixed Starlette versions without overriding
upstream metadata. This repository does not override that metadata.

The selected compiler is for validation; it does not automatically publish or
flash firmware. A clean installation and all eight firmware builds must pass
before changing this pin. Prefer the next compatible stable release after the
same checks. Its runtime lock includes
platform markers so local macOS validation and Linux CI resolve their own
dependencies without adding unpinned packages. Some dependencies, including
paho-mqtt 1.6.1, have only source distributions; they build with the preinstalled
locked tools. CI compiles all eight declared configurations using isolated dummy
credentials. Python locks do not pin ESPHome's separately downloaded native
firmware toolchains. Update the ESPHome input file, lock filename, policy and CI matrix
together. The YAML linter has a separate lock.
