# Tool

Jessica 的实用工具与 Codex Skills 集合。每个子目录都可独立使用和维护。

## 项目

### Rotation Lab Workflows (English, local-first)

- [Sequencing QuickCheck](./quickchange-seq-check): Sanger screening with a double-click launcher and English upload interface. [零基础中文入门](./quickchange-seq-check/START_HERE.zh-CN.md).
- [Confocal Cell Measurements](./confocal-cell-measurements): two-channel ratios, segmentation adapters, puncta and QC exports.
- [STING Structure Triage](./sting-structure-triage): sequence-verified structural site descriptors; research prototype.
- [STING Mutant Databank](./sting-mutant-databank): provenance-aware SQLite schema, CSV import and offline search.

See [implementation status and validation gates](./docs/lab-workflows-release.md). These projects run without API keys; model weights and optional dependencies are installed separately. No private experimental data are included.

### [Zotero Word Translate](./zotero-word-translate)

在 Zotero 7–9 的 PDF/EPUB 选区浮窗中提供中英双向翻译。无需 API Key，只将当前选中的文字发送给 MyMemory，不读取 PDF 或 Zotero 文库。

- 安装包：[下载 v1.0.3 XPI](https://github.com/xi95360-web/tool/releases/tag/zotero-word-translate-v1.0.3)
- Skill：`zotero-word-translate/skills/zotero-word-translate/`

### [Zoom Recording Helper](./zoom-recording-helper)

面向 Apple Silicon Mac 的透明、需明确同意的 Zoom 录屏工作流，组合 OBS、BlackHole、音频整理和可选的本地 Whisper 转写。

- 不隐藏录制，不绕过 macOS 权限
- 不包含上传功能，录屏和转写默认仅保存在本机
- Skill：`zoom-recording-helper/skills/zoom-recording-helper/`

### [Build Research Presentation](./build-research-presentation)

把论文、Zotero 文献、实验数据或研究设想整理成逻辑严密、证据可追溯的 proposal / journal club 学术汇报。

- 内置用户问卷和参考文献候选表
- 每页执行 claim–evidence–limitation–takeaway 内容契约
- 融合 action title、ghost deck 和单页单证据焦点的沟通优先设计
- 区分已发表证据、用户数据、研究假设和推断，禁止虚构数据或引用
- 包含 proposal、journal club 双路线，逐图分析、讲稿、计时、备页和渲染质检
- Skill：`build-research-presentation/`
- 调用示例：`Use $build-research-presentation to create a 15-minute journal club deck from these papers.`

## 开源许可

仓库采用 [MIT License](./LICENSE)。使用录屏工具时，使用者仍须取得所有参会者同意，并遵守适用法律及组织政策。
