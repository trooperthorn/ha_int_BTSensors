"""Parser registry/decode tests against real captured advertisements.

These assertions are the ground truth established by manually
cross-checking each capture against `govee-ble`/`PySwitchbot` and the
Bluetooth SIG company identifier registry -- see
docs/device_identification.md. If a future change to a parser or the
registry's match order breaks one of these, that is a real regression.
"""

from __future__ import annotations

import pytest

from custom_components.btsensors.const import (
    PARSER_GENERIC_RAW,
    PARSER_GOVEE,
    PARSER_SWITCHBOT,
)
from custom_components.btsensors.parsers.registry import (
    create_parser,
    identify_parser_key,
)

from .fixtures.advertisements import CAPTURES, to_service_info

_EXPECTED_PARSER_KEY = {
    "switchbot_meter_1": PARSER_SWITCHBOT,
    "unidentified_t80": PARSER_GENERIC_RAW,
    "unidentified_wsbr": PARSER_GENERIC_RAW,
    "govee_h5074": PARSER_GOVEE,
    "switchbot_curtain": PARSER_SWITCHBOT,
    "switchbot_meter_2": PARSER_SWITCHBOT,
    "switchbot_meter_3": PARSER_SWITCHBOT,
    "unidentified_nordic_tracker": PARSER_GENERIC_RAW,
    "unidentified_x15wk": PARSER_GENERIC_RAW,
    "sp630e_controller": "sp630e",
}


@pytest.mark.parametrize("capture", CAPTURES, ids=lambda c: c.label)
def test_registry_dispatch(capture):
    """Every capture is routed to the parser we manually verified for it."""
    service_info = to_service_info(capture)
    assert identify_parser_key(service_info) == _EXPECTED_PARSER_KEY[capture.label]


def _capture(label: str):
    return next(c for c in CAPTURES if c.label == label)


def test_govee_h5074_decodes_temperature_humidity_battery():
    service_info = to_service_info(_capture("govee_h5074"))
    parser = create_parser(identify_parser_key(service_info))
    parsed = parser.parse(service_info)

    assert parsed.model == "H5074"
    assert parsed.manufacturer == "Govee"
    assert parsed.fields["temperature"].native_value == pytest.approx(24.09)
    assert parsed.fields["humidity"].native_value == pytest.approx(50.57)
    assert parsed.fields["battery"].native_value == 48
    assert not parsed.unmapped


def test_switchbot_meter_decodes_temperature_humidity_battery():
    service_info = to_service_info(_capture("switchbot_meter_1"))
    parser = create_parser(identify_parser_key(service_info))
    parsed = parser.parse(service_info)

    assert parsed.fields["temperature"].native_value == pytest.approx(28.3)
    assert parsed.fields["humidity"].native_value == 66
    assert parsed.fields["battery"].native_value == 100
    assert not parsed.unmapped


def test_switchbot_curtain_decodes_position_and_motion():
    service_info = to_service_info(_capture("switchbot_curtain"))
    parser = create_parser(identify_parser_key(service_info))
    parsed = parser.parse(service_info)

    assert parsed.fields["position"].native_value == 100
    assert parsed.fields["battery"].native_value == 81
    assert parsed.fields["inMotion"].native_value is False
    assert parsed.fields["inMotion"].binary is True


@pytest.mark.parametrize(
    "label",
    [
        "unidentified_t80",
        "unidentified_wsbr",
        "unidentified_nordic_tracker",
        "unidentified_x15wk",
    ],
)
def test_unidentified_devices_get_raw_diagnostics(label):
    """Devices with no vendor parser still surface rssi + raw hex fields."""
    service_info = to_service_info(_capture(label))
    parser = create_parser(identify_parser_key(service_info))
    parsed = parser.parse(service_info)

    assert parsed.unmapped is True
    assert parsed.fields["rssi"].native_value == service_info.rssi
    assert any(key.startswith("raw_manufacturer_data_") for key in parsed.fields)


def test_govee_parser_instance_is_reusable_across_updates():
    """A persistent parser (as the coordinator uses) must decode repeatedly."""
    service_info = to_service_info(_capture("govee_h5074"))
    parser = create_parser(PARSER_GOVEE)

    first = parser.parse(service_info)
    second = parser.parse(service_info)

    assert first.fields["temperature"].native_value == second.fields["temperature"].native_value
