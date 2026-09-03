"""Constants for the BLE Sensors integration."""

DOMAIN = "btsensors"

CONF_PARSER_KEY = "parser_key"

SIGNAL_STRENGTH_KEY = "signal_strength"
LAST_SEEN_KEY = "last_seen"

# Parser keys, also used as the "model family" shown to the user.
PARSER_GOVEE = "govee"
PARSER_SWITCHBOT = "switchbot"
PARSER_SP630E = "sp630e"
PARSER_GENERIC_RAW = "generic_raw"

# Service / manufacturer identifiers used for discovery and parser dispatch.
GOVEE_SERVICE_UUID = "0000ec88-0000-1000-8000-00805f9b34fb"
SWITCHBOT_SERVICE_DATA_UUID = "0000fd3d-0000-1000-8000-00805f9b34fb"
SWITCHBOT_MANUFACTURER_ID = 2409

# Unregistered manufacturer IDs with no decoder yet; see docs/device_identification.md.
BBQ_PROBE_MANUFACTURER_ID = 43521  # e.g. "T-80" style meat/BBQ thermometers
AEV_MANUFACTURER_ID = 1939  # e.g. "wSBR" named devices
SP630E_MANUFACTURER_ID = 20563  # Sperll SP630E LED controller (BanlanX app)
SP630E_SERVICE_UUID = "0000e0ff-0000-1000-8000-00805f9b34fb"
