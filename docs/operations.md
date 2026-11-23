# Operations

## Test environment dependencies

Native Windows cannot run the test suite: `homeassistant.runner` imports
`fcntl`, which is POSIX-only. Run `pytest` under WSL or Linux.

The suite runs on `pytest-homeassistant`, the harness published from
home-assistant/core. Each release pins the exact matching `homeassistant`
(and `pytest`, `pytest-asyncio` and friends), so the `dev` extra in
`pyproject.toml` keeps `homeassistant==X` and
`pytest-homeassistant[bluetooth]==X` on the same version; bump them together.
The plugin loads automatically. `addopts` carries `-p no:respx` so Home
Assistant installs its httpx alias before respx is imported, as the harness
README requires.

The `bluetooth` extra of the harness is required even though this integration
never imports those packages directly. Importing
`homeassistant.components.bluetooth` (used by `coordinator.py`) transitively
imports `homeassistant.components.usb` and, since core 2026.11,
`homeassistant.components.hassio`, and the `homeassistant` PyPI package does
not bundle component-level requirements the way a full Home Assistant
installation does. The extra installs core's own versions of `aiousbwatcher`,
`serialx`, `aiohasupervisor` and the Bluetooth stack. Without it, `pytest`
fails at collection with `ModuleNotFoundError: No module named
'aiohasupervisor'` on a fresh environment, even though the integration itself
has no USB or Supervisor dependency.
