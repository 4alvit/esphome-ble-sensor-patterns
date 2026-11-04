# Daly BMS BLE Pattern

Daly Smart BMS with BLE interface. Uses `syssi/esphome-daly-bms` external component.

## Hardware
- Daly Smart BMS (Li-ion, LFP, LTO variants)
- Daly BMS Bluetooth dongle / built-in BLE
- ESP32 with Bluetooth
- BLE service UUID: `0xFFE0` / `0xFFE1` (Nordic UART style)

## Supported Sensors
- Pack voltage, current, power, SOC
- Individual cell voltages (up to 24 cells)
- Temperatures (4x battery + MOS)
- Charge cycles, remaining capacity
- FET status (charging/discharging)
- Protection flags (OV, UV, OC, OT, UT)
- Balancing status and current

## Configuration Files
- `single-bms.yaml` - One BMS with continuous connection
- `multi-bms.yaml` - Multiple BMS sequential polling

## Usage
1. Copy config to your project
2. Update MAC address in `ble_client` section
3. Add secrets (WiFi, MQTT, MAC address)
4. Flash with ESPHome

## External Component
```yaml
external_components:
  - source: github://syssi/esphome-daly-bms@17ae67d1d917968e5a99a0c419b21b93f7ed9450
    refresh: 1d
    components: [daly_bms_ble]
```

## Multi-BMS Notes
- ESP32 BLE supports ~4-8 concurrent connections
- Use event-driven connect/disconnect for >2 BMS
- Adjust `CONFIG_BT_ACL_CONNECTIONS` in esp32 framework config

## References
- Component: https://github.com/syssi/esphome-daly-bms
- Protocol: Daly BLE protocol (FFE0/FFE1)

The component is pinned at a [compatible upstream revision](https://github.com/syssi/esphome-daly-bms/commit/17ae67d1d917968e5a99a0c419b21b93f7ed9450) with the current formatting API and sensitive configuration-password handling for the repository's ESPHome 2026.11.0b1 compile-only CI. Sensor definitions and control settings are unchanged. CI compilation does not replace testing on your hardware.

Configuration-password redaction does not suppress runtime protocol logs. Upstream still logs a received password at `INFO`; both examples therefore limit the `daly_bms_ble` tag to `WARN`, preserving warnings and errors without changing the global log level. Keep that override and do not enable lower-severity BMS protocol logging when using real credentials.
