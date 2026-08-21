"""The BLE Sensors integration."""

from __future__ import annotations

import logging

from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.core import HomeAssistant

from .const import CONF_PARSER_KEY
from .coordinator import BTSensorsConfigEntry, BTSensorsCoordinator
from .parsers.registry import create_parser

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.LIGHT, Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: BTSensorsConfigEntry) -> bool:
    """Set up a BLE Sensors device from a config entry."""
    address: str = entry.data[CONF_ADDRESS]
    parser_key: str = entry.data[CONF_PARSER_KEY]
    parser = create_parser(parser_key)

    entry.runtime_data = coordinator = BTSensorsCoordinator(
        hass, _LOGGER, address, parser
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    # Only start scanning once every platform has had a chance to register
    # its processor, so the very first advertisement isn't dropped.
    entry.async_on_unload(coordinator.async_start())
    return True


async def async_unload_entry(hass: HomeAssistant, entry: BTSensorsConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
