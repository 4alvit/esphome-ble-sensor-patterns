# Inkbird internal-sensor decoding contract

See the [illustrated RC fuzzing process and verified rollout results](https://github.com/victron-venus/venus-os-ci-toolkit/blob/main/docs/rc-fuzzing-results.md)
for the shared release flow, evidence requirements and a dated cross-project
snapshot. The project-specific scope and reproduction guidance below still apply.

This repository owns the pure `decode_inkbird_th1_internal` C++ function and calls
it from `inkbird-ibs-th1.yaml`. It implements a narrow compatibility profile for
TH1 / TH1 Mini internal-sensor advertisements. It is not a manufacturer protocol
specification or evidence of hardware compatibility. TH2, TH3, external probes,
and other revisions are outside this profile. Unknown frames publish nothing.

## Evidence and correction

The pinned compile target is ESPHome 2026.10.0b1, commit
`33cf262616960c9549252f79ec540d19996715d4`. Its
[advertisement decoder](https://github.com/esphome/esphome/blob/33cf262616960c9549252f79ec540d19996715d4/esphome/components/ble_device_base/ble_device.cpp)
separates the first two manufacturer bytes into a little-endian UUID16 and passes
the remaining bytes separately. The
[manufacturer callback](https://github.com/esphome/esphome/blob/33cf262616960c9549252f79ec540d19996715d4/esphome/components/esp32_ble_tracker/automation.h)
therefore does not include those first two bytes in its vector.

The same release's
[Inkbird decoder](https://github.com/esphome/esphome/blob/33cf262616960c9549252f79ec540d19996715d4/esphome/components/inkbird_ibsth1_mini/inkbird_ibsth1_mini.cpp)
checks a public address, no service data, one manufacturer entry, UUID16 and seven
remaining bytes. It interprets UUID16 as signed temperature in hundredths,
remaining bytes 0–1 as unsigned humidity in hundredths, byte 2 as the sensor
selector, byte 5 as battery percent and byte 6 as marker 6 or 8. Its author
explicitly describes reverse engineering of a single device, with uncertainty.

As an independent cross-check, the
[inkbird-ble decoder](https://github.com/Bluetooth-Devices/inkbird-ble/blob/c88a839d2275ea8a773b61b50f028bb23baeec37/src/inkbird_ble/parser.py)
at `c88a839d2275ea8a773b61b50f028bb23baeec37` reconstructs the two-byte dictionary
key plus payload for its nine-byte sensor path, then decodes signed temperature,
unsigned humidity and byte 7 battery. It also rejects impossible humidity and
battery percentages. Its general documentation describes manufacturer keys as
company identifiers; the actual nine-byte reconstruction and decoder establish
the field offsets used here. This is not a general rule for other BLE devices.

The old example's fixed company filter `0x038A`, eleven-byte minimum and `0x2D`
frame were unsupported by these sources. Merely shifting its offsets would
preserve the wrong layout. The corrected example uses `on_ble_advertise` to keep
the UUID16 field available. No upstream source code is vendored or copied.

## Accepted input and output

The ESPHome automation selects the configured `inkbird_th1_mac`. The lambda then
requires a public address, no service data, exactly one manufacturer entry, and
UUID16. MAC selection is not authentication and does not prevent spoofing.

The pure function takes UUID16, a payload pointer and its length, and an output
record. It requires exactly seven bytes and a non-null pointer:

- Payload 0–1: unsigned little-endian relative humidity × 100, at most 10000.
- Payload 2: exactly 0 (internal sensor). Selector 1 is intentionally unsupported.
- Payload 3–4: uninterpreted; changing them cannot change any decoded reading.
- Payload 5: battery percent, 0 through 100.
- Payload 6: marker 6 or 8, as accepted by the pinned ESPHome decoder.
- UUID16: signed two's-complement temperature × 100. Mathematical sign extension
  handles the full encoding without an implementation-defined signed cast.

On failure the output record remains unchanged. On success integer hundredths
are returned; only the lambda converts to floats and publishes all three values.
Temperature's full encoding range is a decoder property, not a physical operating
range. No CRC, authenticity or sensor-calibration claim is made: neither selected
upstream decoder validates payload 3–4. Those bytes are intentionally uninterpreted.

## Validation boundaries

All fixtures are invented bytes with a public placeholder MAC, not captured
household traffic. Host tests exhaust all 65536 temperature encodings and cover
null/truncated/overlong input, unknown selectors and markers, and 100/101 percent
boundaries. They compile the actual lambda text with host API stubs, test its
publication behavior, and verify that compile staging copies the exact header.
The eight real ESPHome compile jobs separately check the actual ESPHome API.

The libFuzzer target calls the production header with arbitrary input; its oracle
independently checks acceptance and field arithmetic, unchanged failure output,
and invariance of ignored bytes/accepted markers. RC mutation runs on Linux with
Clang 18, ASan and UBSan. It has a 60-second target budget and 128-byte maximum
input. Setup compiles only a host executable; the mutation process has no network.
No ESP32 firmware runs, no BLE scan starts, and no MQTT message is sent.

Physical sensor revision, interference, timing, calibration and installation
remain untested. Validate them separately before relying on readings. This task
does not request or perform device access, firmware flashing or deployment.
