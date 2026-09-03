"""Identification-only parser for Sperll SP630E-family LED controllers.

No control protocol is implemented; see docs/sp630e_protocol.md.
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
