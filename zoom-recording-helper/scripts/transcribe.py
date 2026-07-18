from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


class TranscriptionError(RuntimeError):
    pass


def _timestamp(seconds: float) -> str:
    millis = max(0, round(seconds * 1000))
    hours, remainder = divmod(millis, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, ms = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"


def write_transcripts(result: dict[str, Any], directory: Path) -> list[Path]:
    text = str(result.get("text", "")).strip()
    segments = result.get("segments") or []
    txt = directory / "transcript.txt"
    md = directory / "transcript.md"
    srt = directory / "transcript.srt"
    txt.write_text(text + "\n", encoding="utf-8")
    md.write_text("# 会议转写\n\n" + text + "\n", encoding="utf-8")
    srt_lines: list[str] = []
    for index, segment in enumerate(segments, 1):
        srt_lines.extend([
            str(index),
            f"{_timestamp(float(segment.get('start', 0)))} --> {_timestamp(float(segment.get('end', 0)))}",
            str(segment.get("text", "")).strip(),
            "",
        ])
    srt.write_text("\n".join(srt_lines), encoding="utf-8")
    return [txt, md, srt]


def transcribe_mlx(audio: Path, config: dict[str, Any]) -> list[Path]:
    try:
        import mlx_whisper
    except ImportError:
        raise TranscriptionError("未安装 mlx-whisper。运行: python3 -m pip install mlx-whisper") from None
    try:
        result = mlx_whisper.transcribe(str(audio), path_or_hf_repo=str(config["transcription_model"]))
    except Exception as exc:
        raise TranscriptionError(f"MLX Whisper 转写失败：{exc}") from None
    return write_transcripts(result, audio.parent)


def transcribe_cpp(audio: Path, config: dict[str, Any]) -> list[Path]:
    binary = shutil.which(str(config.get("whisper_cpp_binary", "whisper-cli")))
    model = Path(str(config.get("whisper_cpp_model", ""))).expanduser()
    if not binary:
        raise TranscriptionError("未找到 whisper.cpp 的 whisper-cli；请安装并在配置中填写 whisper_cpp_binary。")
    if not str(config.get("whisper_cpp_model", "")) or not model.exists():
        raise TranscriptionError("请在 config.yaml 的 whisper_cpp_model 填写本地模型路径。")
    prefix = audio.parent / "transcript"
    result = subprocess.run(
        [binary, "-m", str(model), "-f", str(audio), "-otxt", "-osrt", "-of", str(prefix)],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        raise TranscriptionError(f"whisper.cpp 转写失败：{result.stderr.strip()[-500:]}")
    txt = prefix.with_suffix(".txt")
    srt = prefix.with_suffix(".srt")
    text = txt.read_text(encoding="utf-8") if txt.exists() else ""
    md = prefix.with_suffix(".md")
    md.write_text("# 会议转写\n\n" + text.strip() + "\n", encoding="utf-8")
    return [txt, md, srt]


def transcribe(audio: Path, config: dict[str, Any]) -> list[Path]:
    backend = str(config.get("transcription_backend", "mlx-whisper")).lower()
    if backend in {"mlx", "mlx-whisper", "mlx_whisper"}:
        return transcribe_mlx(audio, config)
    if backend in {"whisper.cpp", "whisper-cpp", "cpp"}:
        return transcribe_cpp(audio, config)
    raise TranscriptionError(f"不支持的转写后端：{backend}")
