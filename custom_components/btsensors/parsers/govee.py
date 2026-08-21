"""Adapter around the `govee-ble` (Bluetooth-Devices) parser library.

We deliberately do not reimplement Govee's advertisement format: the
`sensor-state-data` ecosystem already maintains a well-tested decoder for
the whole Govee thermometer/hygrometer family (H5074, H5075, H5100,
H5101, H5104, H5105, H5106, H5108, H5109, H5179, H5183, H5184, H5185,
H5198, H5199, ...). This module only adapts its output shape to our
``ParsedDevice``.
"""

from __future__ import annotations

from govee_ble import GoveeBluetoothDeviceData
from home_assistant_bluetooth import BluetoothServiceInfoBleak
from sensor_state_data import SensorUpdate

from ..const import GOVEE_SERVICE_UUID, PARSER_GOVEE
from .base import ParsedDevice, ParsedField


class GoveeParser:
    key = PARSER_GOVEE
    display_name = "Govee sensor"

    def __init__(self) -> None:
        self._data = GoveeBluetoothDeviceData()

    @classmethod
    def can_parse(cls, service_info: BluetoothServiceInfoBleak) -> bool:
        return GOVEE_SERVICE_UUID in {uuid.lower() for uuid in service_info.service_uuids}

    def parse(self, service_info: BluetoothServiceInfoBleak) -> ParsedDevice:
        update: SensorUpdate = self._data.update(service_info)
        device_info = update.devices.get(None)

        parsed = ParsedDevice(
            address=service_info.address,
            parser_key=self.key,
            name=service_info.name or service_info.address,
            model=device_info.model if device_info else None,
            manufacturer=device_info.manufacturer if device_info else "Govee",
            sw_version=device_info.sw_version if device_info else None,
        )

        for device_key, value in update.entity_values.items():
            description = update.entity_descriptions.get(device_key)
            device_class = (
                description.device_class.value
                if description and description.device_class
                else None
            )
            unit = (
                description.native_unit_of_measurement.value
                if description
                and description.native_unit_of_measurement
                and hasattr(description.native_unit_of_measurement, "value")
                else (
                    description.native_unit_of_measurement
                    if description
                    else None
                )
            )
            parsed.add(
                ParsedField(
                    key=device_key.key,
                    name=value.name or device_key.key,
                    native_value=value.native_value,
                    device_class=device_class,
                    unit=unit,
                )
            )

        return parsed
