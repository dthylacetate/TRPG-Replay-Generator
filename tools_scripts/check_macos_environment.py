#!/usr/bin/env python3
"""Check the source-run prerequisites for the Apple Silicon macOS port."""

from __future__ import annotations

import importlib
import platform
import shutil
import subprocess
import sys


REQUIRED_PACKAGES = (
    "pygame",
    "numpy",
    "pandas",
    "PIL",
    "ffmpeg",
    "pydub",
    "openpyxl",
    "azure.cognitiveservices.speech",
    "ttkbootstrap",
    "chlorophyll",
    "pyttsx3",
    "websocket",
    "pinyin",
    "emoji",
    "nls",
)


def main() -> int:
    failures: list[str] = []
    print(f"Platform: {platform.system()} {platform.mac_ver()[0]} ({platform.machine()})")
    print(f"Python: {platform.python_version()}")

    if platform.system() != "Darwin":
        failures.append("This check is intended for macOS.")
    if platform.machine() != "arm64":
        failures.append("This baseline targets Apple Silicon (arm64).")
    if sys.version_info[:2] != (3, 11):
        failures.append("Use the project's Python 3.11 development environment.")

    for package in REQUIRED_PACKAGES:
        try:
            importlib.import_module(package)
            print(f"OK package: {package}")
        except Exception as error:
            failures.append(f"Missing or unusable package {package}: {error}")

    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path is None:
        failures.append("ffmpeg is not available on PATH.")
    else:
        version = subprocess.run(
            [ffmpeg_path, "-version"],
            check=False,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        print(f"OK ffmpeg: {version[0] if version else ffmpeg_path}")

    if failures:
        print("\nEnvironment check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("\nmacOS development environment is ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
