# Common Templates

Shared ESPHome configuration templates for BLE sensor patterns.

## Files

| File | Purpose |
|------|---------|
| `esp32-ble-config.yaml` | ESP32 BLE tuning for 8+ connections |
| `ble-client-template.yaml` | Template for event-driven BLE client |
| `mqtt-template.yaml` | Standard MQTT configuration |
| `secrets.example.yaml` | Required secrets template |

## Usage

Include in your pattern config:

```yaml
# ESP32 BLE tuning
<<: !include ../common/esp32-ble-config.yaml

# MQTT config
<<: !include ../common/mqtt-template.yaml

# BLE client per BMS
<<: !include ../common/ble-client-template.yaml
  variables:
    bms_mac: "AA:BB:CC:DD:EE:FF"
    bms_id: "bms1"
```

## esp32-ble-config.yaml

Sets `CONFIG_BT_ACL_CONNECTIONS=9` and enables SPIRAM allocation for BLE.

## ble-client-template.yaml

Event-driven connect → read → disconnect pattern to stay within ESP32 BLE limits.

## mqtt-template.yaml

Standard MQTT with retain, availability, and device info for Home Assistant.