from __future__ import annotations

import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from .audio_device import current_output_device, set_output_device
from .common import get_logger
from .config import ConfigError, load_config
from .doctor import collect_checks, critical_failures, print_checks
from .file_manager import session_directory, write_json
from .obs_client import OBSClientError, wait_for_obs
from .session import SessionError, load_session, save_session


def _open_app(name: str) -> bool:
    return subprocess.run(["open", "-a", name], capture_output=True, check=False).returncode == 0


def main() -> int:
    logger = get_logger("start")
    try:
        config = load_config()
        existing = load_session()
    except (ConfigError, SessionError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        logger.error("start blocked: %s", exc)
        return 1
    if existing:
        print(f"FAIL: 已有活动会话：{existing.get('session_directory', '未知目录')}。请先运行 ./zoom-record stop", file=sys.stderr)
        return 1

    checks = collect_checks(config)
    failures = critical_failures(checks)
    if failures:
        print_checks(checks)
        print("\nFAIL: 关键环境检查未通过；请修复以上 FAIL 后重试。", file=sys.stderr)
        return 1

    previous_output = current_output_device()
    target_output = str(config["multi_output_device"])
    if previous_output != target_output:
        ok, detail = set_output_device(target_output)
        if not ok:
            print(f"FAIL: {detail}", file=sys.stderr)
            logger.error("audio switch failed: %s", detail)
            return 1
        logger.info("audio output switched from=%s to=%s", previous_output or "unknown", target_output)

    now = datetime.now().astimezone()
    output_root = Path(str(config["recording_directory"])).expanduser()
    session_dir = session_directory(output_root, now)
    suffix = 1
    while session_dir.exists():
        session_dir = session_dir.with_name(f"{session_dir.name}_{suffix}")
        suffix += 1
    session_dir.mkdir(parents=True)
    metadata_path = session_dir / "metadata.json"
    metadata = {
        "start_time": now.isoformat(), "end_time": None, "status": "recording",
        "obs_scene": config["obs_scene_name"], "system_audio_device": config["system_audio_device"],
        "microphone_device": config["microphone_device"], "output_file": None,
    }
    write_json(metadata_path, metadata)

    if config.get("auto_open_obs", True):
        if not _open_app("OBS"):
            metadata["status"] = "failed_to_start"
            write_json(metadata_path, metadata)
            if previous_output and previous_output != target_output:
                set_output_device(previous_output)
            print("FAIL: 无法打开 OBS Studio。请确认已安装。", file=sys.stderr)
            return 1
    if config.get("auto_open_zoom", True):
        if not _open_app("zoom.us"):
            logger.warning("Zoom could not be opened")
            print("WARNING: 无法自动打开 Zoom，请手动打开。")

    print("正在等待 OBS WebSocket（最长 30 秒）…")
    try:
        obs = wait_for_obs(config, timeout=30)
        active, _ = obs.get_record_status()
        if active:
            print("FAIL: OBS 已在录制。为避免接管未知录制，本次启动已取消。", file=sys.stderr)
            return 1
        obs.set_scene(str(config["obs_scene_name"]))
        obs.set_record_directory(session_dir)
        obs.start_record()
        time.sleep(1)
        active, provisional_path = obs.get_record_status()
        if not active:
            raise OBSClientError("OBS 未报告活动录制状态。")
    except OBSClientError as exc:
        metadata["status"] = "failed_to_start"
        write_json(metadata_path, metadata)
        if previous_output and previous_output != target_output:
            set_output_device(previous_output)
        print(f"FAIL: {exc}", file=sys.stderr)
        logger.error("OBS start failed: %s", exc)
        return 1

    session = {
        "start_time": now.isoformat(), "session_directory": str(session_dir),
        "metadata_path": str(metadata_path), "previous_output_device": previous_output,
        "target_output_device": target_output, "provisional_output_path": provisional_path,
    }
    save_session(session)
    logger.info("recording started directory=%s", session_dir)
    print("\n🔴 Recording started — OBS 正在明显录制，请确保所有参会者已同意。")
    print(f"System audio: {config['system_audio_device']}")
    print(f"Microphone: {config['microphone_device']}")
    print(f"Output directory: {session_dir}")
    print("结束时运行: ./zoom-record stop")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
