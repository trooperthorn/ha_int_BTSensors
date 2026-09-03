# Security Policy

## Reporting a vulnerability

Do not open a public issue containing exploit details, credentials, private
addresses, or logs. Use GitHub's private vulnerability-reporting feature for
this repository. If private reporting is unavailable, open a minimal issue
asking the maintainer to establish a private channel; omit technical details.

Include the affected version/commit, prerequisites, impact, a minimal
reproduction, and suggested remediation. Remove tokens, API keys, cookies,
and private network details.

## Response targets

These are project targets, not an SLA: acknowledge critical/high reports in
three business days, establish severity and containment in seven, and publish
a coordinated fix/advisory as soon as safely validated. Lower-severity issues
are prioritized by exploitability and impact.

## Supported version

Only the latest published release and the default branch receive security
fixes. Operators should keep Home Assistant, this integration, and their
Bluetooth proxies updated, and retain a tested rollback/backup.

## Security boundaries

BLE Sensors is a passive-scanning Home Assistant integration; the light
platform (SP630E) additionally opens an active BLE GATT connection to
identify a device but sends no control commands (see
docs/sp630e_protocol.md). It is not a sandbox and cannot prevent a
malicious integration in the same Python process from reading shared
memory or files. Advertisement data from nearby BLE devices is untrusted
input; the generic raw-capture parser surfaces it as diagnostic hex data
rather than acting on it, and vendor parsers rely on upstream decoder
libraries (govee-ble, PySwitchbot) for the same devices Home Assistant
core's own integrations decode.
