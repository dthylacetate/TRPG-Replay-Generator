#!/usr/bin/env python3
"""Run macOS media-path smoke tests without opening the application UI."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from core.OutputType import ExportVideo
from core.Platform import ffmpeg_executable
from core.ProjConfig import preference
from core.Utils import convert_audio


def check_audio_conversion(work_dir: Path) -> None:
    source = work_dir / 'source.mp3'
    output = work_dir / 'converted.wav'
    subprocess.run(
        [
            ffmpeg_executable(),
            '-f', 'lavfi',
            '-i', 'sine=frequency=440:duration=0.1',
            '-q:a', '9',
            '-y', str(source),
            '-loglevel', 'error',
        ],
        check=True,
    )
    success, result = convert_audio('wav', str(source), str(output))
    if not success or not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError(f'Audio conversion failed: {result}')
    print('OK audio conversion')


def check_video_export(work_dir: Path) -> None:
    output = work_dir / 'frame.mp4'
    exporter = ExportVideo.__new__(ExportVideo)
    exporter.config = SimpleNamespace(Width=2, Height=2, frame_rate=1)
    original_hwaccels = preference.hwaccels
    preference.hwaccels = False
    try:
        process = exporter.ffmpeg_output(str(output), None)
        process.stdin.write(bytes((0, 0, 0)) * 4)
        process.stdin.close()
        return_code = process.wait(timeout=30)
    finally:
        preference.hwaccels = original_hwaccels
    if return_code != 0 or not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError('Video export did not create a valid MP4 file.')
    print('OK video export')


def main() -> int:
    print(f'FFmpeg: {ffmpeg_executable()}')
    with tempfile.TemporaryDirectory(prefix='rplgen-macos-') as directory:
        work_dir = Path(directory)
        check_audio_conversion(work_dir)
        check_video_export(work_dir)
    print('macOS media smoke test passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
