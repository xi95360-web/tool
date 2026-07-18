# Zotero 选词翻译

适用于 Zotero 7、8 和 9。在 Zotero 内置 PDF/EPUB 阅读器中选中文字，翻译会直接出现在 Zotero 自带的选区浮窗里。项目源码公开、无需 API Key。

## 安装

1. 打开 Zotero。
2. 进入“工具” → “插件”。
3. 点击右上角齿轮，选择“Install Plugin From File…”（从文件安装插件）。
4. 从 GitHub Releases 下载并选择 `zotero-word-translate-1.0.3.xpi`。
5. 打开一篇 PDF，选中一个英文单词即可看到中文翻译；选中中文时会翻译成英文。

## 隐私与限制

- 插件只把当前选中的文字发送给 MyMemory 在线翻译接口，不会上传 PDF 或 Zotero 文库数据。
- MyMemory 无需 API Key，但匿名免费服务有调用额度，且必须联网。
- 一次最多翻译 200 个字符；翻译结果会在本次 Zotero 运行期间缓存，减少重复请求。

## 源码结构

- `manifest.json`：Zotero 插件信息和兼容版本。
- `bootstrap.js`：选区浮窗、翻译请求和缓存逻辑。

## 重新打包

需要 Python 3。在本目录执行：

```sh
python3 scripts/build_xpi.py
unzip -t dist/zotero-word-translate-1.0.3.xpi
```

## Codex Skill

仓库包含 `skills/zotero-word-translate/`，用于指导 Codex 安全地修改、检查和打包插件。Skill 不会读取你的 Zotero 文库。
