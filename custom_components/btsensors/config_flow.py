"""Config flow for the BLE Sensors integration.

Bluetooth discovery plus a manual picker listing every seen device,
including ones with no known decoder; see docs/design.md.
"""

from __future__ import annotations

from typing import Any, override

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_ADDRESS
from homeassistant.exceptions import HomeAssistantError
import voluptuous as vol

from .const import CONF_PARSER_KEY, DOMAIN
from .parsers.registry import display_name_for, identify_parser_key

_BLUETOOTH_CONFIRM_WITHOUT_DISCOVERY_MESSAGE = (
    "async_step_bluetooth_confirm reached without a prior async_step_bluetooth call"
)


class BTSensorsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BLE Sensors."""

    VERSION = 1

    def __init__(self) -> None:
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._parser_key: str | None = None
        self._discovered_devices: dict[str, BluetoothServiceInfoBleak] = {}

    @override
    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle a manifest-matched device found by the bluetooth integration."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self._discovery_info = discovery_info
        self._parser_key = identify_parser_key(discovery_info)
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm setup, showing what this integration detected the device as."""
        if self._discovery_info is None or self._parser_key is None:
            raise HomeAssistantError(_BLUETOOTH_CONFIRM_WITHOUT_DISCOVERY_MESSAGE)
        discovery_info = self._discovery_info
        title = discovery_info.name or discovery_info.address

        if user_input is not None:
            return self.async_create_entry(
                title=title,
                data={
                    CONF_ADDRESS: discovery_info.address,
                    CONF_PARSER_KEY: self._parser_key,
                },
            )

        self._set_confirm_only()
        placeholders = {
            "name": title,
            "detected_type": display_name_for(self._parser_key),
        }
        self.context["title_placeholders"] = placeholders
        return self.async_show_form(
            step_id="bluetooth_confirm", description_placeholders=placeholders
        )

    @override
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle manual setup: pick from any device the scanner has seen."""
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            discovery_info = self._discovered_devices[address]
            parser_key = identify_parser_key(discovery_info)
            return self.async_create_entry(
                title=discovery_info.name or address,
                data={CONF_ADDRESS: address, CONF_PARSER_KEY: parser_key},
            )

        await bluetooth.async_request_active_scan(self.hass)
        current_addresses = self._async_current_ids(include_ignore=False)
        for discovery_info in async_discovered_service_info(self.hass, connectable=False):
            address = discovery_info.address
            if address in current_addresses or address in self._discovered_devices:
                continue
            self._discovered_devices[address] = discovery_info

        if not self._discovered_devices:
            return self.async_abort(reason="no_devices_found")

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ADDRESS): vol.In(
                        {
                            address: (
                                f"{discovery_info.name or address}"
                                f" ({display_name_for(identify_parser_key(discovery_info))})"
                            )
                            for address, discovery_info in self._discovered_devices.items()
                        }
                    )
                }
            ),
        )
