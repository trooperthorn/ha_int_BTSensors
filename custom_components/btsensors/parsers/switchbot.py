"""Adapter around the `PySwitchbot` advertisement parser.

Flattens PySwitchbot's decoded output into ParsedFields. Fields missing
from _FIELD_META still get an entity so new firmware fields never
disappear silently; see docs/design.md.
"""

from __future__ import annotations

from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from home_assistant_bluetooth import BluetoothServiceInfoBleak
from switchbot import SwitchBotAdvertisement, parse_advertisement_data

from ..const import (
    PARSER_SWITCHBOT,
    SWITCHBOT_MANUFACTURER_ID,
    SWITCHBOT_SERVICE_DATA_UUID,
)
from .base import ParsedDevice, ParsedField

# key -> (display name, device_class, unit, is_binary, entity_category)
_FIELD_META: dict[str, tuple[str, str | None, str | None, bool, str | None]] = {
    "temperature": ("Temperature", "temperature", "°C", False, None),
    "humidity": ("Humidity", "humidity", "%", False, None),
    "battery": ("Battery", "battery", "%", False, "diagnostic"),
    "position": ("Position", None, "%", False, None),
    "inMotion": ("In Motion", "moving", None, True, None),
    "calibration": ("Calibrated", None, None, True, "diagnostic"),
    "lightLevel": ("Light Level", None, None, False, None),
    "deviceChain": ("Device Chain", None, None, False, "diagnostic"),
    "isHold": ("Held", None, None, True, None),
    "motion_detected": ("Motion", "motion", None, True, None),
    "contact_open": ("Contact", "opening", None, True, None),
    "power": ("Power", "power", "W", False, None),
}

_SKIP_KEYS = {"temp", "fahrenheit"}  # duplicated by flat "temperature"


def _to_advertisement_data(service_info: BluetoothServiceInfoBleak) -> AdvertisementData:
    return AdvertisementData(
        local_name=service_info.name,
        manufacturer_data=service_info.manufacturer_data,
        service_data=service_info.service_data,
        service_uuids=service_info.service_uuids,
        rssi=service_info.rssi,
        tx_power=service_info.tx_power,
        platform_data=(),
    )


class SwitchbotParser:
    key = PARSER_SWITCHBOT
    display_name = "SwitchBot device"

    @classmethod
    def can_parse(cls, service_info: BluetoothServiceInfoBleak) -> bool:
        has_service_data = SWITCHBOT_SERVICE_DATA_UUID in {
            uuid.lower() for uuid in service_info.service_data
        }
        has_manufacturer_id = SWITCHBOT_MANUFACTURER_ID in service_info.manufacturer_data
        return has_service_data or has_manufacturer_id

    def parse(self, service_info: BluetoothServiceInfoBleak) -> ParsedDevice:
        ble_device = BLEDevice(service_info.address, service_info.address, {})
        adv = _to_advertisement_data(service_info)
        result: SwitchBotAdvertisement | None = parse_advertisement_data(ble_device, adv)

        parsed = ParsedDevice(
            address=service_info.address,
            parser_key=self.key,
            name=service_info.name or service_info.address,
            manufacturer="SwitchBot",
        )

        if result is None:
            # Encrypted or unrecognized SwitchBot payload: still identified
            # as SwitchBot by manufacturer/service UUID, but undecodable
            # without pairing/encryption keys.
            parsed.unmapped = True
            parsed.add(
                ParsedField(
                    key="undecoded",
                    name="Undecoded SwitchBot Payload",
                    native_value=True,
                    entity_category="diagnostic",
                    binary=True,
                )
            )
            return parsed

        parsed.model = result.data.get("modelFriendlyName")

        for key, value in result.data.get("data", {}).items():
            if key in _SKIP_KEYS:
                continue
            name, device_class, unit, binary, entity_category = _FIELD_META.get(
                key, (key, None, None, False, None)
            )
            parsed.add(
                ParsedField(
                    key=key,
                    name=name,
                    native_value=value,
                    device_class=device_class,
                    unit=unit,
                    binary=binary,
                    entity_category=entity_category,
                )
            )

        return parsed
