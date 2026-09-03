"""Fallback parser: always matches, exposes only raw/diagnostic data.

Must be tried last in the registry since can_parse() always returns True.
See docs/design.md and docs/adding_a_parser.md.
"""

from __future__ import annotations

from home_assistant_bluetooth import BluetoothServiceInfoBleak

from ..const import PARSER_GENERIC_RAW
from .base import ParsedDevice, ParsedField


class GenericRawParser:
    key = PARSER_GENERIC_RAW
    display_name = "Unidentified BLE device (raw capture)"

    @classmethod
    def can_parse(cls, service_info: BluetoothServiceInfoBleak) -> bool:
        return True

    def parse(self, service_info: BluetoothServiceInfoBleak) -> ParsedDevice:
        parsed = ParsedDevice(
            address=service_info.address,
            parser_key=self.key,
            name=service_info.name or service_info.address,
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

        for company_id, payload in service_info.manufacturer_data.items():
            parsed.add(
                ParsedField(
                    key=f"raw_manufacturer_data_{company_id}",
                    name=f"Raw Manufacturer Data ({company_id})",
                    native_value=payload.hex(),
                    entity_category="diagnostic",
                )
            )

        for service_uuid, payload in service_info.service_data.items():
            safe_key = service_uuid.replace("-", "")
            parsed.add(
                ParsedField(
                    key=f"raw_service_data_{safe_key}",
                    name=f"Raw Service Data ({service_uuid})",
                    native_value=payload.hex(),
                    entity_category="diagnostic",
                )
            )

        if service_info.service_uuids:
            parsed.add(
                ParsedField(
                    key="raw_service_uuids",
                    name="Advertised Service UUIDs",
                    native_value=", ".join(sorted(service_info.service_uuids)),
                    entity_category="diagnostic",
                )
            )

        return parsed
