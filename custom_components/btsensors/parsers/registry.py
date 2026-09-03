"""Parser identification and instantiation.

See docs/design.md for the identify/create split and match order, and
docs/adding_a_parser.md to add a new vendor parser.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..const import PARSER_GENERIC_RAW, PARSER_GOVEE, PARSER_SP630E, PARSER_SWITCHBOT
from .generic_raw import GenericRawParser
from .govee import GoveeParser
from .sp630e import SP630EParser
from .switchbot import SwitchbotParser

if TYPE_CHECKING:
    from home_assistant_bluetooth import BluetoothServiceInfoBleak

    from .base import DeviceParser, ParsedDevice

_PARSER_CLASSES: dict[str, type[DeviceParser]] = {
    PARSER_GOVEE: GoveeParser,
    PARSER_SWITCHBOT: SwitchbotParser,
    PARSER_SP630E: SP630EParser,
    PARSER_GENERIC_RAW: GenericRawParser,
}
_MATCH_ORDER: tuple[str, ...] = (PARSER_GOVEE, PARSER_SWITCHBOT, PARSER_SP630E)


def identify_parser_key(service_info: BluetoothServiceInfoBleak) -> str:
    """Return the parser key that should handle this advertisement."""
    for key in _MATCH_ORDER:
        if _PARSER_CLASSES[key].can_parse(service_info):
            return key
    return PARSER_GENERIC_RAW


def create_parser(parser_key: str) -> DeviceParser:
    """Instantiate the persistent parser for a given key.

    Falls back to the generic raw parser for an unknown/removed key so a
    config entry created by an older version of this integration never
    fails to set up.
    """
    parser_cls = _PARSER_CLASSES.get(parser_key, GenericRawParser)
    return parser_cls()


def identify_and_parse(service_info: BluetoothServiceInfoBleak) -> ParsedDevice:
    """One-shot identify + decode, for config-flow previews and tests.

    Not used by the coordinator: that path needs a persistent parser
    instance, created once via ``create_parser`` and reused across updates.
    """
    parser = create_parser(identify_parser_key(service_info))
    return parser.parse(service_info)


def display_name_for(parser_key: str) -> str:
    """Human readable label for a parser key, for config-flow UI."""
    parser_cls = _PARSER_CLASSES.get(parser_key, GenericRawParser)
    return parser_cls.display_name
