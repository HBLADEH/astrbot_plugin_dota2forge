"""Standard-library-only version guard copied into generated host plugin roots."""

from __future__ import annotations

import json
import sys
from importlib import metadata
from pathlib import Path

ADAPTERS = {
    "Dota2UID": "dota2uid",
    "astrbot_plugin_dota2forge": "astrbot-plugin-dota2forge",
}
MINIMUM_PYTHON = (3, 12)


def verify_dependencies(entry: str) -> None:
    """Fail before SDK/runtime imports; never silently load an older shared library."""
    if sys.version_info < MINIMUM_PYTHON:
        raise RuntimeError("Dota2Forge requires Python 3.12 or newer. Upgrade the host first.")
    try:
        manifest = json.loads(Path(entry).with_name("release.json").read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or type(manifest.get("schema_version")) is not int:
            raise ValueError
        if manifest["schema_version"] != 1:
            raise ValueError
        adapter = ADAPTERS[manifest["plugin"]]
        expected = manifest["versions"]
        if not isinstance(expected, dict) or set(expected) != {
            "dota2forge-core",
            "dota2forge-renderer",
            "dota2forge-assets",
            adapter,
        }:
            raise ValueError
        if any(not isinstance(value, str) or not value for value in expected.values()):
            raise ValueError
    except (OSError, ValueError, KeyError, TypeError):
        raise RuntimeError(
            "Dota2Forge release manifest is missing or invalid. Reinstall the plugin."
        ) from None
    incompatible = []
    for name, version in sorted(expected.items()):
        try:
            installed = metadata.version(name)
        except metadata.PackageNotFoundError:
            installed = None
        if installed != version:
            incompatible.append(name)
    if incompatible:
        raise RuntimeError(
            "Dota2Forge dependencies are missing or incompatible: "
            + ", ".join(incompatible)
            + ". Stop the host, install the pinned versions, then restart."
        )
