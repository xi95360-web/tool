# STING Structure：零基础入门

## 下载和启动

1. 在 [GitHub](https://github.com/xi95360-web/tool) 点击 **Code → Download ZIP**，解压。
2. 打开 `tool-main → sting-structure-triage`，保留整个文件夹。
3. 电脑需要 Python 3.10 或更新版本；缺少时先从 [Python 官网](https://www.python.org/downloads/) 安装。
4. Mac 双击 **Start STING Structure.command**；Windows 双击 **Start STING Structure.bat**（Windows 尚未实机验证）。
5. 第一次联网安装组件，等待浏览器打开，并保持终端开启。
6. 点 **Try a synthetic example** 先试跑；示例是人工构造的四残基结构，不是 STING 生物学证据。

## 分析自己的突变

1. 上传参考蛋白的 **氨基酸 FASTA**，不是质粒 DNA 或 GenBank 文件。
2. 上传对应结构的 **PDB / mmCIF** 文件。
3. 从下拉菜单选择目标蛋白链。
4. 输入真实需要检查的突变，例如 `N154S`，或 `Assess L90E and M120L`。多个突变目前分别描述，不预测彼此的相互作用。
5. 默认选择实验 B factor；只有明确知道文件把 pLDDT 存在 B-factor 字段时才切换为 pLDDT。
6. 点 **Assess mutations**，查看位点映射状态、结构残基编号和结构描述。
7. 点 **Save report (.zip)**，解压后双击 HTML 阅读，或用 Excel 打开 CSV。

## 怎么读结果

`mapped` 表示位点成功对应；`unresolved` 可能是缺失残基或映射不确定，不表示突变没有功能影响。参考残基不匹配时请核对序列背景与编号；序列一致性不足时请核对物种和链。

当前版本提供输入结构上的位点描述，尚未接入 ΔΔG、功能预测或构象评分，也不生成突变体结构。与非水异源原子的距离可能涉及离子或添加剂，不等于配体结合能力。

## 下次使用

先下载报告，再在终端按 **Control+C** 关闭；下次再次双击启动。首次安装需要联网，正常本地分析无需 API。浏览器未打开时使用终端显示的本地网址；端口被占用时先关闭另一个 workflow。

Mac 双击启动不了时，终端输入 `python3` 加一个空格，把本目录 **launch.py** 拖入后回车。更多排错见 [README](./README.md)。
