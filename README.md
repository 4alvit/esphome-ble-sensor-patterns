# ESPHome BLE Sensor Patterns

> Reference library of production-ready ESPHome configurations for BLE sensors.
> Extracted from real deployments monitoring 8+ JBD BMS units, Daly BMS, and various temperature/plant sensors.

[![CI](https://github.com/4alvit/esphome-ble-sensor-patterns/workflows/CI/badge.svg)](https://github.com/4alvit/esphome-ble-sensor-patterns/actions)
[![ESPHome](https://img.shields.io/badge/ESPHome-2025.6%2B-green)](https://esphome.io)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)

## Patterns Included

| Pattern | Sensors | Config | Description |
|---------|---------|--------|-------------|
| [JBD BMS](patterns/jbd-bms/) | 8× BMS | `single-bms.yaml`, `multi-bms.yaml` | Event-driven sequential BLE polling for multiple BMS |
| [Daly BMS](patterns/daly-bms/) | 3× BMS | `single-bms.yaml`, `multi-bms.yaml` | Daly Smart BMS via BLE (FFE0/FFE1) |
| [BLE Temp](patterns/ble-temp-sensor/) | LYWSD03MMC, IBS-TH1 | `xiaomi-lywsd03mmc.yaml`, `inkbird-ibs-th1.yaml` | Passive scan for encrypted/unencrypted temp sensors |
| [Mi Flora](patterns/xiaomi-mi-flora/) | HHCCJCY01 | `mi-flora.yaml` | Plant sensor with MiOT protocol |

[→ Comparison: BLE vs UART vs CAN](comparison/ble-vs-uart-vs-can.md)

## Quick Start

```bash
# 1. Clone
git clone https://github.com/4alvit/esphome-ble-sensor-patterns.git
cd esphome-ble-sensor-patterns

# 2. Pick a pattern
cp patterns/jbd-bms/single-bms.yaml my-bms.yaml

# 3. Configure secrets
cp patterns/jbd-bms/secrets.example.yaml secrets.yaml
# Edit secrets.yaml with your WiFi, MQTT, MAC addresses

# 4. Compile & flash
esphome run my-bms.yaml
```

## Architecture Highlights

### Event-Driven Multi-BMS (JBD/Daly)
```yaml
# Prevents ESP32 BLE connection limit (~8 max)
ble_client:
  - mac_address: "AA:BB:CC:DD:EE:01"
    id: bms1_client
    auto_connect: false
    on_connect:
      - lambda: 'id(bms1).update();'
      - delay: 4s
      - ble_client.disconnect: bms1_client

interval:
  - interval: 30s
    then:
      - ble_client.connect: bms1_client  # Sequential polling
```

### ESP32 BLE Tuning (for 8+ devices)
```yaml
esp32:
  framework:
    type: esp-idf
    sdkconfig_options:
      CONFIG_BT_ACL_CONNECTIONS: "9"
      CONFIG_BT_GATTC_CONNECT_RETRY_COUNT: "3"
      CONFIG_BT_ALLOCATION_FROM_SPIRAM_FIRST: "y"
      CONFIG_BT_BLE_DYNAMIC_ENV_MEMORY: "y"

esp32_ble:
  max_connections: 8
```

### Encrypted Xiaomi Sensors
```yaml
xiaomi_ble:
  - mac_address: "A4:C1:38:XX:XX:XX"
    bindkey: !secret xiaomi_bindkey  # Get from Mi Home app
    id: lywsd03mmc

sensor:
  - platform: xiaomi_ble
    xiaomi_ble_id: lywsd03mmc
    temperature: { name: "Temp" }
    humidity: { name: "Hum" }
    battery_level: { name: "Battery" }
```

## Repository Structure

```
esphome-ble-sensor-patterns/
├── .github/workflows/ci.yml          # ESPHome compile matrix
├── patterns/
│   ├── jbd-bms/                      # JBD BMS (syssi/esphome-jbd-bms)
│   ├── daly-bms/                     # Daly BMS (syssi/esphome-daly-bms)
│   ├── ble-temp-sensor/              # Temp/humidity (passive scan)
│   ├── xiaomi-mi-flora/              # Plant sensor (MiOT)
│   └── common/                       # Shared templates
│       ├── esp32-ble-config.yaml
│       ├── ble-client-template.yaml
│       ├── mqtt-template.yaml
│       └── secrets.example.yaml
├── comparison/
│   └── ble-vs-uart-vs-can.md         # Protocol comparison table
�└── README.md
```

## External Components Used

All patterns use official ESPHome external components (no custom C++):

| Component | Repository | Sensors |
|-----------|------------|---------|
| `jbd_bms_ble` | syssi/esphome-jbd-bms | JBD BMS |
| `daly_bms_ble` | syssi/esphome-daly-bms | Daly BMS |
| `xiaomi_ble` | syssi/esphome-xiaomi-ble | LYWSD03MMC, etc. |
| `xiaomi_miot` | syssi/esphome-xiaomi-miot | Mi Flora |

## CI Validation

Every push compiles all patterns against ESPHome 2025.6:

```yaml
matrix:
  pattern:
    - jbd-bms/single-bms.yaml
    - jbd-bms/multi-bms.yaml
    - daly-bms/single-bms.yaml
    - daly-bms/multi-bms.yaml
    - ble-temp-sensor/xiaomi-lywsd03mmc.yaml
    - ble-temp-sensor/inkbird-ibs-th1.yaml
    - ble-temp-sensor/generic-ble-temp.yaml
    - xiaomi-mi-flora/mi-flora.yaml
```

## Contributing

1. Add new pattern in `patterns/<name>/`
2. Include `README.md`, `*.yaml`, `secrets.example.yaml`
3. Update CI matrix in `.github/workflows/ci.yml`
4. Ensure `esphome compile` passes locally
5. PR welcome!

## License

MIT - Use freely in your projects.

---

**Maintained by [4alvit](https://github.com/4alvit)** · Part of the Victron/Energy monitoring ecosystem