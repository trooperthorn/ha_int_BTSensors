"""Real BLE advertisements captured via Home Assistant Bluetooth proxies.

Used as ground truth for parser tests: each entry pairs a raw capture
with the manually-verified identity of the device (see
docs/device_identification.md for how each was identified). Keeping real
captures as fixtures is also the mechanism this integration relies on for
"dynamically test to see if raw values map properly" -- a contributor
adds a new capture here, writes/adjusts a parser, and the test suite
proves the decode against real bytes rather than a hand-built payload.
"""

from __future__ import annotations

from dataclasses import dataclass

from bleak.backends.device import BLEDevice
from habluetooth import BluetoothServiceInfoBleak


@dataclass(frozen=True, slots=True)
class Capture:
    label: str
    name: str
    address: str
    rssi: int
    manufacturer_data: dict[int, str]  # company id -> hex string
    service_data: dict[str, str]  # uuid -> hex string
    service_uuids: list[str]
    source: str


CAPTURES: tuple[Capture, ...] = (
    Capture(
        "switchbot_meter_1",
        "E5:90:05:46:26:60",
        "E5:90:05:46:26:60",
        -85,
        {2409: "e590054626608a0e039c4200"},
        {"0000fd3d-0000-1000-8000-00805f9b34fb": "77c0e4"},
        [],
        "08:B6:1F:70:0E:9A",
    ),
    Capture(
        "unidentified_t80",
        "T-80",
        "00:80:E1:22:47:62",
        -93,
        {43521: "000000000080e1224762"},
        {},
        [],
        "08:B6:1F:70:0E:9A",
    ),
    Capture(
        "unidentified_wsbr",
        "wSBR",
        "94:DC:4E:17:24:A3",
        -90,
        {1939: "671b24bab85943058f3dcff1df7d9d63"},
        {},
        [],
        "08:B6:1F:70:0E:9A",
    ),
    Capture(
        "govee_h5074",
        "Govee_H5074_AF03",
        "A4:C1:38:1C:AF:03",
        -40,
        {
            76: "0215494e54454c4c495f524f434b535f48575075f2ffc2",
            60552: "006909c1133002",
        },
        {},
        ["0000ec88-0000-1000-8000-00805f9b34fb"],
        "00:01:95:CC:31:70",
    ),
    Capture(
        "switchbot_curtain",
        "DD:B7:6D:10:1B:C6",
        "DD:B7:6D:10:1B:C6",
        -41,
        {2409: "ddb76d101bc6260b0012048151"},
        {"0000fd3d-0000-1000-8000-00805f9b34fb": "7bc0d1001204"},
        [],
        "00:01:95:CC:31:70",
    ),
    Capture(
        "switchbot_meter_2",
        "D0:C8:40:C6:68:80",
        "D0:C8:40:C6:68:80",
        -64,
        {2409: "d0c840c66880cc0601831800"},
        {"0000fd3d-0000-1000-8000-00805f9b34fb": "7740c3"},
        [],
        "00:01:95:CC:31:70",
    ),
    Capture(
        "switchbot_meter_3",
        "E5:90:04:86:3A:15",
        "E5:90:04:86:3A:15",
        -61,
        {2409: "e59004863a15e20207992b00"},
        {"0000fd3d-0000-1000-8000-00805f9b34fb": "7700e4"},
        [],
        "00:01:95:CC:31:70",
    ),
    Capture(
        "unidentified_nordic_tracker",
        "FA:0A:0B:E7:DE:3E",
        "FA:0A:0B:E7:DE:3E",
        -69,
        {89: "08604ca8c7e7de3ef42d"},
        {},
        ["0000fee5-0000-1000-8000-00805f9b34fb"],
        "00:01:95:CC:31:70",
    ),
    Capture(
        "unidentified_x15wk",
        "X15-WK",
        "51:6E:F0:FF:A7:64",
        -63,
        {6: "010920228b61ef69282ae589fd3ce9f62d5feb2245ce9f4fa92c68"},
        {},
        ["0000180a-0000-1000-8000-00805f9b34fb", "3e1d50cd-7e3e-427d-8e1c-b78aa87fe624"],
        "00:01:95:CC:31:70",
    ),
    Capture(
        "sp630e_controller",
        "SP630E",
        "DA:21:3D:BB:20:01",
        -81,
        {20563: "1f10da213dbb2001"},
        {},
        ["0000e0ff-0000-1000-8000-00805f9b34fb"],
        "00:01:95:CC:31:70",
    ),
)


def to_service_info(capture: Capture) -> BluetoothServiceInfoBleak:
    """Build a real BluetoothServiceInfoBleak from a Capture fixture."""
    device = BLEDevice(capture.address, capture.name, {})
    return BluetoothServiceInfoBleak(
        name=capture.name,
        address=capture.address,
        rssi=capture.rssi,
        manufacturer_data={
            company_id: bytes.fromhex(payload)
            for company_id, payload in capture.manufacturer_data.items()
        },
        service_data={
            uuid: bytes.fromhex(payload) for uuid, payload in capture.service_data.items()
        },
        service_uuids=capture.service_uuids,
        source=capture.source,
        device=device,
        advertisement=None,
        connectable=True,
        time=0.0,
        tx_power=None,
        raw=None,
    )
