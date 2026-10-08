# Security policy

## Reporting a vulnerability

Use [GitHub private vulnerability reporting](https://github.com/4alvit/esphome-ble-sensor-patterns/security/advisories/new) to send a confidential report to maintainers. Include the affected version/commit, impact, reproduction and possible mitigations. Remove production credentials and personal data from attachments. Do not publish exploitation details in a public issue before coordinating disclosure.

## Support and response

Security fixes target the current default branch and the latest maintained release, where releases exist. Older versions are not promised backports. Maintainers aim to acknowledge private reports within 14 days, investigate and communicate status within 60 days, and coordinate disclosure with the reporter. Confirmed vulnerabilities with a practical fix receive priority over feature work; publish an advisory and release notes that identify affected versions, mitigation and the fixed version. If a fix takes longer, keep the reporter informed without exposing confidential details.

## Deployment trust boundaries

Treat BLE advertisements as untrusted, unauthenticated input unless a particular sensor protocol proves otherwise. Validate packet lengths before accessing bytes and preserve bounds checks in embedded lambdas. Keep Wi-Fi, MQTT and sensor bind keys in ignored local `secrets.yaml` files. Test new decoders against malformed and truncated packets and real device captures with identifying information removed. Builds must not flash hardware automatically.

Use synthetic data for testing. Never attach live tokens, private keys, database exports or household telemetry to public CI artifacts. Report a suspected credential exposure privately and revoke the credential through its issuer. See [CONTRIBUTING.md](CONTRIBUTING.md) for validation and [the evidence index](docs/openssf-evidence.md) for assessment limits.


## Firmware management and cryptography

Every complete example requires its own `api_encryption_key` in private
`secrets.yaml`. Generate 32 random bytes with `openssl rand -base64 32`; do not
reuse the public synthetic CI key, a sample bindkey or another device's key.
ESPHome's native API implements Noise authenticated encryption using its FLOSS
cryptographic library; this repository does not implement a cipher. See the
[upstream API protocol](https://developers.esphome.io/architecture/api/protocol_details/).

Network OTA and the optional HTTP management server are omitted by default.
Use a trusted local serial connection for updates. The compile-only CI compiler
is an upstream prerelease; its use does not establish safe physical-device
operation. If you separately enable encrypted OTA, follow the [encrypted OTA guide](https://esphome.io/components/ota/esphome/)
and its migration steps. Do not expose an unauthenticated OTA or web endpoint.
No command in this repository's CI flashes a device.

The examples publish MQTT on a trusted isolated network. MQTT credentials and
sensor values are plaintext unless you configure ESP-IDF MQTT TLS with a trusted
`certificate_authority`, port 8883 and `skip_cert_cn_check: false` as documented
[upstream](https://esphome.io/components/mqtt/). BLE broadcast telemetry likewise
is not an authenticated control channel. Do not use these examples over an
untrusted network or as a battery protection mechanism. A sensor bindkey is a
protocol key, not a password verifier; no user-password database is maintained.
