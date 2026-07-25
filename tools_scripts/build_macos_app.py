#!/usr/bin/env python3
"""Build an Apple Silicon RplGenStudio.app with bundled assets and FFmpeg."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUILD_ROOT = PROJECT_ROOT / 'build' / 'macos'
DIST_ROOT = PROJECT_ROOT / 'dist' / 'macos'
APP_NAME = 'RplGenStudio'


def run(command: list[str]) -> None:
    print('+', ' '.join(command))
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def create_icon() -> Path:
    source = PROJECT_ROOT / 'assets' / 'icon.png'
    iconset = BUILD_ROOT / 'RplGenStudio.iconset'
    icon = BUILD_ROOT / 'RplGenStudio.icns'
    if iconset.exists():
        shutil.rmtree(iconset)
    iconset.mkdir(parents=True)
    sizes = (16, 32, 128, 256, 512)
    for size in sizes:
        run(['sips', '-z', str(size), str(size), str(source), '--out', str(iconset / f'icon_{size}x{size}.png')])
        double_size = size * 2
        run([
            'sips', '-z', str(double_size), str(double_size), str(source),
            '--out', str(iconset / f'icon_{size}x{size}@2x.png'),
        ])
    run(['iconutil', '--convert', 'icns', '--output', str(icon), str(iconset)])
    return icon


def stage_ffmpeg() -> Path:
    try:
        import imageio_ffmpeg
    except ModuleNotFoundError as error:
        raise RuntimeError('Install requirements-macos-build.txt before packaging.') from error

    source = Path(imageio_ffmpeg.get_ffmpeg_exe())
    if not source.is_file():
        raise RuntimeError(f'Bundled FFmpeg was not found: {source}')
    destination = BUILD_ROOT / 'ffmpeg'
    shutil.copy2(source, destination)
    destination.chmod(destination.stat().st_mode | 0o111)
    return destination


def main() -> int:
    if sys.platform != 'darwin':
        raise RuntimeError('This builder must run on macOS.')
    if not BUILD_ROOT.exists():
        BUILD_ROOT.mkdir(parents=True)
    if DIST_ROOT.exists():
        shutil.rmtree(DIST_ROOT)
    DIST_ROOT.mkdir(parents=True)

    icon = create_icon()
    ffmpeg = stage_ffmpeg()
    run([
        sys.executable, '-m', 'PyInstaller',
        '--noconfirm', '--clean', '--windowed',
        '--name', APP_NAME,
        '--distpath', str(DIST_ROOT),
        '--workpath', str(BUILD_ROOT / 'pyinstaller'),
        '--specpath', str(BUILD_ROOT / 'spec'),
        '--target-arch', 'arm64',
        '--osx-bundle-identifier', 'io.github.danddxuanx.rplgenstudio',
        '--icon', str(icon),
        '--add-data', f'{PROJECT_ROOT / "assets"}:assets',
        '--add-data', f'{PROJECT_ROOT / "intel"}:intel',
        '--add-binary', f'{ffmpeg}:bin',
        '--collect-all', 'azure',
        '--collect-all', 'chlorophyll',
        '--collect-all', 'emoji',
        '--hidden-import', 'nls',
        '--hidden-import', 'pinyin',
        '--hidden-import', 'websocket',
        str(PROJECT_ROOT / 'gui.py'),
    ])
    app_path = DIST_ROOT / f'{APP_NAME}.app'
    if not app_path.is_dir():
        raise RuntimeError(f'PyInstaller did not create {app_path}')
    print(f'Created {app_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
