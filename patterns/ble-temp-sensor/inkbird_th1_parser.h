#pragma once

#include <cstddef>
#include <cstdint>

// Narrow internal-sensor compatibility profile; see docs/inkbird-contract.md.
// The UUID is the first two manufacturer bytes already removed by ESPHome.
namespace ble_patterns {
struct InkbirdReading {
  std::int32_t temperature_hundredths;
  std::uint16_t humidity_hundredths;
  std::uint8_t battery_percent;
};

inline bool decode_inkbird_th1_internal(std::uint16_t manufacturer_uuid,
                                        const std::uint8_t *data,
                                        std::size_t size,
                                        InkbirdReading &output) noexcept {
  if (data == nullptr || size != 7 || data[2] != 0 ||
      (data[6] != 6 && data[6] != 8)) {
    return false;
  }
  const auto humidity = static_cast<std::uint16_t>(
      static_cast<std::uint16_t>(data[0]) |
      (static_cast<std::uint16_t>(data[1]) << 8));
  if (humidity > 10000 || data[5] > 100) {
    return false;
  }
  // Mathematical sign extension avoids implementation-defined uint16 -> int16.
  const std::int32_t temperature = manufacturer_uuid < 0x8000
      ? manufacturer_uuid : static_cast<std::int32_t>(manufacturer_uuid) - 65536;
  output = {temperature, humidity, data[5]};
  return true;
}
}  // namespace ble_patterns
