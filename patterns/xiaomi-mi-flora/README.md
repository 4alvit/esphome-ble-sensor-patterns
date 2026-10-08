# Xiaomi Mi Flora (HHCCJCY01)

`mi-flora.yaml` uses ESPHome's built-in `xiaomi_hhccjcy01` passive BLE parser.
It declares temperature, moisture, conductivity, illuminance and battery entities;
which values arrive depends on the sensor's hardware and firmware advertisements.
There is no external Xiaomi repository or speculative custom frame parser.

Copy `secrets.example.yaml` to `secrets.yaml`, set `mi_flora_mac`, networking
credentials and a unique API encryption key. Validate and compile with the
pinned ESPHome version before using a trusted serial connection to install.
The previous firmware-version entity and active-connection example were not
supported by the referenced component and are removed. Existing entity names
for the five actual measurements are preserved.

See the [upstream Xiaomi BLE documentation](https://esphome.io/components/sensor/xiaomi_ble/)
for supported sensor/firmware variants. Do not assume a green newer plant sensor
or similarly named model uses the same protocol. Device behavior still requires
physical validation. See the root [security policy](../../SECURITY.md).
