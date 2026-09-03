# Operations

## Test environment dependencies

Native Windows cannot run the test suite: `homeassistant.runner` imports
`fcntl`, which is POSIX-only. Run `pytest` under WSL or Linux.

The `dev` extra pins `aiousbwatcher==1.1.2` and `serialx==1.9.0` even though
this integration never imports them directly. Importing
`homeassistant.components.bluetooth` (used by `coordinator.py`) transitively
imports `homeassistant.components.usb`, and the `homeassistant` PyPI package
does not bundle component-level requirements the way a full Home Assistant
installation does. Without these two pins, `pytest` fails at collection with
`ModuleNotFoundError: No module named 'aiousbwatcher'` on a fresh
environment, even though the integration itself has no USB dependency.
