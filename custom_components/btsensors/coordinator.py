"""Per-device passive Bluetooth coordinator.

Each config entry represents one physical BLE device. This mirrors the
structure of Home Assistant core's own govee_ble/xiaomi_ble integrations:
a ``PassiveBluetoothProcessorCoordinator`` subclass owns one persistent
parser instance for the device's whole lifetime (created once in
``async_setup_entry``, not per-advertisement -- some parsers, like
`govee-ble`'s, accumulate state across multiple packets). See:
https://developers.home-assistant.io/docs/core/bluetooth/bluetooth_fetching_data/

The coordinator's ``update_method`` only calls the stored parser and
returns a ``ParsedDevice`` -- turning that into HA entities is the job of
each platform's own processor (sensor.py / binary_sensor.py / light.py),
same as core's split between coordinator (fetch+decode) and processor
(shape for a specific entity domain).
"""

from __future__ import annotations

from logging import Logger

from homeassistant.components.bluetooth import (
    BluetoothScanningMode,
    BluetoothServiceInfoBleak,
)
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothProcessorCoordinator,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .parsers.base import DeviceParser, ParsedDevice

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
