"""Diagnostics support for the BLE Sensors integration.

Surfaces the last raw advertisement seen for a device alongside which
parser handled it -- this is the same raw-capture data the generic
fallback parser exposes as entities, bundled here for easy download when
filing a bug report or contributing a new parser.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components import bluetooth

from .const import CONF_PARSER_KEY

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .coordinator import BTSensorsConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: BTSensorsConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data

    service_info = bluetooth.async_last_service_info(
        hass, coordinator.address, connectable=False
    )

    return {
        "parser_key": entry.data.get(CONF_PARSER_KEY),
        "last_service_info": service_info,
    }
