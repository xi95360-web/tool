from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from .audio_device import device_exists
from .config import CONFIG_FILE, DEFAULT_CONFIG, write_default_config
from .doctor import collect_checks, print_checks


MULTI_OUTPUT_GUIDE = """
创建“Zoom Multi-Output”多输出设备：
  1. 在“音频 MIDI 设置”窗口点击左下角“+”。
  2. 选择“创建多输出设备”。
  3. 勾选实际耳机或“MacBook 扬声器”。
  4. 勾选“BlackHole 2ch”。
  5. 将实际播放设备设为主设备（列表最上方/时钟源）。
  6. 为 BlackHole 2ch 开启“漂移校正”。
  7. 双击设备名称，重命名为“Zoom Multi-Output”。
完成后运行: ./zoom-record doctor
"""

OBS_GUIDE = """
OBS 手动配置：
  1. 打开 OBS，创建场景“Zoom Recording”。
  2. 添加“macOS 屏幕采集”或“窗口采集”，选择 Zoom。
  3. 添加“音频输入采集”，设备选 BlackHole 2ch。
  4. 再添加“音频输入采集”，设备选你的麦克风。
  5. 打开 工具 → WebSocket Server Settings，启用服务器，端口 4455。
  6. 若设置密码，将同一密码写入 config.yaml；密码不会写入日志。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="首次配置 Zoom Recording Helper")
    parser.add_argument("--install-python-deps", action="store_true", help="创建 .venv 并安装 Python 依赖")
    parser.add_argument("--no-open", action="store_true", help="不自动打开应用或设置页面")
    args = parser.parse_args()

    project_dir = Path(__file__).resolve().parents[1]
    print_checks(collect_checks(DEFAULT_CONFIG))
    created = not CONFIG_FILE.exists()
    config_path = write_default_config()
    recording_dir = Path(str(DEFAULT_CONFIG["recording_directory"])).expanduser()
    try:
        recording_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"FAIL: 无法创建录制目录 {recording_dir}: {exc}")
        return 1
    print(f"\n{'已创建' if created else '保留现有'}配置: {config_path}")
    print(f"已准备录制目录: {recording_dir}")

    incomplete: list[str] = []

    if args.install_python_deps:
        venv = project_dir / ".venv"
        if not venv.exists():
            subprocess.run([sys.executable, "-m", "venv", str(venv)], check=False)
        pip = venv / "bin" / "python3"
        result = subprocess.run([str(pip), "-m", "pip", "install", "-r", str(project_dir / "requirements.txt")], check=False)
        if result.returncode != 0:
            print("WARNING: Python 依赖安装失败，请检查网络后重试。")
            incomplete.append("Python 依赖安装失败")
    else:
        print("Python 依赖安装（推荐）: ./zoom-record setup --install-python-deps")

    if not device_exists(str(DEFAULT_CONFIG["multi_output_device"])):
        incomplete.append(f"尚未创建 {DEFAULT_CONFIG['multi_output_device']}")
        print(MULTI_OUTPUT_GUIDE)
        if not args.no_open and sys.platform == "darwin":
            audio_midi_setup = Path("/System/Applications/Utilities/Audio MIDI Setup.app")
            result = subprocess.run(["open", str(audio_midi_setup)], check=False)
            if result.returncode != 0:
                print(f"WARNING: 无法自动打开 {audio_midi_setup}，请手动打开“音频 MIDI 设置”。")
    print(OBS_GUIDE)
    if not args.no_open and sys.platform == "darwin" and not shutil.which("obs"):
        # Do not force-launch OBS during setup; the user may still need to install it.
        pass
    print("隐私权限请手动开启：系统设置 → 隐私与安全性 → 屏幕与系统音频录制 / 麦克风 → OBS。")
    print("下一步: 编辑 config.yaml（尤其是麦克风名和 WebSocket 密码），然后运行 ./zoom-record doctor")
    if incomplete:
        print("\nSETUP INCOMPLETE:")
        for item in incomplete:
            print(f"  - {item}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
