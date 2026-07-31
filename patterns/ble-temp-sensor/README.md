# Generic BLE Temperature Sensor Pattern

Collection of ESPHome configurations for popular BLE temperature/humidity sensors using passive advertisement scanning.

## Supported Sensors

| Sensor | Model | Encryption | Advertisement Interval |
|--------|-------|------------|------------------------|
| Xiaomi LYWSD03MMC | Mijia BT Thermometer 2 | AES-CCM | ~2 sec |
| Inkbird IBS-TH1/TH2/TH3 | Digital Hygrometer | None | ~1-2 sec |
| Govee H5075 / H5179 | Smart Hygrometer | None/AES | ~1 sec |
| Qingping CGG1 | Temp/Humidity Monitor | None | ~1 sec |
| SensorPush HT1/HT/w | Wireless Sensor | AES | ~1 min |
| SwitchBot Meter | Meter / Meter Plus | None | ~2 sec |

## Implementation Approaches

### 1. Passive Scan (Recommended for unencrypted)
```yaml
esp32_ble_tracker:
  on_bluetooth_le_advertise:
    - lambda: |-
        if (x.get_manufacturer_id() == MANUFACTURER_ID) {
          parse_data(x.get_manufacturer_data());
        }
```

### 2. Active Connection (For encrypted sensors)
```yaml
ble_client:
  - mac_address: "XX:XX:XX:XX:XX:XX"
    id: sensor_client
    auto_connect: true

# Use component with encryption support (xiaomi_ble, SensorPush, etc.)
```

### 3. Generic Template (Roll Your Own)
See `generic-ble-temp.yaml` for template with placeholder parser.

## Key Configuration Files

| File | Description |
|------|-------------|
| `xiaomi-lywsd03mmc.yaml` | Xiaomi LYWSD03MMC (encrypted, needs bindkey) |
| `inkbird-ibs-th1.yaml` | Inkbird IBS-TH1/TH2/TH3 (unencrypted) |
| `generic-ble-temp.yaml` | Template for custom sensors |

## Getting Bindkeys (Encrypted Sensors)

### Xiaomi LYWSD03MMC
1. **Mi Home App**: Device settings → Firmware → Hold "Check Update" → Version copied to clipboard
2. **Telnet**: `telnet <ip>` in Mi Home → `cat /data/miio/device_info.json`
3. **ESPHome**: Use `xiaomi_ble` component with bindkey

```yaml
xiaomi_ble:
  - mac_address: "A4:C1:38:XX:XX:XX"
    bindkey: "0123456789abcdef0123456789abcdef"
    id: lywsd03mmc

sensor:
  - platform: xiaomi_ble
    xiaomi_ble_id: lywsd03mmc
    temperature: { name: "Temperature" }
    humidity: { name: "Humidity" }
    battery_level: { name: "Battery" }
```

### Govee H5075/H5179
```yaml
# Similar approach with govee_ble component
```

## BLE Scan Parameters

```yaml
esp32_ble_tracker:
  scan_parameters:
    interval: 1600ms   # Time between scan windows
    window: 30ms       # Active scan duration
    active: false      # Passive scan (no scan response requests)
    continuous: true   # Scan continuously
```

- **Passive** (`active: false`): Lower power, gets manufacturer data only
- **Active** (`active: true`): Requests scan response, more data but more power
- **Interval/Window**: 1600ms/30ms = 1.8% duty cycle (good for battery)

## Multiple Sensors

```yaml
esp32_ble_tracker:
  on_bluetooth_le_advertise:
    - lambda: |-
        parse_xiaomi(x);
        parse_inkbird(x);
        parse_govee(x);

# Or use multiple ble_client for active connections
```

## MQTT Publishing Template

```yaml
sensor:
  - platform: template
    name: "Temperature"
    id: temp_sensor
    on_value:
      then:
        - mqtt.publish:
            topic: "sensors/temperature"
            payload: !lambda return to_string(x);

  - platform: template
    name: "Humidity"
    id: hum_sensor
    on_value:
      then:
        - mqtt.publish:
            topic: "sensors/humidity"
            payload: !lambda return to_string(x);
```

## References
- ESPHome BLE Tracker: https://esphome.io/components/esp32_ble_tracker.html
- Xiaomi BLE: https://github.com/syssi/esphome-xiaomi-ble
- Inkbird Protocol: https://github.com/ inkbird-bluetooth-protocol
- Govee BLE: https://github.com/ thehalo/govee-ble