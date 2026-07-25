#!/usr/bin/env python
# coding: utf-8
"""Run Pygame output work in a dedicated macOS process."""

from __future__ import annotations

import sys
import traceback
from pathlib import Path


class QueueWriter:
    """Forward worker output to the GUI process without sharing Tk objects."""

    def __init__(self, message_queue, log_path: str) -> None:
        self.message_queue = message_queue
        self.log_file = Path(log_path).open('a', encoding='utf-8')

    def write(self, text: str) -> int:
        if text:
            self.log_file.write(text)
            self.log_file.flush()
            self.message_queue.put(('log', text))
        return len(text)

    def flush(self) -> None:
        self.log_file.flush()

    def close(self) -> None:
        self.log_file.close()


def run_macos_output(
    output_type: str,
    config_struct: dict,
    media_struct: dict,
    chartab_struct: dict,
    log_struct: dict,
    media_root: str,
    output_path: str,
    key: str,
    title: str,
    message_queue,
    log_path: str,
) -> None:
    """Rebuild project objects and run the Pygame pipeline in the child main thread."""
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    writer = QueueWriter(message_queue, log_path)
    sys.stdout = writer
    sys.stderr = writer
    try:
        print(f'[macOS worker] Starting {output_type}.')
        import pygame

        from .FilePaths import Filepath
        from .Medias import MediaObj
        from .OutputType import ExportVideo, ExportXML, PreviewDisplay
        from .ProjConfig import Config
        from .ScriptParser import CharTable, MediaDef, RplGenLog

        pygame.init()
        Filepath.Mediapath = media_root.rstrip('/') + '/'
        config = Config(dict_input=config_struct)
        config.execute()
        mediadef = MediaDef(dict_input=media_struct)
        chartab = CharTable(dict_input=chartab_struct)
        rplgenlog = RplGenLog(dict_input=log_struct)
        mediadef.execute()
        chartab.execute()
        rplgenlog.execute(media_define=mediadef, char_table=chartab, config=config)

        if output_type == 'display':
            result = PreviewDisplay(rplgenlog=rplgenlog, config=config, title=title).main()
        elif output_type == 'recode':
            result = ExportVideo(
                rplgenlog=rplgenlog,
                config=config,
                output_path=output_path,
                key=key,
            ).main()
        elif output_type == 'exportpr':
            MediaObj.export_xml = True
            MediaObj.output_path = output_path + f'{key}/'
            result = ExportXML(
                rplgenlog=rplgenlog,
                config=config,
                output_path=output_path,
                key=key,
            ).main()
        else:
            raise ValueError(f'Unsupported macOS output type: {output_type}')
        print(f'[macOS worker] Finished with status {result}.')
        message_queue.put(('complete', result))
    except Exception:
        traceback.print_exc()
        message_queue.put(('complete', 1))
    finally:
        try:
            pygame.quit()
        except UnboundLocalError:
            pass
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        writer.close()
