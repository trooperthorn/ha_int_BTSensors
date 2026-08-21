"""Sensor platform: one entity per non-binary decoded field."""

from __future__ import annotations

from typing import override

from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothDataProcessor,
    PassiveBluetoothProcessorEntity,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import BTSensorsConfigEntry
from .entity import build_data_update
from .parsers.base import ParsedDevice, ParsedField

_NUMERIC_TYPES = (int, float)

# Only the device classes a parser (see parsers/*.py) actually sets. A
# field.device_class value with no entry here still becomes a sensor, just
# without a device_class -- new parser fields never disappear silently.
_DEVICE_CLASSES: dict[str, SensorDeviceClass] = {
    "temperature": SensorDeviceClass.TEMPERATURE,
    "humidity": SensorDeviceClass.HUMIDITY,
    "battery": SensorDeviceClass.BATTERY,
    "signal_strength": SensorDeviceClass.SIGNAL_STRENGTH,
    "power": SensorDeviceClass.POWER,
}


def _describe(field: ParsedField) -> SensorEntityDescription:
    return SensorEntityDescription(
        key=field.key,
        device_class=_DEVICE_CLASSES.get(field.device_class) if field.device_class else None,
        native_unit_of_measurement=field.unit,
        entity_category=EntityCategory.DIAGNOSTIC if field.entity_category == "diagnostic" else None,
        icon=field.icon,
        state_class=(
            SensorStateClass.MEASUREMENT
            if isinstance(field.native_value, _NUMERIC_TYPES)
            else None
        ),
    )


def _sensor_update(parsed: ParsedDevice):
    return build_data_update(parsed, want_binary=False, describe=_describe)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BTSensorsConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up BLE Sensors sensor entities."""
    coordinator = entry.runtime_data
    processor = PassiveBluetoothDataProcessor(_sensor_update)
    entry.async_on_unload(
        processor.async_add_entities_listener(BTSensorEntity, async_add_entities)
    )
    entry.async_on_unload(
        coordinator.async_register_processor(processor, SensorEntityDescription)
    )


class BTSensorEntity(
    PassiveBluetoothProcessorEntity[PassiveBluetoothDataProcessor[object, ParsedDevice]],
    SensorEntity,
):
    """A single decoded, non-binary field."""

    @property
    @override
    def native_value(self) -> object:
        return self.processor.entity_data.get(self.entity_key)
