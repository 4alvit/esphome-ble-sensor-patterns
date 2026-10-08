# Security policy

## Reporting a vulnerability

Use [GitHub private vulnerability reporting](https://github.com/4alvit/esphome-ble-sensor-patterns/security/advisories/new) to send a confidential report to maintainers. Include the affected version/commit, impact, reproduction and possible mitigations. Remove production credentials and personal data from attachments. Do not publish exploitation details in a public issue before coordinating disclosure.

## Support and response

Security fixes target the current default branch and the latest maintained release, where releases exist. Older versions are not promised backports. Maintainers aim to acknowledge private reports within 14 days, investigate and communicate status within 60 days, and coordinate disclosure with the reporter. Confirmed vulnerabilities with a practical fix receive priority over feature work; publish an advisory and release notes that identify affected versions, mitigation and the fixed version. If a fix takes longer, keep the reporter informed without exposing confidential details.

## Deployment trust boundaries

Treat BLE advertisements as untrusted, unauthenticated input unless a particular sensor protocol proves otherwise. Validate packet lengths before accessing bytes and preserve bounds checks in embedded lambdas. Keep Wi-Fi, MQTT and sensor bind keys in ignored local `secrets.yaml` files. Test new decoders against malformed and truncated packets and real device captures with identifying information removed. Builds must not flash hardware automatically.

Use synthetic data for testing. Never attach live tokens, private keys, database exports or household telemetry to public CI artifacts. Report a suspected credential exposure privately and revoke the credential through its issuer. See [CONTRIBUTING.md](CONTRIBUTING.md) for validation and [the evidence index](docs/openssf-evidence.md) for assessment limits.
