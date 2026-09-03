"""Per-device passive Bluetooth coordinator.

One persistent parser instance per config entry; see docs/design.md.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.bluetooth import (
    BluetoothScanningMode,
    BluetoothServiceInfoBleak,
)
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothProcessorCoordinator,
)
from homeassistant.config_entries import ConfigEntry

from .parsers.base import DeviceParser, ParsedDevice

if TYPE_CHECKING:
    from logging import Logger

    from homeassistant.core import HomeAssistant

type BTSensorsConfigEntry = ConfigEntry[BTSensorsCoordinator]


def process_service_info(
    parser: DeviceParser, service_info: BluetoothServiceInfoBleak
) -> ParsedDevice:
    """Decode one advertisement using this device's persistent parser."""
    return parser.parse(service_info)


class BTSensorsCoordinator(PassiveBluetoothProcessorCoordinator[ParsedDevice]):
    """Passive scanning coordinator for one BLE device."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: Logger,
        address: str,
        parser: DeviceParser,
    ) -> None:
        self.parser = parser
        super().__init__(
            hass,
            logger,
            address,
            mode=BluetoothScanningMode.PASSIVE,
            update_method=lambda service_info: process_service_info(parser, service_info),
            connectable=False,
        )
