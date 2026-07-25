#!/usr/bin/env python3
"""Validate the macOS Pygame output worker against a project file."""

from __future__ import annotations

import argparse
import multiprocessing
import os
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from core.GUI_FileManager import RplGenProJect
from core.MacOutputWorker import run_macos_output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', required=True, type=Path)
    args = parser.parse_args()
    project_file = args.project.resolve()
    project = RplGenProJect(json_input=str(project_file))
    name, log = next(iter(project.logfile.items()))
    queue = multiprocessing.Queue()
    with tempfile.TemporaryDirectory(prefix='rplgen-macos-worker-') as directory:
        output_path = f'{directory}/'
        log_path = f'{directory}/worker.log'
        worker = multiprocessing.Process(
            target=run_macos_output,
            args=(
                'recode',
                project.config.get_struct(),
                project.mediadef.struct,
                project.chartab.struct,
                log.struct,
                f'{project_file.parent}/',
                output_path,
                name,
                name,
                queue,
                log_path,
            ),
        )
        worker.start()
        status = None
        while worker.is_alive():
            try:
                event, value = queue.get(timeout=1)
                if event == 'complete':
                    status = value
            except Exception:
                pass
        worker.join()
        while not queue.empty():
            event, value = queue.get()
            if event == 'complete':
                status = value
        video_path = Path(directory) / f'{name}.video.mp4'
        if worker.exitcode != 0 or status != 0 or not video_path.is_file() or video_path.stat().st_size == 0:
            print(Path(log_path).read_text(encoding='utf-8'))
            raise RuntimeError(f'Worker export failed: exit={worker.exitcode}, status={status}')
        print(f'OK worker export: {video_path.stat().st_size} bytes')
    return 0


if __name__ == '__main__':
    multiprocessing.freeze_support()
    raise SystemExit(main())
