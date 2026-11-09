# Start here / 从这里开始

Download: repository homepage → **Code → Download ZIP** → extract the ZIP → open one application folder below. Python 3.10 or later is required. First launch installs components automatically and needs internet. There is no API key or coding requirement for the basic local interfaces.

下载仓库 ZIP 并解压，进入下面对应的应用文件夹，双击启动文件。首次需要安装 Python 3.10 或更新版本、联网安装组件；之后重复双击即可。不要只下载单个脚本。

| Application | Folder | Mac double-click file | Beginner guide |
| --- | --- | --- | --- |
| Sequencing QuickCheck | `quickchange-seq-check` | `Start QuickCheck.command` | [English](./quickchange-seq-check/README.md) / [中文](./quickchange-seq-check/START_HERE.zh-CN.md) |
| Confocal Analysis | `confocal-cell-measurements` | `Start Confocal Analysis.command` | [English](./confocal-cell-measurements/README.md) / [中文](./confocal-cell-measurements/START_HERE.zh-CN.md) |
| STING Structure | `sting-structure-triage` | `Start STING Structure.command` | [English](./sting-structure-triage/README.md) / [中文](./sting-structure-triage/START_HERE.zh-CN.md) |
| STING Databank | `sting-mutant-databank` | `Start STING Databank.command` | [English](./sting-mutant-databank/README.md) / [中文](./sting-mutant-databank/START_HERE.zh-CN.md) |

Windows: use the matching `.bat` file instead; Windows entry points are provided but have not been tested on Windows. On Mac, launchers have executable permissions in the repository; archive extraction and operating-system prompts may vary. If double-click fails, type `python3` followed by a space in Terminal, drag that folder's `launch.py` into the window and press Return.

Keep the terminal open while using the browser page. Save/download results before stopping. Press Control+C in the terminal to stop; double-click to start again. Use one app at a time on the default local port. If the browser does not open automatically, use the address printed in the terminal.

Confocal optionally installs Cellpose through a second double-click entry named **Install Cellpose**. CZI import currently uses the documented Fiji export step; it is not yet a direct browser upload. Structure scores and Paperclip integration remain research milestones, as described in each project.
