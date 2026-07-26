#!/usr/bin/env python3
"""Package the built Apple Silicon app as a distributable ZIP archive."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIST_ROOT = PROJECT_ROOT / 'dist' / 'macos'
DEFAULT_APP = DIST_ROOT / 'RplGenStudio.app'
DEFAULT_ARCHIVE = DIST_ROOT / 'RplGenStudio-macos-arm64.zip'


def run(command: list[str]) -> None:
    print('+', ' '.join(command))
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as archive:
        for block in iter(lambda: archive.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--app', type=Path, default=DEFAULT_APP)
    parser.add_argument('--output', type=Path, default=DEFAULT_ARCHIVE)
    args = parser.parse_args()

    if sys.platform != 'darwin':
        raise RuntimeError('This packager must run on macOS.')
    app_path = args.app.resolve()
    archive_path = args.output.resolve()
    if not app_path.is_dir():
        raise RuntimeError(f'Build the app before packaging it: {app_path}')
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    if archive_path.exists():
        archive_path.unlink()

    run(['codesign', '--verify', '--deep', '--strict', str(app_path)])
    run(['ditto', '-c', '-k', '--keepParent', str(app_path), str(archive_path)])
    with zipfile.ZipFile(archive_path) as archive:
        bad_file = archive.testzip()
    if bad_file is not None:
        raise RuntimeError(f'ZIP integrity check failed at {bad_file}')

    checksum_path = archive_path.with_suffix(archive_path.suffix + '.sha256')
    checksum_path.write_text(
        f'{checksum(archive_path)}  {archive_path.name}\n',
        encoding='utf-8',
    )
    print(f'Created {archive_path}')
    print(f'Created {checksum_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
