#include "patterns/ble-temp-sensor/inkbird_th1_parser.h"
#include <cassert>
#include <cstdint>

extern "C" int LLVMFuzzerTestOneInput(const std::uint8_t *input, std::size_t size) {
  if (size < 2) return 0;
  const auto uuid = static_cast<std::uint16_t>(input[0] + 256u * input[1]);
  const auto *payload = input + 2;
  const auto length = size - 2;
  ble_patterns::InkbirdReading reading{123456, 54321, 222};
  const bool accepted = ble_patterns::decode_inkbird_th1_internal(uuid, payload, length, reading);
  // Independent byte-level oracle for the documented internal-only profile.
  const bool expected = size == 9 && input[4] == 0 &&
      (input[8] == 6 || input[8] == 8) &&
      static_cast<unsigned>(input[2]) + 256u * input[3] <= 10000 && input[7] <= 100;
  assert(accepted == expected);
  if (!accepted) {
    assert(reading.temperature_hundredths == 123456);
    assert(reading.humidity_hundredths == 54321 && reading.battery_percent == 222);
    return 0;
  }
  const auto signed_high = input[1] < 128 ? static_cast<int>(input[1]) : static_cast<int>(input[1]) - 256;
  assert(reading.temperature_hundredths == signed_high * 256 + input[0]);
  assert(reading.humidity_hundredths == input[2] + 256u * input[3]);
  assert(reading.battery_percent == input[7]);
  std::uint8_t alternate[7];
  for (std::size_t i = 0; i < 7; ++i) alternate[i] = payload[i];
  alternate[3] ^= 0xff;  // Uninterpreted bytes cannot affect decoded values.
  alternate[4] ^= 0xff;
  alternate[6] = alternate[6] == 6 ? 8 : 6;
  ble_patterns::InkbirdReading other{};
  assert(ble_patterns::decode_inkbird_th1_internal(uuid, alternate, 7, other));
  assert(other.temperature_hundredths == reading.temperature_hundredths);
  assert(other.humidity_hundredths == reading.humidity_hundredths);
  assert(other.battery_percent == reading.battery_percent);
  return 0;
}
