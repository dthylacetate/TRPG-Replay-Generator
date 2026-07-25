#!/usr/bin/env python3
"""Validate macOS workflows against the bundled toy project."""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

import pygame

from core.Medias import MediaObj
from core.OutputType import ExportVideo, ExportXML, PreviewDisplay
from core.ProjConfig import Config, preference
from core.ScriptParser import CharTable, MediaDef, RplGenLog
from core.SpeechSynth import SpeechSynthesizer
from core.TTSengines import System_TTS_engine


TOY_ROOT = PROJECT_ROOT / 'toy'


def make_config() -> Config:
    config = Config()
    config.Width = 640
    config.Height = 360
    config.frame_rate = 10
    config.execute()
    return config


def load_project(log_name: str, export_xml: bool, output_path: Path):
    MediaObj.export_xml = export_xml
    MediaObj.output_path = f'{output_path}/'
    media = MediaDef(file_input=str(TOY_ROOT / 'MediaObject.txt'))
    media.execute()
    chartab = CharTable(file_input=str(TOY_ROOT / 'CharactorTable.tsv'))
    log = RplGenLog(file_input=str(TOY_ROOT / log_name))
    return media, chartab, log


def check_system_tts(output_path: Path) -> None:
    audio_path = output_path / 'system-tts.wav'
    engine = System_TTS_engine(name='macos-check')
    if not engine.voice_list:
        raise RuntimeError('macOS did not report any system TTS voices.')
    engine.start('macOS text to speech check.', str(audio_path))
    if not audio_path.is_file() or audio_path.stat().st_size <= 44:
        raise RuntimeError('System TTS did not create a usable WAV file.')
    print('OK system TTS')


def check_full_script(config: Config, output_path: Path) -> None:
    media, chartab, log = load_project('LogFile.rgl', False, output_path)
    log.execute(media, chartab, config)
    if log.break_point.max() <= 0:
        raise RuntimeError('The full toy script did not create a timeline.')
    print(f'OK full script ({log.break_point.max()} frames)')


def synthesize_short_script(config: Config, output_path: Path, export_xml: bool):
    media, chartab, log = load_project('LogFile2.rgl', export_xml, output_path)
    synthesizer = SpeechSynthesizer(log, chartab, media, f'{output_path}/', config)
    if synthesizer.execute() != 0:
        raise RuntimeError('Toy beats synthesis did not complete.')
    log.execute(media, chartab, config)
    return log


def check_xml_export(config: Config, output_path: Path) -> None:
    log = synthesize_short_script(config, output_path, export_xml=True)
    exporter = ExportXML(log, config, f'{output_path}/', 'toy')
    if exporter.main() != 0:
        raise RuntimeError('Toy XML export failed.')
    xml_path = output_path / 'toy.prproj.xml'
    if not xml_path.is_file() or xml_path.stat().st_size == 0:
        raise RuntimeError('Toy XML export did not create a project file.')
    print('OK XML export')


def check_video_export(config: Config, output_path: Path) -> None:
    log = synthesize_short_script(config, output_path, export_xml=False)
    original_hwaccels = preference.hwaccels
    preference.hwaccels = False
    try:
        exporter = ExportVideo(log, config, f'{output_path}/', 'toy')
        if exporter.main() != 0:
            raise RuntimeError('Toy MP4 export failed.')
    finally:
        preference.hwaccels = original_hwaccels
    video_path = output_path / 'toy.video.mp4'
    if not video_path.is_file() or video_path.stat().st_size == 0:
        raise RuntimeError('Toy MP4 export did not create a video file.')
    print('OK MP4 export')


def check_preview_initialization(config: Config, output_path: Path) -> None:
    # ExportVideo closes pygame. The GUI initializes it again before reading
    # media definitions that create pygame font objects.
    pygame.init()
    try:
        media, chartab, log = load_project('LogFile.rgl', False, output_path)
        log.execute(media, chartab, config)
        preview = PreviewDisplay(log, config, title='macOS validation')
        if preview.display_init() != 0:
            raise RuntimeError('Preview display initialization failed.')
    finally:
        pygame.quit()
    print('OK preview initialization')


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--preview-init', action='store_true')
    args = parser.parse_args()

    config = make_config()
    with tempfile.TemporaryDirectory(prefix='rplgen-toy-macos-') as directory:
        output_path = Path(directory)
        check_system_tts(output_path)
        check_full_script(config, output_path)
        check_xml_export(config, output_path)
        check_video_export(config, output_path)
        if args.preview_init:
            check_preview_initialization(config, output_path)
    MediaObj.export_xml = False
    print('macOS toy-project validation passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
