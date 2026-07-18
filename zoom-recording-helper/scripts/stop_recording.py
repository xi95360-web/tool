from __future__ import annotations

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from .audio_device import set_output_device
from .common import get_logger
from .config import ConfigError, load_config
from .file_manager import extract_audio, find_newest_recording, organize_recording, read_json, remux_to_mp4, write_json
from .obs_client import OBSClientError, wait_for_obs
from .session import SessionError, clear_session, load_session
from .transcribe import TranscriptionError, transcribe


def main() -> int:
    logger = get_logger("stop")
    try:
        config = load_config()
        session = load_session()
    except (ConfigError, SessionError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if not session:
        print("FAIL: 没有活动会话。请先运行 ./zoom-record start", file=sys.stderr)
        return 1

    session_dir = Path(session["session_directory"])
    metadata_path = Path(session["metadata_path"])
    start_time = datetime.fromisoformat(session["start_time"])
    output_path: str | None = None
    try:
        obs = wait_for_obs(config, timeout=10)
        active, status_path = obs.get_record_status()
        if active:
            output_path = obs.stop_record()
            logger.info("OBS stop requested output=%s", output_path or status_path)
            time.sleep(2)
        else:
            output_path = status_path or session.get("provisional_output_path")
            print("WARNING: OBS 已不在录制，将尝试整理最近的输出文件。")
    except OBSClientError as exc:
        print(f"FAIL: 无法安全停止 OBS：{exc}", file=sys.stderr)
        logger.error("OBS stop failed: %s", exc)
        return 1

    source = Path(output_path).expanduser() if output_path else None
    if not source or not source.exists():
        source = find_newest_recording(session_dir, start_time.timestamp())
    if not source:
        print(f"FAIL: OBS 已停止，但未找到输出文件。会话状态已保留，便于再次运行 stop。请检查：{session_dir}", file=sys.stderr)
        logger.error("no recording output found directory=%s", session_dir)
        return 1

    try:
        organized = organize_recording(source, session_dir, start_time)
    except (OSError, FileNotFoundError) as exc:
        print(f"FAIL: 无法整理录制文件：{exc}", file=sys.stderr)
        return 1

    final_media = organized
    warnings: list[str] = []
    mp4, remux_error = remux_to_mp4(organized, logger)
    if mp4:
        final_media = mp4
    elif remux_error:
        warnings.append(f"MP4 转封装失败：{remux_error}")

    audio_files: list[Path] = []
    if config.get("extract_audio", True):
        audio_files, audio_errors = extract_audio(final_media, bool(config.get("audio_tracks_separate", False)), logger)
        warnings.extend(f"音频提取失败：{error}" for error in audio_errors)

    transcript_files: list[Path] = []
    if config.get("transcribe", False):
        transcription_input = audio_files[0] if audio_files else final_media
        try:
            transcript_files = transcribe(transcription_input, config)
            logger.info("transcription completed files=%s", [str(p) for p in transcript_files])
        except TranscriptionError as exc:
            warnings.append(str(exc))
            logger.error("transcription failed: %s", exc)

    previous = session.get("previous_output_device")
    if previous and previous != session.get("target_output_device"):
        ok, detail = set_output_device(str(previous))
        if not ok:
            warnings.append(f"未能恢复音频输出：{detail}")
            logger.warning("audio restore failed: %s", detail)
    end_time = datetime.now().astimezone()
    try:
        metadata = read_json(metadata_path)
    except Exception:
        metadata = {}
    metadata.update({
        "end_time": end_time.isoformat(), "status": "completed",
        "duration_seconds": max(0, round((end_time - start_time).total_seconds())),
        "output_file": str(final_media), "original_recording": str(organized),
        "audio_files": [str(p) for p in audio_files],
        "transcript_files": [str(p) for p in transcript_files],
        "warnings": warnings,
    })
    write_json(metadata_path, metadata)
    clear_session()
    subprocess.run(["open", str(session_dir)], capture_output=True, check=False)
    logger.info("recording completed output=%s", final_media)
    print("\n⏹ Recording stopped and files organized.")
    print(f"Final file: {final_media}")
    print(f"Folder: {session_dir}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
