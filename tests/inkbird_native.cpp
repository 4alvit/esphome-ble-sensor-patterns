// Host-only synthetic fixtures. The test inserts the actual YAML lambda below.
#include "patterns/ble-temp-sensor/inkbird_th1_parser.h"
#include <cassert>
#include <cmath>
#include <vector>
namespace esphome::ble_device_base {
constexpr int BLE_ADDR_TYPE_PUBLIC = 0;
struct ESPBTUUID {
  enum class Type { UUID16, UUID128 };
  Type kind = Type::UUID16;
  std::uint16_t value = 0;
  Type type() const { return kind; }
  std::uint16_t uuid16() const { return value; }
};
}
struct Entry {
  esphome::ble_device_base::ESPBTUUID uuid;
  std::vector<std::uint8_t> data;
};
struct Device {
  int address_type = 0;
  std::vector<int> services;
  std::vector<Entry> entries;
  int get_address_type() const { return address_type; }
  const auto &get_service_datas() const { return services; }
  const auto &get_manufacturer_datas() const { return entries; }
};
struct Sensor {
  int publications = 0;
  float value = 0;
  void publish_state(float next) { ++publications; value = next; }
};
Sensor sensor_temperature, sensor_humidity, sensor_battery;
#define id(sensor) sensor
void consume(const Device &x) {
// ACTUAL_YAML_LAMBDA
}
void reset() {
  sensor_temperature = {};
  sensor_humidity = {};
  sensor_battery = {};
}
void rejects(const Device &device) {
  reset();
  consume(device);
  assert(sensor_temperature.publications == 0);
  assert(sensor_humidity.publications == 0);
  assert(sensor_battery.publications == 0);
}
int main() {
  using ble_patterns::InkbirdReading;
  using ble_patterns::decode_inkbird_th1_internal;
  InkbirdReading reading{123456, 54321, 222};
  std::uint8_t data[33] = {0x88, 0x13, 0, 0, 0, 50, 8};
  assert(!decode_inkbird_th1_internal(0, nullptr, 7, reading));
  for (std::size_t length = 0; length <= 33; ++length) {
    if (length == 7) continue;
    assert(!decode_inkbird_th1_internal(0, data, length, reading));
  }
  assert(reading.temperature_hundredths == 123456);
  assert(reading.humidity_hundredths == 54321 && reading.battery_percent == 222);
  // Exhaust all signed 16-bit representations without signed casts or shifts.
  for (unsigned word = 0; word < 65536; ++word) {
    assert(decode_inkbird_th1_internal(static_cast<std::uint16_t>(word), data, 7, reading));
    const int expected = word < 32768 ? static_cast<int>(word) : static_cast<int>(word) - 65536;
    assert(reading.temperature_hundredths == expected);
    assert(reading.humidity_hundredths == 5000 && reading.battery_percent == 50);
  }
  for (unsigned selector = 1; selector < 256; ++selector) {
    data[2] = static_cast<std::uint8_t>(selector);
    assert(!decode_inkbird_th1_internal(0, data, 7, reading));
  }
  data[2] = 0;
  for (unsigned marker = 0; marker < 256; ++marker) {
    data[6] = static_cast<std::uint8_t>(marker);
    assert(decode_inkbird_th1_internal(0, data, 7, reading) == (marker == 6 || marker == 8));
  }
  data[6] = 8;
  for (unsigned humidity : {0u, 10000u, 10001u, 10100u, 65535u}) {
    data[0] = static_cast<std::uint8_t>(humidity & 0xff);
    data[1] = static_cast<std::uint8_t>(humidity / 256);
    assert(decode_inkbird_th1_internal(0, data, 7, reading) == (humidity <= 10000));
  }
  data[0] = 0x10; data[1] = 0x27;
  for (unsigned battery : {0u, 100u, 101u, 255u}) {
    data[5] = static_cast<std::uint8_t>(battery);
    assert(decode_inkbird_th1_internal(0, data, 7, reading) == (battery <= 100));
  }
  Device valid;
  valid.entries.push_back({{esphome::ble_device_base::ESPBTUUID::Type::UUID16, 0xfb2e},
                           {0x88, 0x13, 0, 0, 0, 100, 8}});
  reset(); consume(valid);
  assert(sensor_temperature.publications == 1 && std::abs(sensor_temperature.value + 12.34f) < 0.001f);
  assert(sensor_humidity.publications == 1 && sensor_humidity.value == 50.0f);
  assert(sensor_battery.publications == 1 && sensor_battery.value == 100.0f);
  auto changed = valid; changed.address_type = 1; rejects(changed);
  changed = valid; changed.services.push_back(1); rejects(changed);
  changed = valid; changed.entries.clear(); rejects(changed);
  changed = valid; changed.entries.push_back(valid.entries[0]); rejects(changed);
  changed = valid; changed.entries[0].uuid.kind = esphome::ble_device_base::ESPBTUUID::Type::UUID128; rejects(changed);
  changed = valid; changed.entries[0].data[2] = 1; rejects(changed);
  changed = valid; changed.entries[0].data[5] = 101; rejects(changed);
  changed = valid; changed.entries[0].data.resize(6); rejects(changed);
  return 0;
}
