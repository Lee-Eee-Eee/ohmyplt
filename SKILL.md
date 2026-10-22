---
name: ohmyplt
description: "Create, edit and polish scientific figures: data plots, statistical comparisons, multi-panel research figures, experimental schematics, method flowcharts and model architectures. Use for 科研绘图、论文配图、数据可视化、误差棒、拟合与残差、能谱、热图、实验示意图 or improving existing plotting code."
metadata:
  version: "1.1.0"
---

# ohmyplt

让科学问题、数据和方法在最终尺寸下清楚可读。沿用用户的数据、有效绘图后端、项目风格与所需格式，按任务复杂度选择最短的绘图路径。

## 先选路径

| 任务 | 使用方式 | 按需参考 |
|---|---|---|
| 单条/多条曲线、散点、误差棒、直方图等普通单图 | 原生Matplotlib `plt.subplots`或修改现有脚本，设置轴、样式和导出 | [数据图](references/data-plots.md)中对应配方 |
| 拟合与残差、分布比较、共同色标、空间场、多面板 | 原生subplot/GridSpec；增加相关的统计定义、尺度与布局检查 | [数据图](references/data-plots.md)；必要时[构图](references/design.md) |
| 方法流程、实验装置、物理机制、网络架构 | 先确定对象、操作与关系，再选择节点、几何、箭头或局部展开 | [结构与示意](references/architecture.md)；复杂布局再读[构图](references/design.md) |
| 修改已有图或脚本 | 保留可用部分，只处理当前问题；按图中内容选择上述路径 | 相关专项参考 |

混合图分别处理数据面板与示意面板，再统一视觉层级。普通单图直接绘制；仅在存在节点连接时设计端口与路由。`Plate`是示意图的可选工具，原生Matplotlib轴是数据图的默认工具。按需读取参考，单图无需先加载完整工具文档或全部示例。

## 共同要求

- **科学含义。**先明确图要支持的判断。保持数据、单位、尺度、配对关系、独立样本单位与不确定度定义。显示变换与原始数据分开；用合成数据演示时注明其来源。
- **信息层级。**把面积留给主要证据。曲线与分组用颜色、线型或标记区分；背景和网格退后。图注容纳统计定义与长说明，图内保留读图所需标签。
- **最终尺寸。**优先使用用户/期刊给定尺寸；85 mm单栏、183 mm双栏可作为可调起点。按成图大小选择字号、线宽与间距，检查标签、图例、色条和裁切。
- **字体与风格。**默认Arial说明文字、Times New Roman数学与数值；用户、项目或期刊要求优先。缺字体时明确选择可用字体或注册字体文件。配色随数据与对象含义选择，兼顾色觉差异和灰度阅读。
- **可编辑交付。**保留生成源码与数据入口，按用户需要导出PDF、SVG或PNG。矢量文字保持可编辑；密集图层可局部栅格化。输入哈希、检查日志留在工作目录。

## 绘制与检查

对简单图，读取数据与标签后直接使用已有后端绘图，应用所需样式，导出并目视最终尺寸。字体、图例、误差定义与范围正确即可完成这一条路径。

组合面板增加共享坐标/色标、对齐、统计表达与相关局部的检查。投稿定稿、复杂示意或出现文字拥挤时，可运行PDF字高、碰撞与字体检查，再逐项处理实际发现。检查层次与命令见[质量检查](references/quality.md)；自动几何报告需要结合图的含义判断。

使用现有Python代码时可导入`configure`、`apply_chart_style`、`export`；接口和其他后端的使用原则见[工具](references/tools.md)。交付所需图与源文件，不在图内加入检查计数或自评文字。

## 可运行起点

在技能目录运行（从用户项目调用时使用脚本的完整路径，输出指向用户项目）：

```bash
# 默认只生成一个轻量单图；--portable明确选择内置DejaVu字体
python scripts/quickstart.py --portable --out output

# 选择科研配方；按需增加完整PDF检查
python scripts/quickstart.py --example calibration --portable --check --out output
python scripts/quickstart.py --example spectrum --portable --out output

# 检验全部示例，包括结构示意
python scripts/quickstart.py --example all --portable --check --out output
```

`--portable`供无Arial/Times的环境体验，正式图使用约定字体。单图见[源码](examples/simple_plot.py)，配方见[源码](examples/scientific_plots.py)，实验示意见[源码](examples/optical_schematic.py)，网络示例见[源码](examples/network.py)。这些示例的图型、配色和组件供选择，不构成所有科研图的固定模板。借鉴与许可见[来源](references/sources.md)。
