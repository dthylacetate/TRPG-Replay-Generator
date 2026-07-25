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

Run the media smoke test after changing FFmpeg or platform code:

```sh
conda run --no-capture-output --name rplgen-macos python tools_scripts/smoke_test_macos.py
```

## Port Progress

### Stage 1: Development Baseline

- Added a Python 3.11 Apple Silicon dependency set and environment checker.
- Installed Homebrew FFmpeg for source development.
- Confirmed the source GUI can start on macOS.

### Stage 2: Platform Runtime

- Added centralized application-root and FFmpeg discovery, with an optional
  `RPLGEN_FFMPEG` override for development and future bundled builds.
- Fixed POSIX audio conversion to pass FFmpeg arguments without a shell.
- Routed MP4 export through the same FFmpeg discovery and selected
  `h264_videotoolbox` instead of NVIDIA encoding when macOS acceleration is enabled.
- Replaced the unavailable `tkextrafont` path with `PingFang SC` and `Menlo` on
  macOS, and removed the incorrect Retina `2.0` window multiplier.

## Known Baseline Limitations

- `tkextrafont` is not installable from its public package on macOS because its
  build script invokes Linux `pacman`. It is not required for startup; the UI
  currently falls back to a system font.
- FFmpeg is a development dependency installed through Homebrew. A later
  packaging stage will bundle a native FFmpeg executable inside the `.app`.
- The current source still assumes it runs from the repository root. Resource
  path refactoring is the next implementation stage.
