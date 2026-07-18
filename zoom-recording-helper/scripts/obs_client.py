from __future__ import annotations

import socket
import time
from pathlib import Path
from typing import Any


class OBSClientError(RuntimeError):
    pass


def tcp_reachable(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


class OBSClient:
    def __init__(self, config: dict[str, Any], timeout: int = 5):
        try:
            import obsws_python as obs
        except ImportError:
            raise OBSClientError("缺少 obsws-python。请运行: python3 -m pip install -r requirements.txt") from None
        try:
            self.client = obs.ReqClient(
                host=str(config["obs_websocket_host"]),
                port=int(config["obs_websocket_port"]),
                password=str(config.get("obs_websocket_password", "")),
                timeout=timeout,
            )
        except Exception as exc:
            raise OBSClientError(_friendly_obs_error(exc)) from None

    def set_scene(self, scene_name: str) -> None:
        try:
            self.client.set_current_program_scene(scene_name)
        except Exception as exc:
            raise OBSClientError(f"无法切换到 OBS 场景“{scene_name}”：{exc}") from None

    def set_record_directory(self, directory: Path) -> None:
        try:
            self.client.set_record_directory(str(directory))
        except Exception as exc:
            raise OBSClientError(f"无法设置 OBS 录制目录：{exc}") from None

    def get_record_status(self) -> tuple[bool, str | None]:
        try:
            status = self.client.get_record_status()
            return bool(status.output_active), getattr(status, "output_path", None)
        except Exception as exc:
            raise OBSClientError(f"无法读取 OBS 录制状态：{exc}") from None

    def start_record(self) -> None:
        try:
            self.client.start_record()
        except Exception as exc:
            raise OBSClientError(f"OBS 无法开始录制：{exc}") from None

    def stop_record(self) -> str | None:
        try:
            response = self.client.stop_record()
            return getattr(response, "output_path", None)
        except Exception as exc:
            raise OBSClientError(f"OBS 无法停止录制：{exc}") from None


def wait_for_obs(config: dict[str, Any], timeout: int = 30) -> OBSClient:
    deadline = time.monotonic() + timeout
    last_error = ""
    while time.monotonic() < deadline:
        try:
            return OBSClient(config)
        except OBSClientError as exc:
            last_error = str(exc)
            time.sleep(1)
    raise OBSClientError(f"等待 OBS WebSocket 超时。{last_error}")


def _friendly_obs_error(exc: Exception) -> str:
    text = str(exc)
    if "authentication" in text.lower() or "password" in text.lower():
        return "OBS WebSocket 认证失败。请检查 config.yaml 中的密码。"
    return f"无法连接 OBS WebSocket：{text or type(exc).__name__}"
