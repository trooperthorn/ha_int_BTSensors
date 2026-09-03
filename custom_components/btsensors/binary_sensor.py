"""Binary sensor platform: one entity per boolean decoded field."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothDataProcessor,
    PassiveBluetoothProcessorEntity,
)
from homeassistant.helpers.entity import EntityCategory

from .entity import build_data_update
from .parsers.base import ParsedDevice, ParsedField

if TYPE_CHECKING:
    from homeassistant.components.bluetooth.passive_update_processor import (
        PassiveBluetoothDataUpdate,
    )
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from .coordinator import BTSensorsConfigEntry

# Only the device classes a parser (see parsers/*.py) actually sets.
_DEVICE_CLASSES: dict[str, BinarySensorDeviceClass] = {
    "moving": BinarySensorDeviceClass.MOVING,
    "motion": BinarySensorDeviceClass.MOTION,
    "opening": BinarySensorDeviceClass.OPENING,
}


def _describe(field: ParsedField) -> BinarySensorEntityDescription:
    return BinarySensorEntityDescription(
        key=field.key,
        device_class=_DEVICE_CLASSES.get(field.device_class) if field.device_class else None,
        entity_category=EntityCategory.DIAGNOSTIC if field.entity_category == "diagnostic" else None,
        icon=field.icon,
    )


def _binary_sensor_update(parsed: ParsedDevice) -> PassiveBluetoothDataUpdate[object]:
    return build_data_update(parsed, want_binary=True, describe=_describe)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: BTSensorsConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up BLE Sensors binary_sensor entities."""
    coordinator = entry.runtime_data
    processor = PassiveBluetoothDataProcessor(_binary_sensor_update)
    entry.async_on_unload(
        processor.async_add_entities_listener(BTBinarySensorEntity, async_add_entities)
    )
    entry.async_on_unload(
        coordinator.async_register_processor(processor, BinarySensorEntityDescription)
    )


class BTBinarySensorEntity(
    PassiveBluetoothProcessorEntity[PassiveBluetoothDataProcessor[object, ParsedDevice]],
    BinarySensorEntity,
):
    """A single decoded boolean field."""

    @property
    @override
    def is_on(self) -> bool | None:
        return self.processor.entity_data.get(self.entity_key)
