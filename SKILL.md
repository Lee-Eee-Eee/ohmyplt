---
name: ohmyplt
description: "Create and refine scientific figures, neural-network architectures, physical-model schematics, and research data plots with precise typography, smooth port-based routing, meaningful functional glyphs, and editable vector output. Use for 科研绘图、论文配图、网络结构图、流程示意图 or polishing existing figures."
metadata:
  version: "1.0.0"
---

# ohmyplt

把研究逻辑画成可读、精致的图。默认沿用用户认可的[风格示例](assets/approved-network-v19.png)：白底、克制配色、Times数学、圆角连续连线、嵌入模块的短标签，以及有功能含义的细节。

## 先选要用的材料

- 所有图：读[构图与排版](references/design.md)。
- 网络、流程、物理对象：再读[网络与功能图形](references/architecture.md)。
- 曲线、空间场、统计比较：再读[数据图](references/data-plots.md)。
- 实际绘制：使用[工具与代码接口](references/tools.md)，运行本地检查后目视全图、最终尺寸及关键局部。
- 借鉴来源与工具许可见[来源](references/sources.md)及[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 固定风格

1. **先说清图要解释什么。**用真实对象、数据、运算和连接组织画面。给主证据或关键运算更多面积；上下阶段可以一处展开、另一处复用简图。
2. **文字融入结构。**标题进入组的顶部，尺寸进入节点页脚，变量靠近对应端口。公式说明眼前的运算。图注承接样本、训练和统计定义；图内保留帮助阅读的必要说明。
3. **Arial正文，Times New Roman数学。**元素符号正体，量符号斜体，描述性下标正体；公式、数字维度、上下标、运算符同属Times。双栏183 mm图可从正文7 pt、数学7.5 pt、脚标5.4 pt、面板字母8 pt开始，依成图尺寸调整。检查实际字形和基线。
4. **Σ作为多路相加节点。**按字形轮廓居中；输入、输出接圆周端口。给箭头留完整线段，常用3–8 mm；转角圆滑，贯通分组边框时留开口。数据实线、参数共享虚线、训练反馈点划线，每种线型维持一种含义。
5. **细节承担解释。**History有时间轴与采样点；GRU有门与递归；Dense有带权连接和偏置；Linear有矩阵、偏置与维度；GELU有激活曲线。叠片对应门、时间或重复结构。可训练参数与固定参数的身份从训练回路和短标签读出。
6. **配色表达角色。**深青用于物理/数据路径，灰用于固定背景，浅青用于记忆单元，浅紫用于线性映射，浅金用于非线性，棕橙用于训练反馈。定量场值使用独立色图与明确色标。按当前图的含义选取所需角色。
7. **清晰来自图本身。**保留恰当的图内公式与说明，删除防御性文字、自评、宣传横幅和QA计数。留白分配给转接、分组和阅读节奏，避免一侧空、一侧挤。
8. **图形对应实际方法。**依代码核对分支、层数、权重形状、偏置、冻结与训练顺序。权重热图近白时先查零值、取样和色标；缩放规则写入图注。数据图保持真实信号尺度、比较范围和统计含义。

## 实施

沿用用户已有的有效后端；新建静态科研图默认Python/Matplotlib。SVG原稿可直接编辑；位图生成适合纹理与概念插画，精确网络结构优先矢量。适用期刊有特定要求时核查其当前指南，采用用户指定的字体与版式。

1. 查看实际代码、数据和用户参照，确定阅读路径与视觉重点。
2. 在最终毫米尺寸安排对象、组、端口和标签；先解决主干与共享关系。
3. 使用`scripts/ohmyplt.py`的组件或按其逻辑修改现有源文件。运行`scripts/doctor.py`核查字体，缺字时调整写法或明确选择可用数学排版方案。
4. 导出所需格式。用`scripts/preflight.py figure.pdf --min-pt 5 --out qa`检查实际字高、碰撞和裁切；用`scripts/preview.py`查看原尺寸与关键局部。重复数据面板另核对绘图区、标号与间距对齐。
5. 目视全图、最终尺寸和Σ/分支/上下标等局部，修复后再导出和检查。交付用户所需的图与源文件；溯源、检查记录留在工作文件中。

## 快速使用

```bash
python scripts/doctor.py
python examples/network.py --out /path/to/output
python examples/data_plot.py --out /path/to/output
python scripts/preflight.py /path/to/output/network.pdf --out /path/to/output/qa
```

两个可运行示例使用固定种子的演示数据；`assets/approved-network-v19.png`是本次研究项目中用户认可的实际风格示例。复制组件时让数据与布局保持独立，按当前研究内容组织新图。
