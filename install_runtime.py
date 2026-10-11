"""Install pinned Dota2Forge runtime wheels while the selected host is stopped."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def public_requirements(root: Path) -> list[str]:
    release = json.loads((root / "release.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "runtime-wheels.json").read_text(encoding="utf-8"))
    plugins = {"Dota2UID": "dota2uid", "astrbot_plugin_dota2forge": "astrbot-plugin-dota2forge"}
    plugin = release.get("plugin") if isinstance(release, dict) else None
    if not isinstance(plugin, str) or plugin not in plugins:
        raise ValueError("Unknown Dota2Forge plugin.")
    adapter = plugins[plugin]
    names = {"dota2forge-core", "dota2forge-renderer", "dota2forge-assets", adapter}
    if (
        not isinstance(release, dict)
        or type(release.get("schema_version")) is not int
        or release.get("schema_version") != 1
        or not isinstance(release.get("versions"), dict)
        or set(release["versions"]) != names
        or not isinstance(manifest, dict)
        or type(manifest.get("schema_version")) is not int
        or manifest.get("schema_version") != 1
        or not isinstance(manifest.get("wheels"), dict)
        or set(manifest["wheels"]) != names
    ):
        raise ValueError("Invalid Dota2Forge release or runtime manifest.")
    repo = manifest.get("repository")
    if not isinstance(repo, str) or not re.fullmatch(
        r"https://github\.com/[A-Za-z0-9_-]+/" + re.escape(plugin), repo
    ):
        raise ValueError("Runtime wheels must come from the matching plugin GitHub repository.")
    for version in release["versions"].values():
        if not isinstance(version, str) or not re.fullmatch(r"[0-9][0-9A-Za-z.!+-]{0,63}", version):
            raise ValueError("Invalid runtime version.")
    tag = "v" + release["versions"][adapter]
    if manifest.get("release_tag") != tag:
        raise ValueError("Runtime release tag does not match the plugin.")
    requirements = []
    for name in sorted(names):
        wheel = manifest["wheels"][name]
        filename = f"{name.replace('-', '_')}-{release['versions'][name]}-py3-none-any.whl"
        if (
            not isinstance(wheel, dict)
            or wheel.get("filename") != filename
            or not isinstance(wheel.get("sha256"), str)
            or not re.fullmatch(r"[0-9a-f]{64}", wheel["sha256"])
        ):
            raise ValueError("Invalid runtime wheel name or SHA256.")
        extra = "" if name in {"dota2forge-renderer", "dota2forge-assets"} else "[stratz]"
        url = f"{repo}/releases/download/{tag}/{filename}#sha256={wheel['sha256']}"
        requirements.append(f"{name}{extra} @ {url}")
    return requirements


def pillow_constraints(host_python: Path) -> list[str]:
    """Preserve active host requirements, excluding the libraries being replaced."""
    result = subprocess.run(
        [
            str(host_python),
            "-I",
            "-c",
            """import importlib.metadata as metadata
import json
from pip._vendor.packaging.requirements import Requirement
excluded = {"dota2forge-core", "dota2forge-renderer", "dota2forge-assets",
            "dota2uid", "astrbot-plugin-dota2forge"}
constraints = set()
for distribution in metadata.distributions():
    name = distribution.metadata.get("Name", "").lower().replace("_", "-")
    if name in excluded:
        continue
    for value in distribution.requires or ():
        requirement = Requirement(value)
        if requirement.name.lower() != "pillow":
            continue
        if requirement.marker and not requirement.marker.evaluate({"extra": ""}):
            continue
        if requirement.url:
            raise ValueError("Host Pillow URL requirements need manual resolution")
        if requirement.specifier:
            constraints.add("pillow" + str(requirement.specifier))
print(json.dumps(sorted(constraints)))
""",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    constraints = json.loads(result.stdout)
    if not isinstance(constraints, list) or any(
        not isinstance(value, str) or not re.fullmatch(r"pillow[0-9A-Za-z.*<>=!~,+-]+", value)
        for value in constraints
    ):
        raise ValueError("Invalid host Pillow constraints.")
    return constraints


def install(host_python: Path, requirements: list[str]) -> int:
    version = subprocess.run(
        [
            str(host_python),
            "-I",
            "-c",
            "import json, sys; print(json.dumps(list(sys.version_info[:2])))",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    if tuple(json.loads(version.stdout)) < (3, 12):
        raise ValueError("The host environment requires Python 3.12 or newer.")
    pip = subprocess.run(
        [str(host_python), "-I", "-m", "pip", "--version"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if pip.returncode:
        bootstrap = subprocess.run(
            [str(host_python), "-I", "-m", "ensurepip", "--upgrade"], check=False
        )
        if bootstrap.returncode:
            return bootstrap.returncode
    constraints = pillow_constraints(host_python)
    with tempfile.TemporaryDirectory(prefix="dota2uid-runtime-") as temporary:
        constraint_file = Path(temporary) / "host-pillow.txt"
        constraint_file.write_text("\n".join(constraints) + "\n", encoding="utf-8")
        result = subprocess.run(
            [
                str(host_python),
                "-I",
                "-m",
                "pip",
                "install",
                "--upgrade",
                "--no-cache-dir",
                "--disable-pip-version-check",
                "--only-binary=:all:",
                "--constraint",
                str(constraint_file),
                *requirements,
            ],
            check=False,
        ).returncode
    if result:
        return result
    return subprocess.run([str(host_python), "-I", "-m", "pip", "check"], check=False).returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host-python", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        requirements = public_requirements(Path(__file__).resolve().parent)
        result = install(args.host_python, requirements)
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print(
            f"Runtime installation failed ({type(error).__name__}). "
            "Check manifests and host Python."
        )
        return 1
    if result == 0:
        print("Pinned public runtime installed. Cold-start the host to load the new libraries.")
    return result


if __name__ == "__main__":
    sys.exit(main())
