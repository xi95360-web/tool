# STING Databank：零基础入门

## 下载和启动

1. 在 [GitHub](https://github.com/xi95360-web/tool) 点击 **Code → Download ZIP**，解压。
2. 打开 `tool-main → sting-mutant-databank`，保留整个文件夹。
3. 电脑需要 Python 3.10 或更新版本；缺少时先从 [Python 官网](https://www.python.org/downloads/) 安装。
4. Mac 双击 **Start STING Databank.command**；Windows 双击 **Start STING Databank.bat**（Windows 尚未实机验证）。
5. 第一次联网安装界面组件，等待浏览器打开；保留终端窗口。
6. 可以点 **Try a synthetic example** 试跑。示例记录是虚构教学内容，不是文献结论。

## 不写代码，直接记录论文

1. 点 **Start a new empty databank**，开始自己的空库。
2. 在表单里填写论文标题、来源链接、变体和蛋白背景；背景不明确就填 `unresolved`，不要猜。
3. 填写实际测试的配体；同一实验的联合处理用英文分号分隔。无外源配体的基线留空。
4. 填写实验终点、论文支持的变化关系、结论，以及具体出处，例如 Figure 2B 或 Abstract。不同终点分开记录。
5. 选择已阅读的来源部分，核对原文后勾选确认，点击 **Add record**。
6. 在搜索框输入变体、配体或终点；留空可以浏览已收集内容。
7. 点击 **Save databank (.sqlite)** 保存。一定要先下载；关闭或重启前未保存的记录可能丢失。
8. 下次启动后展开 **Open a saved databank**，上传上次下载的文件并点击 **Open database**。

新建、打开另一个库或导入 CSV 会替换当前会话，请先保存。简单表单添加的是有出处的文献结论，不是完整剂量、时间、对照齐全的定量测量。

## 已有表格怎么导入

展开 **Import existing structured CSV tables** 可以下载空模板并导入符合本工具格式的关联表。任意 Excel 或 Paperclip 导出还不能直接导入，需要先做字段映射；初次使用建议从表单开始。

当前发布版没有预装完整 STING 文献数据库，也没有连接 Paperclip 或自动检索论文。搜不到只说明自己的库里没有匹配记录，不表示实验上没有反应。详细测量视图在尚未导入测量表时为空。

## 退出和下次使用

下载保存后，在终端按 **Control+C** 停止；下次双击同一启动文件。首次安装需要联网，本地录入和搜索无需 API。浏览器未打开时使用终端显示的网址；端口被占用时先关闭另一个 workflow。

Mac 双击启动不了时，在终端输入 `python3` 加一个空格，将 **launch.py** 拖入后回车。完整说明见 [README](./README.md)。
