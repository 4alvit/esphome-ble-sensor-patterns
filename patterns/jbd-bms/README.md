# JBD BMS BLE Pattern

JBD (Jiabaida) BMS with BLE interface. Uses `syssi/esphome-jbd-bms` external component.

## Hardware
- JBD BMS (SP04S, SP08S, SP14S, SP16S, SP20S, SP24S variants)
- ESP32 with Bluetooth (ESP32, ESP32-S3, ESP32-C3)
- BLE service UUID: `0xFF00`

## Supported Sensors
- Total voltage, current, power
- State of Charge (SOC)
- Remaining capacity
- Charge cycles
- Cell voltages (up to 24 cells)
- Temperatures (MOS, battery, internal)
- FET status (charging/discharging)
- Protection flags (over/under voltage, over current, temperature)

## Configuration Files
- `single-bms.yaml` - One BMS, simple polling
- `multi-bms.yaml` - Multiple BMS with event-driven connect/disconnect (prevents BLE connection limits)

## Usage
1. Copy `single-bms.yaml` or `multi-bms.yaml` to your project
2. Update MAC address(es) in `ble_client` section
3. Add secrets to `secrets.yaml` (WiFi, MQTT)
4. Flash with ESPHome

## External Component
```yaml
external_components:
  - source: github://syssi/esphome-jbd-bms@main
    refresh: 1d
    components: [jbd_bms_ble]
```

## ESP32 BLE Tuning (multi-BMS)
```yaml
esp32:
  framework:
    type: esp-idf
    sdkconfig_options:
      CONFIG_BT_ACL_CONNECTIONS: "9"
      CONFIG_BT_GATTC_CONNECT_RETRY_COUNT: "3"
      CONFIG_BT_ALLOCATION_FROM_SPIRAM_FIRST: "y"
      CONFIG_BT_BLE_DYNAMIC_ENV_MEMORY: "y"
      CONFIG_ESP32_REV_MIN_3: "y"
```

## References
- Component: https://github.com/syssi/esphome-jbd-bms
- Protocol: JBD BLE protocol (0xFF00 service)