# BLE temperature and humidity examples

- `xiaomi-lywsd03mmc.yaml` uses ESPHome's built-in `xiaomi_lywsd03mmc`
  component for stock-firmware encrypted advertisements. Set the sensor MAC and
  actual device bindkey in private `secrets.yaml`. It provides temperature,
  humidity and battery level; no unsupported battery-voltage entity is declared.
- `inkbird-ibs-th1.yaml` is a protocol-specific advertisement example. Validate
  packet format against the physical sensor revision before relying on values.
- `generic-ble-temp.yaml` is a compilable starting point. It reports unavailable
  values until a real parser is implemented, rather than inventing measurements.

All examples require a unique native API encryption key. The pinned compiler and
safe management defaults are documented in [README.md](../../README.md) and
[SECURITY.md](../../SECURITY.md). MQTT is intended for an isolated trusted LAN
unless ESP-IDF TLS is explicitly configured and validated.

For Xiaomi bindkey acquisition and firmware compatibility, follow the
[upstream sensor guide](https://esphome.io/components/sensor/xiaomi_ble/).
Never place a real bindkey in a pull request or paste it into public logs.
Changing sensor firmware or activating it with a third-party tool can change its
key and app compatibility; it is not necessary for testing repository code.

The [BLE tracker guide](https://esphome.io/components/esp32_ble_tracker/)
explains passive/active scanning. Scan duty cycle, advertising interval and radio
conditions affect observed values. Encryption does not imply an active BLE
connection is required: the Xiaomi example decrypts passive advertisements.
