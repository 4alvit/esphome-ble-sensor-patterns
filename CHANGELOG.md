# Changelog

## [0.1.2] - Development line

### Changed

- Qualify this release with the bounded, offline RC fuzz campaign and deterministic seed replay checks.
- Bind release evidence to the exact source and toolkit revision, validate seed corpora, and retain engine execution counts and diagnostic artifacts.
- Document the fuzzing scope, resource limits, and the distinction between synthetic checks and target acceptance.

### Upgrade

Use the existing installation or update procedure. This release changes validation
and release tooling; existing user configuration and data formats are preserved.
Keep the previous immutable release for rollback. Test the exact RC package on the
intended target before accepting a stable promotion.

### Security

The campaign operates offline on synthetic inputs. It rejects missing or invalid
seed corpora and incomplete execution evidence. These checks do not establish
untested hardware, integrations, credentials, or deployment behavior.

## [0.1.1]

### Added

Versioned source archives with explicit membership, extracted-source acceptance,
ASan/UBSan regression tests and RC-only mutation fuzzing of the production Inkbird
parser. Eight pinned ESPHome compile checks remain required.

### Fixed

Replace the unsupported fixed-0x038A/0x2D Inkbird layout with the narrow internal
TH1/TH1 Mini compatibility profile documented from pinned upstream decoders.
Select one configured sensor MAC; reject external-probe frames and unsupported
metadata. Humidity is decoded in hundredths of a percent, not whole percent.


### Security

Reject malformed/truncated input and impossible humidity/battery percentages
before publishing any reading. Sensor selection is not authentication. Source
packages contain only reviewed files, never private credentials or firmware.

Hash-lock Python dependencies and build tools used by firmware CI and YAML
validation. Replace the vulnerable 2025.11.0 compiler dependency set with the
official ESPHome 2026.10.0b1 prerelease and its supported PlatformIO 6.2.0 range.

### Upgrade

Copy `inkbird_th1_parser.h` beside the Inkbird YAML and configure the new private
`inkbird_th1_mac` secret. This example intentionally supports only internal-sensor
frames in the documented profile. Earlier TH2/TH3 claims were not substantiated;
other revisions and external probes require separate validation. No hardware or
radio validation was performed for this source release.

The compile-only CI compiler is a prerelease and now requires Linux with
CPython 3.12. The installer fails before pip on unsupported hosts. The upstream
Intel-macOS dependency branch still contains a vulnerable cryptography pin
and is not supported. Recreate the Linux CPython 3.12 environment
using the documented locks and repeat hardware validation before installing
firmware. No device is flashed by CI. Synthetic CI Noise keys are nonzero because
the new compiler rejects the previously used all-zero fixture; real examples
still require separately generated private per-device keys.

## [0.1.0]

### Fixed

Use ESPHome's built-in Xiaomi HHCCJCY01 and LYWSD03MMC components instead of
unavailable external repositories and unsupported configuration keys. Remove
the speculative Mi Flora frame decoder; it checked for 13 bytes but accessed
byte 14. Pin JBD and Daly external components to explicit source commits.
Correct Daly sensor names and the generic template configuration.

### Security

Require unique per-device Noise API keys in every complete example. Disable
unauthenticated network OTA and HTTP management by default. CI uses public
synthetic credentials only in temporary compile directories and never flashes
hardware. Add required Ruff/Bandit analysis and regression contracts.

### Upgrade

Generate `api_encryption_key` with `openssl rand -base64 32` and keep it in a
private `secrets.yaml`. Set Xiaomi sensor MACs and actual bindkeys there too.
The API client must use the matching key. Use trusted serial updates with the
pinned ESPHome 2025.11.0 compiler; see SECURITY.md for encrypted-OTA requirements
when separately upgrading ESPHome. Removed unsupported Xiaomi battery-voltage,
firmware-version and Daly individual protection entities must not be relied on
by dashboards or automations. Preserve the names of supported measurements.
MQTT remains intended for an isolated trusted LAN unless TLS is configured.
The source release does not certify real-device radio or battery behavior.
