"""Identification-only parser for Sperll SP630E-family LED controllers.

The SP630E (BanlanX app) is a *controllable* device, not a passive
sensor -- there is nothing to decode from its advertisement beyond "this
is one of these". Control happens over an active GATT connection, see
``light.py``.

IMPORTANT: this integration does not currently send any control commands
to the device. A public, verified byte-level protocol for the SP630E
could not be found (unlike the closely related SP110E, older/simpler
protocol write-ups exist but do not clearly generalize to the SP630E's
firmware). Rather than guess and risk sending wrong commands to real
hardware, ``light.py`` only identifies/connects to the device and raises
a clear error on any control action until the real protocol is captured
and documented -- see ``docs/sp630e_protocol.md``.
"""

from __future__ import annotations

from home_assistant_bluetooth import BluetoothServiceInfoBleak

from ..const import PARSER_SP630E, SP630E_MANUFACTURER_ID, SP630E_SERVICE_UUID
from .base import ParsedDevice, ParsedField


class SP630EParser:
    key = PARSER_SP630E
    display_name = "Sperll SP630E LED controller (unconfirmed protocol)"

    @classmethod
    def can_parse(cls, service_info: BluetoothServiceInfoBleak) -> bool:
        has_manufacturer_id = SP630E_MANUFACTURER_ID in service_info.manufacturer_data
        has_service_uuid = SP630E_SERVICE_UUID in {
            uuid.lower() for uuid in service_info.service_uuids
        }
        return has_manufacturer_id or has_service_uuid

    def parse(self, service_info: BluetoothServiceInfoBleak) -> ParsedDevice:
        parsed = ParsedDevice(
            address=service_info.address,
            parser_key=self.key,
            name=service_info.name or service_info.address,
            model="SP630E",
            manufacturer="Sperll (BanlanX)",
            # Control-only device: nothing is decoded from the advertisement.
            unmapped=True,
        )
        parsed.add(
            ParsedField(
                key="rssi",
                name="Signal Strength",
                native_value=service_info.rssi,
                device_class="signal_strength",
                unit="dBm",
                entity_category="diagnostic",
            )
        )
        return parsed
