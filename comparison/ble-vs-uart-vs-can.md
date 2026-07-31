# BLE vs UART vs CAN Comparison by Sensor Type

Reference for choosing communication protocol for each sensor type.

## Comparison Table

| Sensor Type | BLE | UART/RS485 | CAN | Recommended | Notes |
|-------------|-----|------------|-----|-------------|-------|
| **JBD BMS** | ✅ Native | ✅ RS485 | ❌ | UART for >4 units | BLE limited to ~8 concurrent; UART daisy-chain reliable |
| **Daly BMS** | ✅ Native | ✅ RS485 | ❌ | UART for >4 units | Similar to JBD; UART more stable for many BMS |
| **Generic Temp (LYWSD03MMC, Inkbird, etc.)** | ✅ Adv only | ❌ | ❌ | **BLE** | Passive scan, battery lasts years; no wired option |
| **Xiaomi Mi Flora** | ✅ Adv + Conn | ❌ | ❌ | **BLE** | Requires active connection for full data |
| **Victron SmartShunt** | ✅ VE.Direct BLE | ✅ VE.Direct | ✅ VE.Can | **Any** | All three available; CAN for boat/RV networks |
| **Victron BMV-712** | ✅ VE.Direct BLE | ✅ VE.Direct | ✅ VE.Can | **Any** | Same as SmartShunt |
| **Victron Lynx Shunt** | ❌ | ✅ VE.Can | ✅ VE.Can | **CAN** | No BLE; CAN for system integration |
| **Pylontech BMS** | ❌ | ✅ RS485 | ✅ CAN | **CAN** | Proprietary CAN protocol; UART for service only |
| **Growatt BMS** | ❌ | ✅ RS485 | ❌ | **UART** | Modbus RTU over RS485 |
| **Solark/EG4 BMS** | ❌ | ✅ RS485 | ❌ | **UART** | Modbus RTU |
| **REC BMS** | ✅ BLE | ✅ RS485 | ✅ CAN | **CAN** | Full CAN integration for parallel stacks |
| **Batrium BMS** | ❌ | ✅ RS485 | ✅ CAN | **CAN** | BMS+, Link CAN for cell data |
| **SmartSolar MPPT** | ✅ VE.Direct BLE | ✅ VE.Direct | ❌ | **BLE** or **UART** | No CAN on MPPT; VE.Direct for monitoring |
| **Cerbo GX / Ekrano GX** | ✅ BLE | ✅ VE.Direct | ✅ VE.Can | **CAN** | Central hub; CAN for system bus |
| **Ruuvitag / SensorPush** | ✅ Adv only | ❌ | ❌ | **BLE** | Pure advertisement sensors |
| **SwitchBot Meter** | ✅ Adv only | ❌ | ❌ | **BLE** | Encrypted, needs key |

## Protocol Decision Guide

```
Need to monitor >8 BMS units on one ESP32?
├── Yes → Use UART/RS485 daisy chain
└── No  → BLE OK (event-driven sequential)

Sensor only has BLE?
├── Yes → Use BLE (passive scan for temp, active for Mi Flora)
└── No  → Prefer wired (UART/CAN) for reliability

Building mobile/boat/RV system?
├── Yes → CAN bus (Victron VE.Can, RV-C, J1939)
└── No  → UART for short runs, CAN for long/distributed

Need real-time cell balancing data?
├── Yes → CAN (BMS protocols expose per-cell data)
└── No  → UART Modbus sufficient for pack-level

Sensor battery powered (Mi Flora, temp sensors)?
├── Yes → BLE passive scan preserves sensor battery
└── No  → Wired preferred

Integration with Victron ecosystem?
├── Yes → VE.Direct (UART) or VE.Can (CAN)
└── No  → Protocol based on sensor availability
```

## ESP32 Connection Limits

| Protocol | Max Concurrent | Practical Limit | Notes |
|----------|----------------|-----------------|-------|
| BLE | 9 (CONFIG_BT_ACL_CONNECTIONS) | 4-6 | Memory/IRAM constrained |
| UART | 3 hardware + soft | 3-4 | Requires RS485 transceivers |
| CAN | 1 (TWAI controller) | 1 bus | Use CAN bus with multiple devices |

## Multi-BMS Architecture

```
Option A: Single ESP32, BLE Sequential (≤4 BMS)
└── ESP32 → BLE scan → Connect BMS1 → Read → Disconnect → Connect BMS2 → ...

Option B: Single ESP32, UART Daisy Chain (≤8 BMS)
└── ESP32 UART → MAX485 → BMS1 → BMS2 → BMS3 → ... (RS485 bus)

Option C: Multiple ESP32, Each 1-2 BMS BLE
└── ESP32-1 → BLE → BMS1, BMS2
    ESP32-2 → BLE → BMS3, BMS4
    All → MQTT → Home Assistant

Option D: CAN Bus (Victron/REC/Pylontech)
└── ESP32-S3-TWAI → CAN → BMS1, BMS2, BMS3... (parallel)
    → VE.Can → Cerbo GX
```

## Recommended by Use Case

| Use Case | Protocol | Hardware |
|----------|----------|----------|
| 1-4 JBD/Daly BMS, fixed install | BLE Sequential | ESP32 + external antenna |
| 5+ JBD/Daly BMS | UART RS485 | ESP32 + MAX485 + 120Ω term |
| Victron ESS system | VE.Can | Cerbo GX + CAN cables |
| Mobile/boat/RV | CAN (RV-C/VE.Can) | Cerbo GX + CAN bus |
| Temperature sensors only | BLE Passive | ESP32 (no antenna needed) |
| Plant sensors (Mi Flora) | BLE Active | ESP32, 5-min poll interval |
| Mixed sensors | BLE + UART + CAN | Multiple ESP32 or ESP32-S3 |

## References

- ESP32 BLE Limits: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/bluetooth/bluedroid.html
- JBD BLE Protocol: https://github.com/syssi/esphome-jbd-bms
- Daly BLE Protocol: https://github.com/syssi/esphome-daly-bms
- Victron VE.Can: https://www.victronenergy.com/white-papers
- Xiaomi Mi Flora: https://github.com/Cyclenerd/Flora