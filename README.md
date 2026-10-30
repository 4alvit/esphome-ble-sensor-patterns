# ESPHome BLE Sensor Patterns

[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/15470/badge)](https://www.bestpractices.dev/en/projects/15470)

[![Fuzzing: RC only](https://img.shields.io/badge/Fuzzing-RC%20only-blue)](docs/inkbird-contract.md)

Source beta/RC releases include the reviewed examples and production Inkbird
parser. RC qualification covers synthetic host mutation only; each report is
bound to its release tag and source SHA. See [source releases](docs/source-releases.md)
and the [narrow Inkbird decoding contract](docs/inkbird-contract.md).

Reference configurations for ESP32 BLE telemetry using JBD/Daly battery monitors,
Xiaomi temperature and plant sensors, and an Inkbird example. These are starting
points for hardware validation, not battery protection or control firmware.

[![CI](https://github.com/4alvit/esphome-ble-sensor-patterns/actions/workflows/quality-gate.yml/badge.svg)](https://github.com/4alvit/esphome-ble-sensor-patterns/actions/workflows/quality-gate.yml)
[![ESPHome](https://img.shields.io/badge/ESPHome-2026.10.0b1-blue)](https://esphome.io)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)

## Install from your browser

Build your chosen example in **ESPHome Device Builder** on Home Assistant or
another server, then use **[ESPHome Web](https://web.esphome.io/)** to flash its
factory image over USB. No Python or PlatformIO installation is required on the
browser computer. Follow the [browser installation guide](docs/browser-installation.md).
Each example still needs your own sensor address and private credentials;
source beta/RC archives and synthetic CI builds are not ready-to-flash images.

## Examples

- [JBD BMS](patterns/jbd-bms/): one or three battery monitors using the
  commit-pinned `syssi/esphome-jbd-bms` component.
- [Daly BMS](patterns/daly-bms/): one or three monitors using the commit-pinned
  `syssi/esphome-daly-bms` component.
- [Temperature and humidity](patterns/ble-temp-sensor/): built-in Xiaomi
  LYWSD03MMC support, an Inkbird advertisement example and a generic skeleton.
- [Mi Flora](patterns/xiaomi-mi-flora/): built-in ESPHome `xiaomi_hhccjcy01` support.
- [Common fragments](patterns/common/) and [BLE/UART/CAN comparison](comparison/ble-vs-uart-vs-can.md).

JBD/Daly extensions are third-party components. Xiaomi components are supplied by
ESPHome. Some examples contain C++ lambdas; the generic skeleton deliberately
returns unavailable values until a device-specific parser is implemented.

## Advanced: local configuration and builds

The compile-only CI toolchain is ESPHome 2026.10.0b1, an upstream prerelease.
It supplies a compatible PlatformIO release with fixed Starlette dependencies.
The supported compiler host is Linux with CPython 3.12; use a Linux environment
on macOS or Windows.
Validate compatibility on your intended hardware before using its output.
Install the pinned toolchain in an isolated Linux CPython 3.12 environment. Copy an example
and its secrets template into a private working directory, then configure the
Wi-Fi/MQTT credentials, device MAC addresses and a unique native API key:

```bash
python3 -m venv .venv
. .venv/bin/activate
python scripts/install-esphome.py
mkdir -p local-device
cp patterns/jbd-bms/single-bms.yaml local-device/device.yaml
cp patterns/jbd-bms/secrets.example.yaml local-device/secrets.yaml
openssl rand -base64 32
# Put the generated value in api_encryption_key in private secrets.yaml.
# Set networking credentials and replace the BMS MAC in device.yaml.
esphome config local-device/device.yaml
esphome compile local-device/device.yaml
```

Compilation does not install firmware. Use a trusted local serial connection for
installation and physical testing. Never commit a real secrets file or distribute
firmware containing device credentials. Treat compiled images as private.

## Interfaces and security

Each YAML declares its MQTT topic prefix, telemetry entities, BLE addressing and
polling/scan intervals. These can be changed for your installation. Configure the
API client with the same unique `api_encryption_key`; the empty example key
intentionally prevents an unconfigured real-device build. CI substitutes a public
dummy key only in an isolated temporary directory and never flashes its output.

Optional network OTA and HTTP management are disabled by default. Use serial
updates, or separately configure and validate encrypted OTA as described in
[SECURITY.md](SECURITY.md). MQTT is intended for an isolated trusted LAN unless
certificate-verified ESP-IDF MQTT TLS
is configured. BLE advertisements are not a trusted authorization channel.

## Validation and releases

The required CI matrix compiles all eight complete examples on ESPHome 2026.10.0b1:
JBD and Daly single/multi BMS, Inkbird, Xiaomi LYWSD03MMC, Mi Flora and the generic
skeleton. Syntax, management-default regression tests, Ruff/Bandit and CodeQL
checks run as well. Compilation cannot prove packet interpretation, radio range,
sensor calibration or safe battery behavior. Test every pattern on the intended
physical sensor before relying on its values.

See [CONTRIBUTING.md](CONTRIBUTING.md) for exact local checks, review and bug-report
instructions, [CHANGELOG.md](CHANGELOG.md) for compatibility/security changes,
and [release workflow](docs/release-workflow.md) for the source beta/RC policy.
The [OpenSSF evidence index](docs/openssf-evidence.md) records assessment scope;
a prepared assessment is not an awarded badge.

See [dependency lock maintenance](docs/DEPENDENCY_LOCKS.md) for the compiler
selection, lock regeneration and validation scope.

## Project participation and maintenance

See [Contributing](CONTRIBUTING.md), [Governance](GOVERNANCE.md), the [Code of Conduct](CODE_OF_CONDUCT.md), [Security policy](SECURITY.md), and the [roadmap](ROADMAP.md). The [OpenSSF evidence index](docs/openssf-evidence.md) records source and validation scope; only the public badge record establishes an awarded level.
