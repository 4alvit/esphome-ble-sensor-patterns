# Install a BLE sensor example from your browser

Use **ESPHome Device Builder → Factory image → ESPHome Web → USB**. Device Builder
runs the compiler on Home Assistant or another server; your Windows, macOS or
Linux browser computer does not need Python, Homebrew or PlatformIO.

These are configurable examples, not one universal firmware. Each target needs
a sensor address, network settings and a private API key. Xiaomi encrypted
advertisements also need the device's matching bind key. A source beta/RC release
contains source files and validation evidence; it is not a firmware `.bin`.

## 1. Copy a complete example into Device Builder

1. Open your existing ESPHome Device Builder, or follow the
   [official installation guide](https://esphome.io/guides/installing_esphome/)
   to install it on Home Assistant or another server.
2. Choose an example matching the actual device from the
   [repository examples](../README.md#examples). The complete examples target a
   classic ESP32 (`esp32dev`); do not use them unchanged on ESP32-C3, S2, S3, C6 or
   ESP8266 hardware.
3. In Device Builder, create a device, then open **Edit**. Copy the **whole chosen
   YAML file**, rather than only its sensor block, into the editor. Preserve the
   device name you want and verify that its framework/board match your hardware.
   A complete starting point is
   [`patterns/jbd-bms/single-bms.yaml`](../patterns/jbd-bms/single-bms.yaml) with
   an appropriate JBD battery monitor.
4. Copy the corresponding `secrets.example.yaml` fields into Device Builder's
   private **Secrets** editor and replace all placeholders. If other devices
   already use those names, choose device-specific secret names and update the
   `!secret` references in this YAML; do not overwrite their credentials.
5. For the Inkbird profile, also place
   [`inkbird_th1_parser.h`](../patterns/ble-temp-sensor/inkbird_th1_parser.h) beside
   the device YAML, using Home Assistant's file editor if needed. Download both
   files from the same source release/revision. Keep any other referenced local
   files and relative paths intact.
6. Configure the actual BLE address, required model-specific keys, broker and
   a unique 32-byte Base64 API encryption key. Preserve a working device's
   established key and MQTT identity. The generic BLE skeleton deliberately
   reports unavailable until a model-specific parser is implemented; it is not
   a finished sensor decoder.

The configured key, network credentials and sensor identity are compiled into
your own image. Do not put real secrets or generated firmware in public issues,
source commits, CI artifacts or release downloads.

## 2. Download the serial factory image

Choose **Install → Manual download → Factory format** in Device Builder. The
server compiles the configuration and downloads a merged `.factory.bin` to the
computer running your browser. UI wording can vary slightly by version. Use a
compiler version validated for your source revision; see
[dependency lock maintenance](DEPENDENCY_LOCKS.md).

Choose the serial **factory** image, not an OTA-only application `.bin`. The
factory image includes the bootloader and partition data for initial USB
installation. A GitHub source ZIP or fuzzing report cannot be flashed.

## 3. Connect and install in the browser

1. Keep a backup of any working device's configuration and known-good firmware.
2. Connect the matching ESP32 board with a USB data cable to the browser computer.
3. Open **[ESPHome Web](https://web.esphome.io/)** directly in desktop Chrome or
   Edge. Select **Connect**, then choose the board's serial port.
4. Select **Install**, open your downloaded factory image, review the confirmation
   and any erase option, and start installation. Use your existing-project image,
   not a generic first-use image.
5. Leave power connected until completion, then inspect the logs and the real
   BLE/MQTT/API readings. A successful write does not validate a sensor decoder,
   radio range, battery behavior or calibration.

The generic [Espressif browser flasher](https://espressif.github.io/esptool-js/)
is an alternative for a **merged ESP32 factory image at `0x0`**. Do not reuse that
address for an OTA-only image or guess offsets for separate firmware parts.

## Browser and USB troubleshooting

- **Unsupported browser:** use current desktop Chrome or Edge. The installer
  needs the Web Serial API (`navigator.serial`); if unavailable, switch to a
  supported desktop browser. Mobile/iOS support is not assumed. Open the HTTPS
  page directly.
- **No port:** try a known USB data cable and a direct USB port. Check that the
  operating system sees the adapter; use the manufacturer's CP210x or CH340
  driver only when required.
- **Port busy:** close other serial monitors, log sessions and browser tabs using
  the port. On Linux, check the normal serial-device group permissions rather
  than running the browser as root.
- **Bootloader connection fails:** follow the board's BOOT/EN procedure. On a
  DevKit with those buttons, hold BOOT, briefly press EN/RESET, then release BOOT
  after connection. Do not short unidentified pins.
- **No readings after a successful flash:** verify the actual sensor address,
  model support, Xiaomi bind key where applicable, network credentials, broker
  access and selected parser. A BLE advertisement alone is not authenticated
  evidence that a reading is genuine.
- **Wrong image or resets:** stop and check chip family, flash capacity and image
  format. Do not force a different chip's image or blindly erase a working unit.

## Updating and release boundaries

The examples disable network OTA by default. Rebuild your existing private
configuration and use the same browser/serial path for updates, preserving keys
and identities. If you separately enable network updates, follow
[SECURITY.md](../SECURITY.md) and validate encrypted OTA; the web flasher does not
require enabling an HTTP management endpoint on the device.

CI compiles with synthetic credentials to check source compatibility. Its output
must not be published as ready-to-use firmware. A future public install button
needs a reviewed runtime onboarding flow for all required configuration, exact
board support, complete factory images and checksums. Until then, build once on
the server for your device and flash that private image from the browser.
