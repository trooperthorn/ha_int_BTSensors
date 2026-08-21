# Device identification log

Ground truth for the captures in `tests/fixtures/advertisements.py`, established by cross-referencing the Bluetooth SIG company identifier registry and decoding each payload with the actual vendor library (`govee-ble`, `PySwitchbot`). See `tests/test_parsers.py` for the automated assertions.

| Capture label | Name | Manufacturer ID(s) | Service UUID(s) | Identified as | Parser |
|---|---|---|---|---|---|
| `switchbot_meter_1`, `switchbot_meter_2`, `switchbot_meter_3` | random MAC (privacy mode) | 2409 (`Woan Technology`, SwitchBot's registered SIG name) | `fd3d` (service_data) | SwitchBot Indoor/Outdoor Meter (`WoIOSensorTH`) | `switchbot` |
| `switchbot_curtain` | random MAC (privacy mode) | 2409 | `fd3d` (service_data) | SwitchBot Curtain 3 (`WoCurtain`) | `switchbot` |
| `govee_h5074` | `Govee_H5074_AF03` | 76 (spoofed/reused Apple ID + embedded `INTELLI_ROCKS` marker), 60552 (Govee's own `ec88` service reused as a manufacturer key) | `ec88` | Govee H5074 Thermo-Hygrometer | `govee` |
| `sp630e_controller` | `SP630E` | 20563 (unregistered) | `e0ff` | Sperll SP630E RGB(W) LED strip controller (BanlanX app) | `sp630e` (identification only, no control protocol yet -- see `docs/sp630e_protocol.md`) |
| `unidentified_t80` | `T-80` | 43521 / `0xAA01` (unregistered, commonly squatted by cheap BLE thermometers) | none | Likely a BBQ/meat-probe thermometer; exact vendor/protocol unconfirmed | `generic_raw` |
| `unidentified_wsbr` | `wSBR` | 1939 (`AEV spol. s r.o.`) | none | Unidentified; no public writeup found for this product | `generic_raw` |
| `unidentified_nordic_tracker` | random MAC | 89 (`Nordic Semiconductor ASA` -- generic SoC vendor ID, not a specific product) | `fee5` | Unidentified Nordic-chip-based device | `generic_raw` |
| `unidentified_x15wk` | `X15-WK` | 6 (`Microsoft` -- likely an SDK default/placeholder, not a genuine Microsoft beacon) | `180a` (Device Information), custom 128-bit UUID | Likely a generic Telink/JieLi-SDK wearable | `generic_raw` |

## How to identify a new device

1. Capture the advertisement (HA's Bluetooth integration diagnostics, or a raw BLE scanner app).
2. Look up the manufacturer_data company ID against the [Bluetooth SIG assigned numbers list](https://www.bluetooth.com/specifications/assigned-numbers/company-identifiers/) -- but don't stop there: many cheap devices reuse/squat unregistered or unrelated IDs (see `T-80`, `X15-WK` above), so also search the device name, service UUIDs, and payload length against known reverse-engineering writeups.
3. Check whether `govee-ble`, `PySwitchbot`, or another [Bluetooth-Devices](https://github.com/Bluetooth-Devices) library already decodes it before writing a new parser -- see `docs/adding_a_parser.md`.
4. Once identified, add a `Capture` fixture and, if a decoder exists or you write one, a `tests/test_parsers.py` assertion pinning the decoded values -- this is what "dynamically test to see if raw values map properly" means in practice for this project: real bytes in, asserted real-world values out.
