# Adding a parser for a new device

This integration deliberately does **not** try to reimplement decoding for devices that already have a mature, maintained parser -- see the survey that shaped this architecture, summarized below. Before writing a new parser, check whether one already exists.

## 1. Check for an existing decoder first

* Is it a Govee, SwitchBot, Xiaomi, BTHome, Inkbird, SensorPush, or similar named-vendor sensor? Home Assistant core very likely already supports it (`govee_ble`, `switchbot`, `xiaomi_ble`, `bthome`, ...), or a parser library exists in the [Bluetooth-Devices](https://github.com/Bluetooth-Devices) GitHub org (`sensor-state-data` ecosystem: `govee-ble`, `xiaomi-ble`, `bthome-ble`, `PySwitchbot`, ...).
* If a library exists: add it as a dependency (`manifest.json` `requirements` + `pyproject.toml`), write a thin adapter in `parsers/<vendor>.py` implementing the `DeviceParser` protocol (see `parsers/govee.py` / `parsers/switchbot.py` for the pattern), register it in `parsers/registry.py`, and add capture-based tests.
* If nothing exists: you're reverse-engineering a new device. Continue below.

## 2. Capture real advertisements

Add one or more real captures to `tests/fixtures/advertisements.py` (see `docs/device_identification.md` for the identification workflow). The `generic_raw` fallback parser already exposes every device's raw manufacturer/service data as diagnostic sensors in Home Assistant -- use that live view, correlated against the device's real-world state (e.g. a known-good thermometer reading next to it), to work out the byte layout.

## 3. Write the parser

Implement `DeviceParser` in `parsers/<name>.py`:

```python
class MyDeviceParser:
    key = "my_device"
    display_name = "My Device"

    @classmethod
    def can_parse(cls, service_info: BluetoothServiceInfoBleak) -> bool:
        ...  # cheap, stateless: company ID / service UUID / name check only

    def parse(self, service_info: BluetoothServiceInfoBleak) -> ParsedDevice:
        ...  # decode; instance state is fine here, see below
```

Important: `can_parse` is a `@classmethod` and must be side-effect-free -- it's used for detection before any config entry exists (during discovery/config flow). `parse`, on the other hand, is called on a **persistent, per-config-entry instance** that the coordinator keeps alive for the device's whole lifetime; if your decoding needs to accumulate state across multiple advertisement packets, put that state on `self`.

## 4. Register and test

Add your parser's key to `const.py`, register the class in `parsers/registry.py`'s `_PARSER_CLASSES` (and `_MATCH_ORDER` if it should be auto-detected, ahead of `generic_raw`), and add a `tests/test_parsers.py` case asserting the decoded values against your real capture.
