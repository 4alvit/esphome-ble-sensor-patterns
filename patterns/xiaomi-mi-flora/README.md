# Xiaomi Mi Flora Plant Sensor (HHCCJCY01) Pattern

Xiaomi Mi Flora / Flower Care plant monitor via BLE.

## Hardware
- Xiaomi Mi Flora (HHCCJCY01) - older white version
- Xiaomi Mi Flora v2 - newer green version
- ESP32 with Bluetooth
- Service UUID: `0xFE95` (Xiaomi MiOT)

## Sensors
| Sensor | Method | Notes |
|--------|--------|-------|
| Temperature | Advertisement | Real-time, from passive scan |
| Soil Moisture | Advertisement + Connection | % (0-100) |
| Fertility (EC) | Connection required | µS/cm via MiOT |
| Light (Lux) | Connection required | 0-65535 lux |
| Battery | Connection required | % |

## Two Approaches

### 1. Passive Scan (Advertisement Only)
- Reads temperature and moisture from BLE advertisements
- No active connection needed
- Battery friendly for sensor
- Limited data (no fertility, light, battery)

### 2. Active Connection (MiOT Protocol)
- Connects and reads via `xiaomi_miot` component
- Full sensor suite: temp, moisture, fertility, light, battery
- Drains sensor battery faster (~6 months vs ~12 months)
- Use `update_interval: 300s` (5 min) minimum

## Configuration
- `mi-flora.yaml` - Combined passive + active approach
- Use `xiaomi_miot` for full data, passive scan for temp/moisture

## External Component
```yaml
external_components:
  - source: github://syssi/esphome-xiaomi-miot@main
    refresh: 1d
    components: [xiaomi_miot]
```

## MAC Address Format
- Old (white): `C4:7C:8D:XX:XX:XX`
- New (green): `A4:C1:38:XX:XX:XX`

## Product IDs
- `0x00A4` - Mi Flora v1
- `0x00A5` - Mi Flora v2

## References
- Protocol: https://github.com/Cyclenerd/Flora
- Component: https://github.com/syssi/esphome-xiaomi-miot
- BLE spec: Xiaomi MiOT specification