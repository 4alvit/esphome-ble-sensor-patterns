# Changelog

## [Unreleased]

### Security

Hash-lock Python dependencies and build tools used by firmware CI and YAML
validation. Replace the vulnerable 2025.11.0 compiler dependency set with the
official ESPHome 2026.10.0b1 prerelease and its supported PlatformIO 6.2.0 range.

### Upgrade

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
