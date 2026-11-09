# Confocal Analysis：零基础入门

## 下载和启动

1. 打开 [GitHub 仓库](https://github.com/xi95360-web/tool)，点击 **Code → Download ZIP**，解压。
2. 进入 `tool-main → confocal-cell-measurements`。保留整个文件夹。
3. 电脑需要 Python 3.10 或更新版本；未安装时先从 [Python 官网](https://www.python.org/downloads/) 安装。
4. Mac 双击 **Start Confocal Analysis.command**；Windows 双击 **Start Confocal Analysis.bat**（Windows 尚未实机验证）。
5. 首次联网安装组件，等待浏览器打开；保留终端窗口。以后直接双击即可。
6. 先点 **Try a synthetic example**，可看到合成示例的表格、QC 图和下载按钮。

## 分析自己的图片

1. 准备原始单平面的两通道 TIFF，例如 RFP 和 GFP。要求原始 Z=1、T=1、XY 像素大小相同；不能用投影图或 RGB 截图代替。
2. 上传负责识别细胞边界的通道，再上传需要测量的通道。
3. 选择细胞分割方式：已有 mask、Cellpose-SAM，或者简单阈值基线。已有 mask 必须是每个细胞一个独立整数标签、背景为 0 的 TIFF。
4. 如果要用 Cellpose：先关闭程序，双击 **Install Cellpose.command**（Windows 用同名 `.bat`），等待较大的组件下载完成，再启动程序选择 Cellpose。第一次分割还可能下载模型权重。未进行实机模型验收前请检查每张分割图。
5. 从显微镜元数据填写像素大小，单位是 **µm/pixel**；确认原始单平面信息。不同像素大小的图片请分批分析。
6. 在配对表中，为每张边界通道图选择同一视野的测量通道图和 mask；不要按上传顺序猜测配对。条件和生物学重复可按实际情况填写。
7. 点击 **Analyze images**，检查青色细胞边界、品红色 puncta 和表格中的 QC 标记。
8. 点击 **Save all results (.zip)** 保存。解压后，CSV 可用 Excel 打开，TIFF 和 overlay 可用 Fiji 查看。

## 原始文件是 CZI 怎么办

目前网页只接收 TIFF。先在 Fiji 选择 **File → New → Script**，在脚本编辑器打开本目录的 **export_channels.groovy**，选择 **Language → Groovy → Run**。选择 CZI 和一个新的空导出文件夹。核对导出的通道身份与像素单位，再上传对应 TIFF。不同源文件使用不同空目录，避免同名序列覆盖。这个 Fiji 导出桥接尚待人工验收。

## 保存、退出和报错

保存 ZIP 后，在终端按 **Control+C** 停止；下次再次双击启动。结果未下载前只保存在运行中的会话里。puncta 数量不能单独证明自噬通量，默认阈值也需要结合自己的图像验证。

浏览器没自动打开时，打开终端显示的网址，通常是 `http://localhost:8501`。Mac 双击打不开时，在终端输入 `python3` 加一个空格，把 **launch.py** 拖入后回车。首次安装需要联网，不需要 API key。端口被占用时先关闭另一个 workflow；详细说明见 [README](./README.md)。
