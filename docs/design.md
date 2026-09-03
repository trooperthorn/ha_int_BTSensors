# Design and architecture

This document collects the rationale that used to live in module
docstrings and inline comments. Code keeps a one-line purpose statement;
the "why" lives here.

## Parser protocol

Every parser turns a raw `BluetoothServiceInfoBleak` advertisement into a
`ParsedDevice`: a vendor-agnostic bag of named fields (temperature,
battery, and so on) plus identifying metadata. The rest of the
integration (`coordinator.py`, `sensor.py`, `binary_sensor.py`) only ever
deals with `ParsedDevice` / `ParsedField`; it has no vendor-specific
knowledge. See `custom_components/btsensors/parsers/base.py` for the
`DeviceParser` protocol these adapters implement.

Parsers must be cheap, synchronous, and side-effect free. They run on
every advertisement the Bluetooth scanner sees, potentially several times
a second per device, so they must not block or make network calls.

A parser instance is created once per physical device (per config entry)
and reused for the lifetime of that entry. Some underlying libraries,
such as `govee-ble`'s `GoveeBluetoothDeviceData`, accumulate state across
multiple advertisement or scan-response packets, so a fresh instance per
update would silently break multi-packet decoding.

`can_parse` is a classmethod for this reason: it only inspects the
advertisement shape (company IDs, service UUIDs) and must not depend on
any accumulated instance state, so it can cheaply be used for detection
before a persistent instance exists, for example during config flow.

## Parser registry

`parsers/registry.py` has two separate concerns:

* `identify_parser_key`: stateless detection, used during config flow
  (Bluetooth discovery and the manual device picker) to tell the user
  what kind of device they are adding, before any config entry exists.
* `create_parser`: builds the one persistent parser instance a config
  entry's coordinator reuses for its entire lifetime. The chosen
  `parser_key` is stored in the config entry so the same parser class is
  reconstructed after every Home Assistant restart. If a stored key no
  longer matches a registered parser (an older version of this
  integration used a since-removed key), `create_parser` falls back to
  `GenericRawParser` rather than failing config entry setup.

Order matters in `_MATCH_ORDER`: specific parsers are tried first,
`GenericRawParser` is the implicit catch-all fallback because its
`can_parse` always returns `True`. Add new vendor parsers by following
`docs/adding_a_parser.md`.

## Generic raw-capture fallback

`parsers/generic_raw.py` is what makes "probe and sense every device"
possible: any BLE advertisement this integration is configured to watch,
but that no vendor-specific parser recognizes, still becomes a Home
Assistant device with diagnostic entities showing exactly what was
received. That lets a user or contributor correlate the raw bytes with a
known ground truth, such as a real thermometer reading next to the
device, and then write a real parser.

## SwitchBot adapter

SwitchBot devices broadcast a wide variety of payloads (meters, curtains,
bots, contact and motion sensors, plugs) all under the same manufacturer
ID (2409) and service data UUID (fd3d). `PySwitchbot` already decodes all
of these; `parsers/switchbot.py` only flattens its output into
`ParsedField`s. Fields not covered by `_FIELD_META` still get an entity
as a plain, unitless sensor, so a new SwitchBot model or firmware field
never disappears silently; only its metadata is best-effort until a
mapping is added.

## Govee adapter

`parsers/govee.py` deliberately does not reimplement Govee's
advertisement format. The `sensor-state-data` ecosystem already
maintains a well-tested decoder for the whole Govee thermometer and
hygrometer family (H5074, H5075, H5100, H5101, H5104, H5105, H5106,
H5108, H5109, H5179, H5183, H5184, H5185, H5198, H5199, and others). This
module only adapts that decoder's output shape to `ParsedDevice`.

## Coordinator

Each config entry represents one physical BLE device. This mirrors the
structure of Home Assistant core's own `govee_ble` and `xiaomi_ble`
integrations: a `PassiveBluetoothProcessorCoordinator` subclass owns one
persistent parser instance for the device's whole lifetime, created once
in `async_setup_entry`, not per advertisement, for the state-accumulation
reason described above. See the [Bluetooth developer
docs](https://developers.home-assistant.io/docs/core/bluetooth/bluetooth_fetching_data/).

The coordinator's `update_method` only calls the stored parser and
returns a `ParsedDevice`. Turning that into HA entities is the job of
each platform's own processor (`sensor.py`, `binary_sensor.py`,
`light.py`), the same split core uses between coordinator (fetch and
decode) and processor (shape for a specific entity domain).

## Entity key shape

Both `sensor.py` and `binary_sensor.py` convert the coordinator's
`ParsedDevice` into a `PassiveBluetoothDataUpdate` through
`entity.py:build_data_update`, keeping only the fields relevant to their
entity domain (the `binary` flag on `ParsedField` decides sensor versus
binary_sensor). Since one config entry always represents exactly one
physical device, every entity key uses `device_id=None`; there is nothing
to disambiguate.

## Config flow

Config flow has two entry points, mirroring HA core's own BLE
integrations such as `govee_ble`: automatic discovery via the manifest's
`bluetooth` matchers (`async_step_bluetooth`), and a manual picker
(`async_step_user`) for anything the passive scanner has seen. The manual
picker deliberately lists every discovered device, not just
manifest-matched ones. That is what lets a user add a device with no
known decoder (the `T-80` or `wSBR` captures in
`docs/device_identification.md`) as a raw-capture entry to start
reverse-engineering it, per this integration's goal of probing and
sensing every device.

## SP630E light entity

`light.py` requires an active GATT connection because the SP630E does
not report its state via advertisements, unlike the passive
sensor/binary_sensor platforms. Control commands are intentionally not
implemented; see `docs/sp630e_protocol.md` for why and what is needed to
change that. `async_turn_on` and `async_turn_off` connect and raise a
clear, actionable error instead of silently doing nothing or guessing at
the byte protocol.
