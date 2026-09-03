# BLE Sensors

A custom Home Assistant integration that turns BLE advertisements seen by your [Bluetooth proxies](https://www.home-assistant.io/integrations/bluetooth/) into devices and entities -- for known sensor families (Govee, SwitchBot, ...) via well-tested decoder libraries, and for anything else via raw-capture diagnostic entities so it can be identified and a decoder contributed later.

Minimum required Home Assistant version: 2026.9.0

> **Before you install this for a Govee or SwitchBot device you already have working:** Home Assistant core ships its own `govee_ble` and `switchbot` integrations, actively maintained and Gold-quality-scale. This project depends on the exact same underlying libraries (`govee-ble`, `PySwitchbot`) for those vendors -- it does not reimplement their decoding. Running both core's integration and this one for the *same physical device* will create duplicate entities; either use core's integration for devices it already supports, or disable/ignore the core-discovered entry for that device if you want this integration to own it instead.

## Why this exists

Most BLE sensors on the market have no HA support at all, and the tooling to identify a mystery device (what company ID is this? does a decoder already exist?) is scattered. This integration is built to:

* Auto-discover any BLE device matching a known pattern (Bluetooth `manifest.json` matchers), or let you manually add **any** device your proxies have seen.
* Decode known device families using the actual `sensor-state-data`/`Bluetooth-Devices` ecosystem libraries HA core itself uses -- not a reimplementation.
* For anything unrecognized, still create a device with raw manufacturer/service-data hex and signal-strength diagnostic entities, so you (or a contributor) can correlate the bytes with the device's real-world state and write a real decoder.
* Keep vendor-specific knowledge entirely inside `parsers/`, so the sensor/binary_sensor platforms are fully generic -- adding support for a new device family never touches the entity code.

See [`docs/adding_a_parser.md`](docs/adding_a_parser.md) for the contribution workflow and [`docs/device_identification.md`](docs/device_identification.md) for how devices get identified. See [`docs/README.md`](docs/README.md) for the full documentation index.

## Supported today

| Device family | Decoder | Entities |
|---|---|---|
| Govee thermometer/hygrometers (H5074, H5075, ...) | `govee-ble` | Temperature, humidity, battery, signal strength |
| SwitchBot devices (meters, curtains, bots, contact/motion sensors, ...) | `PySwitchbot` | Whatever that model reports (temperature/humidity/battery for meters, position/motion/battery for curtains, etc.) |
| Sperll SP630E LED controller | identification only | Connectivity; **no control commands yet**, see [`docs/sp630e_protocol.md`](docs/sp630e_protocol.md) |
| Anything else | raw-capture fallback | Signal strength + raw manufacturer/service-data hex (diagnostic) |

## Architecture

* `parsers/` -- one module per device family implementing a small `DeviceParser` protocol (`can_parse` for detection, `parse` for decoding). `parsers/registry.py` dispatches advertisements to the right one, falling back to `parsers/generic_raw.py`.
* `coordinator.py` -- one `PassiveBluetoothProcessorCoordinator` per config entry (per physical device), holding a persistent parser instance for the device's lifetime (needed because some decoders accumulate state across multiple advertisement packets).
* `sensor.py` / `binary_sensor.py` -- fully generic: entities are created dynamically from whatever fields the active parser produced, with no per-vendor code.
* `light.py` -- SP630E connection scaffold; control protocol not yet implemented (see above).
* `config_flow.py` -- Bluetooth discovery for manifest-matched devices, plus a manual picker that lists *any* device the passive scanner has seen (including ones with no known decoder).

This mirrors the structure of Home Assistant core's own BLE integrations (`govee_ble`, `xiaomi_ble`, ...) -- see the [Bluetooth developer docs](https://developers.home-assistant.io/docs/core/bluetooth/bluetooth_fetching_data/).

## Development

```bash
python3.14 -m venv .venv
. .venv/bin/activate
pip install -e .[dev]
pytest
```

Tests run against real captured advertisements (`tests/fixtures/advertisements.py`) decoded with the actual vendor libraries -- see [`docs/device_identification.md`](docs/device_identification.md) for how each was identified.

## Quality scale

[`custom_components/btsensors/quality_scale.yaml`](custom_components/btsensors/quality_scale.yaml) tracks this integration's status against Home Assistant's [Integration Quality Scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/), targeting Platinum. It's an honest snapshot, not an aspirational claim -- most rules beyond Bronze are still `todo`.

## Downloading

### HACS

Add this repository as a custom repository in [HACS](https://hacs.xyz/), category "Integration".

### Manual

Copy `custom_components/btsensors` into your Home Assistant `custom_components` directory and restart.

## Issues

Please [file an issue](https://github.com/trooperthorn/ha_int_btsensors/issues), including diagnostics (Settings -> Devices & services -> BLE Sensors -> your device -> Download diagnostics) where relevant.
