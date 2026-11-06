# Dependency locks

The dependency files used by ESPHome firmware checks pin exact package versions and
SHA-256 distribution hashes. CI installs build tools from
`.github/requirements-build.txt` before installing source distributions or this
project with `--no-build-isolation`. This prevents pip from resolving a separate,
unlocked build environment. Application dependencies remain installed from their
full locks; `--no-deps` is used only for the subsequent local project install.

The first two comment lines in each generated lock record its `uv pip compile`
command. Most commands run from the repository root with uv 0.12.7. The
ESPHome compiler command runs inside `.github` so it reads the Linux resolver
metadata; use the explicit `--directory .github` command below when starting
from the repository root. Review version and hash changes, then repeat the
corresponding CI checks before merging. Hashes establish the selected artifact identity; they do
not establish that a package is free of vulnerabilities. Keep dependency
security scanning and update review enabled.

## Supported compiler environment

The compile-only matrix uses upstream
[ESPHome 2026.11.0b1](https://pypi.org/project/esphome/2026.11.0b1/), a prerelease.
Its constraints permit Pillow 13.0.0 and filelock 4.2.6, resolving the older
compiler's incompatible pins without overrides. The policy, CI matrix and
complete Linux compiler lock select the same ESPHome version; source-contract
tests reject mismatches. This CI choice does not recommend prerelease firmware
for production devices. Prefer a subsequent compatible stable release after the
same checks.

The installer rejects non-Linux hosts, non-CPython interpreters and Python
versions other than 3.12 before pip runs. Direct native installation on macOS and
Windows is unsupported; use a Linux environment. Upstream 2026.11.0b1 has an
unsatisfiable Intel-macOS branch: its cryptography 50.0.2 pin conflicts with
`aioesphomeapi`'s `<49` requirement on that platform. Do not override either
constraint or broaden the supported host policy.

Regenerate the compiler lock from the repository root:

```sh
uv --directory .github pip compile requirements-esphome.in --generate-hashes --universal --python-version=3.12 --output-file=requirements-esphome.txt
```

The dedicated `.github/pyproject.toml` restricts this universal resolution to
Linux. It does not restrict Linux architecture: x86_64, aarch64 and conditional
Python dependency branches remain in scope. The input retains Linux markers.
`--directory .github` is required so uv reads that metadata; a root-level
invocation without it attempts unsupported operating-system branches.
The file configures lock regeneration only, not runtime installation or other
project tooling.

## Validation and update boundaries

A clean hash-checked installation, `pip check` and all eight firmware builds
must pass before changing the compiler pin. Some dependencies have only source
distributions; they build with the preinstalled locked tools. CI compiles all
eight configurations using isolated dummy credentials. Python locks do not pin
ESPHome's separately downloaded native firmware toolchains. Update the input,
generated lock, environment metadata, policy and CI matrix together. The YAML
linter has a separate lock. Audit every package/version selected by the lock,
including conditional marker branches; a host-filtered audit alone is incomplete.

The compiler is a development tool, not bundled into the source-only application
release or automatically installed on a device. Validation does not publish or
flash firmware and does not establish physical sensor compatibility.

Renovate keeps the qualified ESPHome compiler at 2026.11.0b1 while updating
other editable inputs and their generated locks. A compiler upgrade must update
the requirement input, lock, `.release-policy.json` and workflow matrix together
and pass the existing eight-build qualification described above.
