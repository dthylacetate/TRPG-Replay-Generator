#!/usr/bin/env python
# coding: utf-8
"""Platform-specific paths and executable discovery."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def is_macos() -> bool:
    return sys.platform == 'darwin'


def is_windows() -> bool:
    return sys.platform.startswith('win')


def application_root() -> Path:
    """Return the directory containing bundled or source application assets."""
    if getattr(sys, 'frozen', False):
        return Path(getattr(sys, '_MEIPASS', Path(sys.executable).parent)).resolve()
    return Path(__file__).resolve().parent.parent


def resource_path(*parts: str) -> Path:
    return application_root().joinpath(*parts)


def ffmpeg_executable() -> str:
    """Locate FFmpeg for development, a bundled app, or an explicit override."""
    configured = os.environ.get('RPLGEN_FFMPEG')
    if configured:
        candidate = Path(configured).expanduser()
        if candidate.is_file():
            return str(candidate)
        raise FileNotFoundError(f'RPLGEN_FFMPEG does not exist: {candidate}')

    executable_name = 'ffmpeg.exe' if is_windows() else 'ffmpeg'
    for candidate in (
        resource_path('bin', executable_name),
        resource_path(executable_name),
    ):
        if candidate.is_file():
            return str(candidate)

    on_path = shutil.which(executable_name)
    if on_path is None and is_windows():
        on_path = shutil.which('ffmpeg')
    if on_path:
        return on_path
    raise FileNotFoundError(
        'FFmpeg was not found. Install it on PATH or set RPLGEN_FFMPEG.'
    )
