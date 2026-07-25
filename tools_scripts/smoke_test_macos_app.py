#!/usr/bin/env python3
"""Check a built macOS app bundle without relying on the source checkout."""

from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_APP = PROJECT_ROOT / 'dist' / 'macos' / 'RplGenStudio.app'


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--app', type=Path, default=DEFAULT_APP)
    args = parser.parse_args()
    app_path = args.app.resolve()
    executable = app_path / 'Contents' / 'MacOS' / 'RplGenStudio'
    ffmpeg = app_path / 'Contents' / 'Frameworks' / 'bin' / 'ffmpeg'
    if not executable.is_file() or not ffmpeg.is_file():
        raise RuntimeError(f'Incomplete application bundle: {app_path}')

    subprocess.run(['codesign', '--verify', '--deep', '--strict', str(app_path)], check=True)
    version = subprocess.run([str(ffmpeg), '-version'], check=True, capture_output=True, text=True)
    print(version.stdout.splitlines()[0])

    process = subprocess.Popen([str(executable)], cwd='/')
    time.sleep(8)
    if process.poll() is not None:
        raise RuntimeError(f'Bundled app exited early with status {process.returncode}.')
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)
    print('macOS app smoke test passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
