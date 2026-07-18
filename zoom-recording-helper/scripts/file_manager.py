from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


MEDIA_EXTENSIONS = {".mkv", ".mp4", ".mov", ".flv", ".ts"}


def session_directory(root: Path, now: datetime | None = None) -> Path:
    now = now or datetime.now().astimezone()
    return root / f"{now:%Y-%m-%d_%H-%M}_Zoom"


def meeting_filename(start_time: datetime, suffix: str) -> str:
    suffix = suffix if suffix.startswith(".") else f".{suffix}"
    return f"{start_time:%Y-%m-%d_%H-%M}_Zoom_Meeting{suffix.lower()}"


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def find_newest_recording(directory: Path, since_timestamp: float = 0) -> Path | None:
    candidates = [
        path for path in directory.glob("*")
        if path.is_file() and path.suffix.lower() in MEDIA_EXTENSIONS and path.stat().st_mtime >= since_timestamp - 5
    ]
    return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None


def organize_recording(source: Path, destination_dir: Path, start_time: datetime) -> Path:
    source = source.expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(f"OBS 输出文件不存在：{source}")
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / meeting_filename(start_time, source.suffix)
    if source != destination:
        if destination.exists():
            destination = destination.with_stem(f"{destination.stem}_{int(datetime.now().timestamp())}")
        shutil.move(str(source), str(destination))
    return destination


def run_ffmpeg(args: list[str], logger) -> tuple[bool, str]:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return False, "未安装 ffmpeg；原始录制已安全保留。安装: brew install ffmpeg"
    command = [ffmpeg, "-hide_banner", "-nostdin", "-y", *args]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode == 0:
        logger.info("ffmpeg success output=%s", args[-1])
        return True, ""
    detail = "\n".join(result.stderr.splitlines()[-8:])
    logger.error("ffmpeg failed code=%s detail=%s", result.returncode, detail)
    return False, detail or "ffmpeg 执行失败"


def remux_to_mp4(source: Path, logger) -> tuple[Path | None, str]:
    if source.suffix.lower() != ".mkv":
        return (source if source.suffix.lower() == ".mp4" else None), ""
    target = source.with_suffix(".mp4")
    ok, detail = run_ffmpeg(["-i", str(source), "-map", "0", "-c", "copy", str(target)], logger)
    return (target if ok else None), detail


def extract_audio(source: Path, separate_tracks: bool, logger) -> tuple[list[Path], list[str]]:
    outputs: list[Path] = []
    errors: list[str] = []
    mappings = [(0, "mixed_audio.m4a")]
    if separate_tracks:
        mappings = [(0, "mixed_audio.m4a"), (1, "system_audio.m4a"), (2, "microphone_audio.m4a")]
    for index, name in mappings:
        target = source.parent / name
        ok, detail = run_ffmpeg(
            ["-i", str(source), "-map", f"0:a:{index}", "-vn", "-c:a", "aac", "-b:a", "192k", str(target)], logger
        )
        if ok:
            outputs.append(target)
        else:
            errors.append(f"{name}: {detail}")
    return outputs, errors
