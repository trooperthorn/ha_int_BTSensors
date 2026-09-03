"""Shared helpers for turning a ParsedDevice into HA's passive-update shape.

See docs/design.md for why every entity key uses device_id=None.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothDataUpdate,
    PassiveBluetoothEntityKey,
)
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.helpers.entity import EntityDescription

    from .parsers.base import ParsedDevice, ParsedField


def _device_info(parsed: ParsedDevice) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, parsed.address)},
        name=parsed.name,
        model=parsed.model or ("Unidentified device" if parsed.unmapped else None),
        manufacturer=parsed.manufacturer,
        sw_version=parsed.sw_version,
    )


def build_data_update(
    parsed: ParsedDevice,
    *,
    want_binary: bool,
    describe: Callable[[ParsedField], EntityDescription],
) -> PassiveBluetoothDataUpdate[object]:
    """Filter a ParsedDevice down to one entity domain's fields."""
    entity_descriptions: dict[PassiveBluetoothEntityKey, EntityDescription] = {}
    entity_data: dict[PassiveBluetoothEntityKey, object] = {}
    entity_names: dict[PassiveBluetoothEntityKey, str | None] = {}

    for field_key, entity_field in parsed.fields.items():
        if entity_field.binary != want_binary:
            continue
        entity_key = PassiveBluetoothEntityKey(field_key, None)
        entity_descriptions[entity_key] = describe(entity_field)
        entity_data[entity_key] = entity_field.native_value
        entity_names[entity_key] = entity_field.name

    return PassiveBluetoothDataUpdate(
        devices={None: _device_info(parsed)},
        entity_descriptions=entity_descriptions,
        entity_data=entity_data,
        entity_names=entity_names,
    )
