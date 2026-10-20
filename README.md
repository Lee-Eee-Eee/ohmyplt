# ohmyplt

把研究逻辑画清楚，把细节做到位。

一个面向科研图、神经网络架构和物理示意图的绘图 skill。它把多轮实际修改中形成的风格、技巧与工具整理为可复用的规则和Python组件。

## 风格示例

![ohmyplt风格示例：共同表示与稀疏历史反演](assets/approved-network-v19.png)

这张图展示了这套风格的主要做法：物理对象与时间采样接入网络；模块内部展示实际运算；残差沿圆角路径进入Σ；共享解码器一处展开、一处简写；Times数学与Arial标签各司其职。

## 包含什么

- **结构与节奏**：依据科学主线安排面积、留白、分组和阅读路径。
- **字体**：Arial正文，Times New Roman元素、公式、数值维度与上下标。
- **精细连线**：连续圆角路径、圆周端口、完整箭杆、分组边框开口。
- **功能图形**：时间采样、GRU门与回路、Dense带权连接、Linear矩阵与偏置、激活曲线。
- **数据图**：配对比较、时间曲线、空间场、统计定义、同尺度比较。
- **工具**：毫米坐标组件、字体与缺字检查、PDF字高与碰撞检查、最终尺寸与局部预览。
- **出处**：Nature绘图skill、Transformer、SHPNet及实际修改经验的明确归属。

## 安装

```bash
git clone https://github.com/Lee-Eee-Eee/ohmyplt.git ~/.codex/skills/ohmyplt
python -m pip install -r ~/.codex/skills/ohmyplt/requirements.txt
```

在Codex中使用：

```text
使用 $ohmyplt 绘制这张网络结构图，结合实际代码解释各模块与训练路径。
```

也可以将仓库放在其他路径，把[SKILL.md](SKILL.md)提供给支持skill的工具。

## 运行组件示例

```bash
python scripts/doctor.py
python examples/network.py --out output
python examples/data_plot.py --out output
python scripts/preflight.py output/network.pdf --out output/qa
```

默认使用系统已安装的Arial与Times New Roman；可通过`--font-dir`注册自己提供的字体目录。跨平台功能测试可显式指定`--body-font "Liberation Sans" --math-font "Liberation Serif"`，实际字体记录在输出清单中。

代码示例使用固定种子的演示数据。上方PNG是用户认可的实际项目风格示例。工具用法见[references/tools.md](references/tools.md)。

## 借鉴与许可

[Nature Figure skill](https://github.com/Yuan1z0825/nature-skills)提供了最终尺寸、矢量输出、字体与碰撞检查等工作流启发；本仓库保留两项原始检查工具及Apache-2.0许可。Transformer和SHPNet提供了结构组织的参考。详见[来源说明](references/sources.md)和[第三方说明](THIRD_PARTY_NOTICES.md)。本仓库采用Apache-2.0许可。
