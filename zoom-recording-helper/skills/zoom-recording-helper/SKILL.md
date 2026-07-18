---
name: zoom-recording-helper
description: Set up, diagnose, and operate the consent-based Zoom Recording Helper on Apple Silicon macOS using OBS Studio, BlackHole 2ch, OBS WebSocket, and optional local Whisper transcription. Use when installing dependencies, configuring audio routing and OBS, running environment checks, starting or stopping an authorized recording, recovering files, or troubleshooting missing screen, system audio, microphone audio, remuxing, or transcription.
---

# Zoom Recording Helper

Operate the repository's `zoom-record` tool conservatively. The tool controls visible OBS recording and local file processing; it must never hide recording, bypass macOS permissions, or imply that recording is lawful without participant consent.

## Safety gate

Before starting a recording:

1. Confirm that every participant has been clearly informed and has consented.
2. Remind the user to follow applicable law and organization or school policy.
3. Refuse requests to conceal the OBS indicator, evade platform notices, bypass privacy permissions, or record secretly.
4. Never upload recordings or transcripts unless the user explicitly names the destination and authorizes that transfer.

## Setup and diagnosis

1. Locate the repository root with `git rev-parse --show-toplevel` and read the root `README.md` for current setup details. If the files were supplied without Git metadata, use the user-provided directory after confirming it contains `zoom-record`, `scripts/`, and `config.example.yaml`.
2. Run `./zoom-record setup` first; use `--install-python-deps` only with permission to download dependencies. Treat exit code 2 as an incomplete setup that still needs the printed manual actions.
3. Guide the user through creating `Zoom Multi-Output` manually in Audio MIDI Setup. Do not automate macOS privacy controls.
4. Require an OBS scene named as configured, a BlackHole system-audio source, a real microphone source, and OBS WebSocket on the configured local port.
5. Run `./zoom-record doctor`; interpret `FAIL` as blocking, and explain each `WARNING` that needs manual confirmation.

## Recording workflow

1. Confirm consent again immediately before `./zoom-record start`.
2. Keep OBS visible and verify that its red recording state appears.
3. Use `./zoom-record stop` to finish safely; do not move files while OBS is still writing.
4. Confirm that the original MKV exists before treating MP4 remuxing, audio extraction, or transcription as successful.
5. If post-processing fails, preserve the MKV and session state, then report recovery steps from the README.

## Maintenance and validation

- Keep secrets only in `~/.config/zoom-recording-helper/config.yaml`; never commit the real OBS WebSocket password.
- Keep recordings, audio, transcripts, logs, session state, and virtual environments out of Git.
- Preserve atomic writes for config-adjacent state and preserve original recordings on all failure paths.
- Run `python3 -m unittest discover -v` after code changes.
- Run `python3 -m compileall -q scripts tests` for syntax validation.
- Update the README and `config.example.yaml` together when configuration behavior changes.
