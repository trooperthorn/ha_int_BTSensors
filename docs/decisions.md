# Decisions

Dated decisions and the alternatives that were rejected. Newest first.

## 2026-09-03: quality_scale.yaml honesty policy

`custom_components/btsensors/quality_scale.yaml` is kept as an honest
snapshot of a freshly scaffolded integration, not an aspirational claim.
Most Silver, Gold, and Platinum rules are marked `todo`. A rule is only
moved to `done` once it is actually implemented and, where applicable,
covered by a test; see `tests/test_parsers.py` for the start of that
coverage. The alternative, marking rules `done` ahead of the work to
signal an intended quality target, was rejected because it would make the
file useless as a status check for CI or a future contributor.

## 2026-09-03: do not reimplement vendor decoding

For Govee and SwitchBot devices, this integration wraps the same
`govee-ble` and `PySwitchbot` libraries Home Assistant core's own
`govee_ble` and `switchbot` integrations use, rather than writing new
decoders. The alternative, an independent decoder per vendor, was
rejected: it would duplicate already-tested code and diverge from core's
behavior over time as those libraries are updated for new firmware.

## 2026-09-03: no guessed SP630E control protocol

`light.py` does not send control commands to the Sperll SP630E LED
controller. No publicly verified byte-level GATT write protocol for this
exact model could be found as of August 2026; the closely related
SP110E/SP108E controllers have some community reverse-engineering, but
nothing found clearly generalizes to the SP630E's firmware. The
alternative, sending best-guess command bytes based on the related
models, was rejected because it risks corrupting a user's real hardware
configuration or producing undefined behavior. See
`docs/sp630e_protocol.md` for what is needed to change this.
