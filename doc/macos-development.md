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

Run the complete toy-project validation after changing parsers, media objects,
exporters, or TTS code. Add `--preview-init` to briefly open and initialize the
pygame preview window.

```sh
conda run --no-capture-output --name rplgen-macos python tools_scripts/validate_toy_macos.py --preview-init
```

Build an Apple Silicon application bundle with its own assets and static FFmpeg:

```sh
conda run --no-capture-output --name rplgen-macos python -m pip install -r requirements-macos-build.txt
conda run --no-capture-output --name rplgen-macos python tools_scripts/build_macos_app.py
conda run --no-capture-output --name rplgen-macos python tools_scripts/smoke_test_macos_app.py
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

### Stage 3: Project Workflow Validation

- Validated the complete `toy/LogFile.rgl` parser flow, Premiere XML export,
  MP4 export, and pygame preview initialization at a small test resolution.
- Added a native macOS system-TTS implementation based on `say`, because the
  current `pyttsx3` macOS driver is incompatible with modern PyObjC.
- Made file-backed media definitions own their `@/` root, and updated timeline
  storage for pandas 3 so numeric render data keeps its intended types.
- An unavailable cloud TTS engine now emits a warning and only disables that
  character, allowing local Beats and system voices to continue working.

### Stage 4: Native Application Bundle

- Added a reproducible PyInstaller builder for an Apple Silicon
  `RplGenStudio.app`, including `assets`, `intel`, an `.icns` application icon,
  and a static ARM64 FFmpeg binary.
- Added an app-bundle smoke test that verifies the ad-hoc code signature,
  bundled FFmpeg, and a GUI launch outside the source checkout.
- The initial bundle is approximately 259 MB and is written to
  `dist/macos/RplGenStudio.app`.

## Known Baseline Limitations

- `tkextrafont` is not installable from its public package on macOS because its
  build script invokes Linux `pacman`. It is not required for startup; the UI
  currently falls back to a system font.
- FFmpeg is a development dependency installed through Homebrew. A later
  packaging stage will bundle a native FFmpeg executable inside the `.app`.
- The current source still assumes it runs from the repository root. Resource
  path refactoring is the next implementation stage.
- Cloud TTS services still require valid provider credentials and an SDK version
  compatible with the service. The bundled sample's placeholder credentials are
  intentionally skipped during local validation.
- The application currently has an ad-hoc signature only. External release
  requires an Apple Developer certificate, notarization, and a DMG or ZIP
  distribution workflow.
