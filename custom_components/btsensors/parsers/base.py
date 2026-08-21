"""Shared types for BLE advertisement parsers.

Every parser turns a raw ``BluetoothServiceInfoBleak`` advertisement into a
``ParsedDevice``: a vendor-agnostic bag of named fields (temperature,
battery, ...) plus identifying metadata. The rest of the integration
(coordinator, sensor/binary_sensor platforms) only ever deals with
``ParsedDevice``/``ParsedField`` -- it has no vendor-specific knowledge.

Parsers are intentionally cheap, synchronous and side-effect free: they are
called on every advertisement seen by the Bluetooth scanner (potentially
several times a second per device), so they must not block or make network
calls.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from home_assistant_bluetooth import BluetoothServiceInfoBleak


@dataclass(slots=True)
class ParsedField:
    """A single decoded value (temperature, battery, raw hex blob, ...)."""

    key: str
    name: str
    native_value: Any
    device_class: str | None = None
    unit: str | None = None
    entity_category: str | None = None  # e.g. "diagnostic"
    icon: str | None = None
    binary: bool = False


@dataclass(slots=True)
class ParsedDevice:
    """The decoded state of one physical BLE device."""

    address: str
    parser_key: str
    name: str
    model: str | None = None
    manufacturer: str | None = None
    sw_version: str | None = None
    # True when no vendor-specific decoder matched and this is raw-capture
    # diagnostic data only (see parsers/generic_raw.py).
    unmapped: bool = False
    fields: dict[str, ParsedField] = field(default_factory=dict)

    def add(self, parsed_field: ParsedField) -> None:
        self.fields[parsed_field.key] = parsed_field


class DeviceParser(Protocol):
    """A vendor-specific (or generic fallback) advertisement decoder.

    A parser instance is created once per physical device (per config
    entry) and reused for the lifetime of that entry -- some underlying
    libraries (e.g. `govee-ble`'s ``GoveeBluetoothDeviceData``) accumulate
    state across multiple advertisement/scan-response packets, so a fresh
    instance per update would silently break multi-packet decoding.
    ``can_parse`` is therefore a classmethod: it only inspects the
    advertisement shape (company IDs, service UUIDs) and must not depend on
    any accumulated instance state, so it can cheaply be used for detection
    *before* a persistent instance is created (e.g. during config flow).
    """

    #: Stable identifier, also used as the config-flow "detected type" and
    #: stored in the config entry so the same parser class is reconstructed
    #: on every Home Assistant restart.
    key: str
    #: Human readable label shown to the user during setup.
    display_name: str

    @classmethod
    def can_parse(cls, service_info: BluetoothServiceInfoBleak) -> bool:
        """Return True if this parser recognizes the advertisement."""

    def parse(self, service_info: BluetoothServiceInfoBleak) -> ParsedDevice:
        """Decode the advertisement. Only called after can_parse() is True."""
