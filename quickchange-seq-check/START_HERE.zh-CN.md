# QuickCheck：第一次使用

无需写代码。程序会在你电脑的浏览器里显示英文操作界面，目前仍需要电脑安装 Python 3.10 或更新版本。

## 下载并启动

1. 打开 [GitHub 仓库](https://github.com/xi95360-web/tool)，点击绿色 **Code → Download ZIP**。
2. 解压，打开 `tool-main`，再打开 `quickchange-seq-check` 文件夹。请保留整个文件夹。
3. Mac：双击 **Start QuickCheck.command**。Windows：双击 **Start QuickCheck.bat**（Windows 启动器尚未实机验证）。
4. 第一次会打开终端并自动安装组件，需要联网，请等待；以后直接双击即可。
5. 浏览器打开分析页面后，保持终端窗口开启。如果浏览器没有自动打开，可以打开终端显示的本地网址，通常是 `http://localhost:8501`。

如果提示没有 Python，请先从 [Python 官网](https://www.python.org/downloads/) 安装，再启动程序。它目前不是免安装的独立 App。

## 上传并分析

1. **Choose your reference sequence**：上传原始对照质粒 `.gb` 或 `.gbk` 文件。
2. **Choose your sequencing files**：上传测序公司的 `.ab1` 文件，可同时选择多个。`.seq` 也能分析，但没有峰图质量分数。
3. **Select the gene you want to check**：从下拉菜单选择目标基因，例如 STING；不要选到抗性基因。
4. **Expected amino-acid edits**：填写真实预期，例如 `N154S`。同一个克隆的双突变写成 `H72N,M120L`；不填写则只报告观察到的变化。这个设置会应用于本次所有文件，预期不同的样本请分批分析。
5. 点击 **Analyze sequences**，查看结果、比对、其他替换和插入/缺失。
6. 点击 **Save quickchange_report.html** 保存报告，以后可直接双击报告打开。

只覆盖一段的测序不能排除质粒其他区域的错误。报告中的 PASS 只针对已覆盖范围，不能直接保证整个质粒及表达完全正常。

## 关闭和下次使用

保存报告后，在终端窗口按 **Control+C** 停止。下次再次双击启动文件即可，无需重复安装、激活环境或输入测序路径。

## 如果 Mac 双击启动不了

打开终端，输入 `python3` 再加一个空格；先不要回车。把文件夹中的 **launch.py** 拖进终端，再按回车。程序会自动得到完整路径，因此不需要先进入指定文件夹。

`Directory '.' is not installable` 表示旧说明里的安装命令在错误文件夹运行；上面的启动方法不受当前文件夹影响。`command not found: quickcheck` 是安装未完成后的连带报错。pip 的“有新版本”只是通知，不是这次失败的原因。
