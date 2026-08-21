"""Pytest configuration: make `custom_components` importable."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
