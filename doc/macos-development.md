# macOS Development

This baseline targets Apple Silicon Macs running macOS 15 with Python 3.11.

## Setup

```sh
conda create --name rplgen-macos python=3.11 pip
conda run --name rplgen-macos python -m pip install -r requirements-macos.txt
brew install ffmpeg
```

Run the application from the repository root so the current source layout can
find `assets` and `intel`:

```sh
conda run --no-capture-output --name rplgen-macos python gui.py
```

Check the installed environment before debugging an application issue:

```sh
conda run --no-capture-output --name rplgen-macos python tools_scripts/check_macos_environment.py
```

## Known Baseline Limitations

- `tkextrafont` is not installable from its public package on macOS because its
  build script invokes Linux `pacman`. It is not required for startup; the UI
  currently falls back to a system font.
- FFmpeg is a development dependency installed through Homebrew. A later
  packaging stage will bundle a native FFmpeg executable inside the `.app`.
- The current source still assumes it runs from the repository root. Resource
  path refactoring is the next implementation stage.
