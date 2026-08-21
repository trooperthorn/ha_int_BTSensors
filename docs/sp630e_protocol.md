# SP630E control protocol -- help wanted

The Sperll SP630E (controlled by the "BanlanX" mobile app) is included in this integration's scope as a controllable BLE LED strip controller, but **no control commands are implemented yet**. `light.py` connects to the device and identifies it, but `async_turn_on`/`async_turn_off` deliberately raise an error instead of guessing at the byte protocol.

## Why nothing is implemented

A web search (August 2026) did not turn up a publicly documented, verified byte-level GATT write protocol for this exact model. The closely related SP110E/SP108E controllers have some community reverse-engineering, but nothing found clearly generalizes to the SP630E's firmware, and sending guessed command bytes to a real LED controller risks corrupting its configuration or producing undefined behavior. That's not an acceptable trade for a guess.

## What's known so far

* Manufacturer ID `20563` (`0x5053`), unregistered in the Bluetooth SIG list.
* Advertises service UUID `0000e0ff-0000-1000-8000-00805f9b34fb`.
* Confirmed product: Shenzhen Sperll Optoelectronic Technology SP630E, an SPI+PWM RGB(W) LED strip controller.

## How to help

If you own this hardware:

1. Install the official "BanlanX" app and pair with the device.
2. Capture the GATT writes it sends while changing power/color/brightness -- e.g. an Android Bluetooth HCI snoop log (Developer Options -> "Enable Bluetooth HCI snoop log"), opened in Wireshark, filtered to the device's address and `ATT` write requests.
3. Open an issue or PR with the captured characteristic UUID(s) and byte sequences for each action (power on/off, set RGB, set brightness, set effect), ideally with the app state before/after each capture.
4. Once the protocol is verified, implement it in `parsers/sp630e.py`/`light.py` and add it to `docs/device_identification.md`.
