# Zoom Recording Helper

> **录制前请取得所有参会者的明确同意，并遵守所在地法律、雇主/学校政策和会议平台规则。** 本工具不会隐藏录制、不会注入或修改 Zoom，也不会绕过 macOS 权限。所有录制和转写默认只在本机进行。

这是一个适用于 Apple Silicon Mac 的轻量级终端工具。它组合 Zoom、OBS Studio、BlackHole 2ch、macOS 多输出设备和 OBS WebSocket，负责开始/停止录制、整理文件、无损转封装、提取音频，以及可选的本地 Whisper 转写。它不是 Zoom 插件，也不是完整 macOS App。

OBS 录制时会显示红色录制状态，终端也会明确输出 `🔴 Recording started`。请勿将本工具用于秘密录制。

仓库只包含工具源码、示例配置和测试；`.gitignore` 会排除真实密码、录屏、音频、转写、日志和本地会话状态。

## 工作原理

正常扬声器或耳机和 BlackHole 2ch 被组合成 `Zoom Multi-Output`。Zoom 的声音一边播放给你听，一边送入 BlackHole；OBS 同时采集 BlackHole、麦克风和 Zoom 窗口。脚本只切换音频输出、打开应用，并通过 OBS 官方 WebSocket 控制录制。

## 1. 安装基础软件

### 安装 Homebrew

打开“终端”（访达 → 应用程序 → 实用工具 → 终端），粘贴并回车：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

安装结束后，请按 Homebrew 显示的提示把它加入 PATH，然后安装依赖：

```bash
brew install --cask obs
brew install --cask blackhole-2ch
brew install ffmpeg
brew install switchaudio-osx
brew install python
```

BlackHole 安装后若设备没有出现，请注销并重新登录，必要时重启 Mac。

## 2. 首次配置

进入本项目目录：

```bash
cd zoom-recording-helper
./zoom-record setup --install-python-deps
```

这会创建项目专用的 `.venv`、安装 `PyYAML` 与 `obsws-python`、创建：

- 配置：`~/.config/zoom-recording-helper/config.yaml`
- 日志：`~/.config/zoom-recording-helper/logs/`
- 录制目录：`~/Movies/ZoomRecordings/`

若当前没有网络，也可先运行 `./zoom-record setup`；之后再运行带 `--install-python-deps` 的命令。

### 创建多输出设备

如果 `Zoom Multi-Output` 不存在，setup 会打开“音频 MIDI 设置”。请手动完成：

1. 点击左下角 `+`。
2. 选择“创建多输出设备”。
3. 勾选你实际听声音的设备，例如“MacBook 扬声器”或有线耳机。
4. 勾选 `BlackHole 2ch`。
5. 将实际播放设备设为主设备/时钟源（通常排在最上方）。
6. 为 BlackHole 2ch 勾选“漂移校正”。
7. 双击左侧设备名称，改名为 `Zoom Multi-Output`。

不建议把蓝牙耳机作为会议麦克风与输出的组合设备；详见常见问题。

### 配置 Zoom

在 Zoom → 设置 → 音频中：

- 扬声器选“与系统相同”，或直接选 `Zoom Multi-Output`。
- 麦克风选你真实使用的麦克风，不要选 BlackHole。

脚本开始录制时会把 macOS 输出切换到 `Zoom Multi-Output`，停止时恢复原设备。

## 3. 配置 OBS

### 创建场景

1. 打开 OBS，点击“场景”区域的 `+`，命名为 `Zoom Recording`。
2. 在“来源”区域添加“macOS 屏幕采集”或“窗口采集”，选择 Zoom 窗口/显示器。
3. 添加“音频输入采集”，命名为“系统音频”，设备选 `BlackHole 2ch`。
4. 再添加“音频输入采集”，命名为“麦克风”，设备选你的实际麦克风。
5. 在 OBS → 设置 → 输出 → 录制中，推荐格式选择 **MKV**。意外退出时 MKV 比 MP4 更容易保全。

首次捕获屏幕和麦克风时，macOS 会要求授权。进入“系统设置 → 隐私与安全性”，在“屏幕与系统音频录制”和“麦克风”中启用 OBS，然后彻底退出并重新打开 OBS。脚本不会也不能替你绕过这些权限。

### 开启 OBS WebSocket

OBS 28 及更新版通常内置 WebSocket：

1. 打开 `Tools（工具） → WebSocket Server Settings`。
2. 勾选 `Enable WebSocket server`。
3. 端口保持 `4455`。
4. 可以设置密码；将同一个密码写入 `~/.config/zoom-recording-helper/config.yaml` 的 `obs_websocket_password`。

密码只用于连接 OBS，不会写进日志。若 OBS 版本过旧，请升级 OBS。

### 设置混合和独立音轨

在 OBS 混音器齿轮菜单打开“高级音频属性”：

- `BlackHole 2ch`：勾选轨道 1 和轨道 2。
- 麦克风：勾选轨道 1 和轨道 3。
- 轨道 1 = 混合音频。
- 轨道 2 = 系统/参会者音频。
- 轨道 3 = 麦克风音频。

还要在 OBS → 设置 → 输出 → 录制中启用轨道 1、2、3。然后在配置中设置：

```yaml
audio_tracks_separate: true
```

停止后工具会尝试生成 `mixed_audio.m4a`、`system_audio.m4a` 和 `microphone_audio.m4a`。等价手动命令是：

```bash
ffmpeg -i meeting.mp4 -map 0:a:0 -vn -c:a aac mixed_audio.m4a
ffmpeg -i meeting.mp4 -map 0:a:1 -vn -c:a aac system_audio.m4a
ffmpeg -i meeting.mp4 -map 0:a:2 -vn -c:a aac microphone_audio.m4a
```

如果只录制一个混合音轨，保持 `audio_tracks_separate: false`。

## 4. 检查环境

确保 OBS 已经打开，然后运行：

```bash
./zoom-record doctor
```

- `PASS`：已确认正常。
- `WARNING`：通常需要人工确认，例如 macOS 隐私权限或 OBS 暂未运行。
- `FAIL`：缺少关键软件或设备，按同一行提示修复。

脚本无法可靠读取 macOS TCC 隐私数据库，所以权限项会显示 WARNING 并要求人工确认。可用下面的命令打开屏幕权限设置：

```bash
./zoom-record doctor --open-privacy
```

## 5. 开始和停止录制

开始前让 Zoom 的扬声器使用“与系统相同”，打开/加入会议，然后运行：

```bash
./zoom-record start
```

它会进行关键检查、切换音频设备、打开 OBS（以及配置允许时打开 Zoom）、切换到 `Zoom Recording` 场景、设置本次目录并开始录制。重复运行 start 会被拒绝。

结束时运行：

```bash
./zoom-record stop
```

工具会停止 OBS，等待写盘，按 `YYYY-MM-DD_HH-mm_Zoom_Meeting.mkv` 命名原始文件，再用以下方式无损封装 MP4（不重新编码）：

```bash
ffmpeg -i input.mkv -map 0 -c copy output.mp4
```

原始 MKV 默认永久保留。不要在 OBS 仍写盘时手动移动文件。

## 6. 找回录制文件

默认位置是：

```text
~/Movies/ZoomRecordings/YYYY-MM-DD_HH-mm_Zoom/
```

stop 完成后会自动用访达打开该目录。目录中通常有：

- 原始 `.mkv`（永不自动删除）
- 无损封装的 `.mp4`
- `metadata.json`
- `mixed_audio.m4a`，以及启用独立音轨时的另外两个音频文件
- 开启转写后的 `transcript.txt`、`transcript.md`、`transcript.srt`

如果 stop 未找到输出，它会保留 `current_session.json`，避免丢失恢复线索。可检查 OBS → 文件 → 显示录像，以及本次会话目录，再重新运行 stop。

## 7. 可选本地转写

默认关闭，且不会上传到云端。

### MLX Whisper（Apple Silicon 推荐）

使用项目虚拟环境安装：

```bash
.venv/bin/python3 -m pip show mlx-whisper
.venv/bin/python3 -m pip install mlx-whisper
```

配置：

```yaml
transcribe: true
transcription_backend: mlx-whisper
transcription_model: mlx-community/whisper-small-mlx
```

不指定 `language`，让模型自动处理中文、英文或混合语言。

### whisper.cpp

先自行安装 `whisper-cli` 并下载本地模型，再配置：

```yaml
transcribe: true
transcription_backend: whisper.cpp
whisper_cpp_binary: whisper-cli
whisper_cpp_model: ~/Models/ggml-small.bin
```

转写失败只会显示 WARNING 并写入元数据/日志，不会删除或破坏录制。

## 配置参考

首次 setup 会生成完整配置。常用项：

```yaml
recording_directory: ~/Movies/ZoomRecordings
obs_scene_name: Zoom Recording
obs_websocket_host: localhost
obs_websocket_port: 4455
obs_websocket_password: ""
multi_output_device: Zoom Multi-Output
system_audio_device: BlackHole 2ch
microphone_device: MacBook Microphone
auto_open_zoom: true
auto_open_obs: true
extract_audio: true
transcribe: false
```

如果 Mac 上的麦克风显示为其他名称，请把 `microphone_device` 改成 OBS 中看到的准确名称。此项用于提示和元数据；实际采集设备仍由 OBS 场景控制。

## 常见问题

### 只能录到自己的声音

OBS 很可能只采集了麦克风。确认 Zoom 扬声器是“与系统相同”或 `Zoom Multi-Output`，OBS 中存在以 `BlackHole 2ch` 为设备的音频输入采集，并观察对方说话时该电平表是否跳动。

### 只能录到对方声音

确认 OBS 场景中还有第二个“音频输入采集”，设备是实际麦克风；检查 macOS 麦克风权限以及 OBS 混音器是否静音。Zoom 和 OBS 可以同时读取麦克风。

### 使用蓝牙耳机后音质变差

当蓝牙耳机同时作为麦克风和输出时，macOS 可能切到低带宽通话模式。使用 MacBook/USB 麦克风作为输入，蓝牙耳机只作输出；或者使用有线/USB 耳机。设备变化后需要重新检查多输出设备。

### OBS 没有声音

查看 OBS 混音器电平。确认来源未静音、设备不是“默认”而是明确的 `BlackHole 2ch`，采样率一致（通常 48 kHz），并重启 OBS。不要同时启用一个重复的全局桌面音频来源。

### BlackHole 无声音

BlackHole 本身是虚拟线缆，不会发声。必须使用包含真实播放设备和 BlackHole 的多输出设备；真实设备作主设备，BlackHole 开漂移校正。

### Zoom 听不到声音

Zoom 的“麦克风”必须是你的真实麦克风，不是 BlackHole。用 Zoom 设置中的“测试麦克风”确认。`Zoom Multi-Output` 应用于扬声器/系统输出。

### stop 后没有生成文件

先在 OBS 选择“文件 → 显示录像”。确认磁盘有空间、OBS 输出格式正常，查看本次会话目录和 `~/.config/zoom-recording-helper/logs/`。不要删除 `current_session.json`；把 OBS 文件放进本次目录后可再次运行 stop。若你在 OBS 内手动停止，工具也会尝试寻找本次目录中最新文件。

### OBS WebSocket 无法连接

确认 OBS 正在运行、工具 → WebSocket Server Settings 已启用、端口为 4455。若设置密码，配置文件必须完全一致。`localhost` 通常无需修改。防火墙一般不会阻止本机连接，但安全软件可能会。

## 日志与隐私

日志位于 `~/.config/zoom-recording-helper/logs/`，记录命令时间、OBS 连接/录制、设备切换、输出路径、ffmpeg 结果和错误。日志不会保存 OBS WebSocket 密码、音频内容、转写全文或会议内容。工具不包含上传功能。

## 测试

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts tests
```

真实 OBS/音频设备联调必须在已授权的 Apple Silicon Mac 上手动运行 `doctor`、`start` 和 `stop`。

## Codex Skill

仓库包含 `skills/zoom-recording-helper/`，用于指导 Codex 在取得参会者同意后配置、检查和排障。Skill 明确禁止隐藏录制、绕过 macOS 权限或未经授权上传录屏和转写。

## 完全卸载

先停止任何活动录制，然后删除项目、配置和录制文件（录制文件删除不可恢复，请先备份）：

```bash
rm -rf ~/.config/zoom-recording-helper
rm -rf /path/to/zoom-recording-helper
```

仅当你确定其他工作不使用它们时，才卸载依赖：

```bash
brew uninstall --cask obs
brew uninstall --cask blackhole-2ch
brew uninstall ffmpeg switchaudio-osx
```

注销或重启后 BlackHole 才可能从音频设备列表消失。最后在“音频 MIDI 设置”中手动删除 `Zoom Multi-Output`。本工具不会自动删除 `~/Movies/ZoomRecordings`，以免误删录制。
