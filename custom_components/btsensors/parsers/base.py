"""Shared types for BLE advertisement parsers.

See docs/design.md for the parser architecture and why parsers must be
cheap, synchronous and side-effect free.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
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

    One persistent instance per config entry; see docs/design.md for why
    and for the ``can_parse``/``parse`` split.
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
