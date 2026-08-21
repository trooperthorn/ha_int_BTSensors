"""Light platform: SP630E-family LED controllers.

Unlike the sensor/binary_sensor platforms, this entity requires an active
GATT connection (SP630E does not report its state via advertisements).

Control commands are intentionally NOT implemented yet. See
``parsers/sp630e.py`` and ``docs/sp630e_protocol.md``: no publicly
verified byte-level protocol for this exact model could be found, and
sending guessed bytes to real LED-controller hardware risks corrupting
its settings or worse. ``async_turn_on``/``async_turn_off`` connect and
raise a clear, actionable error instead of silently doing nothing or
guessing. If you own this hardware and can capture the official BanlanX
app's GATT writes (e.g. via an Android Bluetooth HCI snoop log), please
contribute the protocol -- see the docs file for what's needed.
"""

from __future__ import annotations

import logging
from typing import Any

from bleak_retry_connector import BleakClientWithServiceCache, establish_connection
from homeassistant.components.bluetooth import async_ble_device_from_address
from homeassistant.components.light import LightEntity
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import CONF_PARSER_KEY, DOMAIN, PARSER_SP630E
from .coordinator import BTSensorsConfigEntry

_LOGGER = logging.getLogger(__name__)

_PROTOCOL_UNCONFIRMED_MESSAGE = (
    "No verified BLE write protocol is available for this device yet. "
    "See docs/sp630e_protocol.md in the btsensors repository for how to "
    "help capture and document it."
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BTSensorsConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the SP630E light entity, if this entry is one."""
    if entry.data.get(CONF_PARSER_KEY) != PARSER_SP630E:
        return
    async_add_entities([SP630ELightEntity(hass, entry.data[CONF_ADDRESS])])


class SP630ELightEntity(LightEntity):
    """Connection scaffold for an SP630E LED controller.

    Reports connectivity only; does not yet support turning on/off or
    setting color -- see module docstring.
    """

    _attr_has_entity_name = True
    _attr_name = None
    _attr_should_poll = False
    _attr_assumed_state = True

    def __init__(self, hass: HomeAssistant, address: str) -> None:
        self._hass = hass
        self._address = address
        self._attr_unique_id = address
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, address)},
            name=address,
            model="SP630E",
            manufacturer="Sperll (BanlanX)",
        )
        self._attr_is_on = None

    async def _connect(self) -> BleakClientWithServiceCache:
        ble_device = async_ble_device_from_address(self._hass, self._address, connectable=True)
        if ble_device is None:
            raise HomeAssistantError(f"{self._address} is not currently reachable")
        return await establish_connection(
            BleakClientWithServiceCache, ble_device, self._address
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._connect()
        raise HomeAssistantError(_PROTOCOL_UNCONFIRMED_MESSAGE)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._connect()
        raise HomeAssistantError(_PROTOCOL_UNCONFIRMED_MESSAGE)
