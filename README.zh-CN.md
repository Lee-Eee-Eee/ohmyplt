# ohmyplt

**从一张简单数据图，到一组清楚的科研配图。**

用于数据图、统计比较、科研组合面板、实验示意和模型架构的 agent skill。基于数据、绘图代码或方法描述生成与修改科研图，交付保留可编辑文字的 SVG、PDF/PNG 和 Python 源码。

[English](README.md) · [安装](#安装) · [快速体验](#快速体验) · [画廊](#画廊)

[![绘图测试](https://github.com/Lee-Eee-Eee/ohmyplt/actions/workflows/smoke.yml/badge.svg)](https://github.com/Lee-Eee-Eee/ohmyplt/actions/workflows/smoke.yml)
[![Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

![科研图示例：简单曲线、标定、计数谱、空间场与分布](assets/gallery/overview.png)

## 选择需要的图

| 任务 | 绘制方式 | 重点 |
|---|---|---|
| **单张数据图** | 原生 Matplotlib 坐标轴 | 数据、单位、尺度、不确定度与清楚的标签 |
| **科研组合面板** | 协调的子图与共享视觉编码 | 拟合残差、配对案例、分布与可比较的空间场 |
| **结构或实验示意** | 物理对象、操作与连接关系 | 实验关系、方法流程、形状与共享参数 |

简单图直接绘制；组合面板增加所需布局与统计约定；示意图按需使用毫米坐标组件。默认 Arial 普通标签、Times New Roman 数学与数值刻度，项目、期刊或用户指定的字体可以覆盖默认值。

## 安装

使用 [Skills CLI](https://github.com/vercel-labs/skills)，需要 Node.js 22.20+：

```bash
npx skills add Lee-Eee-Eee/ohmyplt --skill ohmyplt
```

按提示选择 agent；加 `-g` 可供各项目使用。在实际运行脚本的 Python 环境中安装依赖。手动安装到 Codex：

```bash
git clone https://github.com/Lee-Eee-Eee/ohmyplt.git ~/.codex/skills/ohmyplt
python -m pip install -r ~/.codex/skills/ohmyplt/requirements.txt
```

在 Codex 中用 `$ohmyplt` 调用；其他 agent 可按各自方式加载 [SKILL.md](SKILL.md)。

## 快速体验

需要 Python 3.10+。在工作目录克隆并生成一张数据图：

```bash
git clone https://github.com/Lee-Eee-Eee/ohmyplt.git
cd ohmyplt
python -m pip install -r requirements.txt
python scripts/quickstart.py --portable --out output
```

打开 `output/simple-plot.png` 查看成图。同一目录还会保存 SVG/PDF、合成示例数据、图注与清单。输出路径相对于执行命令时的当前目录。

`--portable` 明确选择 Matplotlib 自带的 DejaVu Sans/Serif。省略该选项使用 Arial/Times；可用 `--font-dir PATH` 注册自备字体，或用 `--body-font`、`--math-font` 指定字体。

用 `--example calibration`、`spectrum`、`heatmap`、`distribution`、`data`、`optical`、`comparison` 或 `network` 选择其他示例；默认值为 `simple`。加 `--check` 才运行 PDF 字高/碰撞检查并生成最终尺寸预览。开发或 CI 需要生成并检查整套画廊时，显式运行：

```bash
python scripts/quickstart.py --example all --portable --check --out output
```

## 画廊

可运行示例使用固定种子的合成数据与初始化演示权重。画廊使用 Arial/Times；样式比较中的 Matplotlib 基线保留其默认字体。各绘图示例均支持显式字体参数。

### 数据图与科研组合面板

| 单图曲线与误差棒 | 标定与残差 |
|---|---|
| ![合成观测、已定义的测量不确定度与生成曲线](assets/gallery/simple-plot.png) | ![合成标定观测、拟合关系及残差](assets/gallery/calibration.png) |
| [源码](examples/simple_plot.py) · [SVG](assets/gallery/simple-plot.svg) · [PDF](assets/gallery/simple-plot.pdf) | [源码](examples/scientific_plots.py) · [SVG](assets/gallery/calibration.svg) · [PDF](assets/gallery/calibration.pdf) |

| 计数谱 | 可比较的空间场 |
|---|---|
| ![合成分箱计数谱](assets/gallery/spectrum.png) | ![共用色标的参考场与预测场，以及独立误差色标](assets/gallery/heatmap.png) |
| [源码](examples/scientific_plots.py) · [SVG](assets/gallery/spectrum.svg) · [PDF](assets/gallery/spectrum.pdf) | [源码](examples/scientific_plots.py) · [SVG](assets/gallery/heatmap.svg) · [PDF](assets/gallery/heatmap.pdf) |

| 分布与独立案例 | 配对案例与时间预测 |
|---|---|
| ![独立合成案例及其分布](assets/gallery/distribution.png) | ![原生子图中的配对观测与采样时间曲线](assets/gallery/data-plot.png) |
| [源码](examples/scientific_plots.py) · [SVG](assets/gallery/distribution.svg) · [PDF](assets/gallery/distribution.pdf) | [源码](examples/data_plot.py) · [SVG](assets/gallery/data-plot.svg) · [PDF](assets/gallery/data-plot.pdf) |

运行科研配方：`python examples/scientific_plots.py --kind calibration --out output`。其他类型为 `spectrum`、`heatmap`、`distribution` 和 `all`。配对/时间示例使用 `python examples/data_plot.py --out output`。

### 同一组数据，两种样式

![Matplotlib 默认样式与 ohmyplt 样式，数据与坐标范围相同](assets/gallery/style-comparison.png)

[源码](examples/style_comparison.py) · [SVG](assets/gallery/style-comparison.svg) · [PDF](assets/gallery/style-comparison.pdf)

两个面板保留相同数据、尺度、范围和标签。复现：`python examples/style_comparison.py --out output`。

### 架构与结构示意

![含样品与参考探测器的概念性光学透射测量示意](assets/gallery/optical-schematic.png)

[源码](examples/optical_schematic.py) · [SVG](assets/gallery/optical-schematic.svg) · [PDF](assets/gallery/optical-schematic.pdf)

这张概念装置图区分光路与读出，展示移除样品后测得的基线归一化。复现：`python examples/optical_schematic.py --out output`。

![采样历史、固定仿射支路、可训练运算、残差合流与更新路径](assets/gallery/network.png)

[绘图源码](examples/network.py) · [SVG](assets/gallery/network.svg) · [PDF](assets/gallery/network.pdf) · [实际项目参考](assets/approved-network-v19.png)

这张架构案例展示按需使用的采样、GRU、带权连接、偏置与端口连线组件。复现：`python examples/network.py --out output`；对应 NumPy 前向计算：`python examples/residual_model.py --out output/prediction.json`。

![架构案例渲染导览：模型源码、绘图细节与矢量导出](assets/demo/walkthrough.gif)

这段 18 秒渲染导览仅展示该架构案例，使用初始化示例权重和实际 PDF 检查结果。[MP4](assets/demo/walkthrough.mp4) · [模型源码](examples/residual_model.py)。将 ffmpeg 加入 PATH 后，用 `python scripts/build_demo.py` 重新制作；中间文件保存在 `output/demo/`。

## 三个起步提示

**一张数据图**

```text
使用 $ohmyplt，把 measurements.csv 中的时间与电压画成一张 85 mm 宽的图。
保留实际单位与已定义的不确定度，提供 SVG、PDF、PNG 和绘图源码。
```

**科研组合面板**

```text
使用 $ohmyplt，基于已有标定数据和拟合结果修改 plot_results.py。
上图显示测量与拟合，下图显示残差，明确不确定度定义与共享坐标。
```

**实验或模型示意**

```text
使用 $ohmyplt，绘制这套实验装置或 model.py 中的方法。
根据实际来源核对物理关系、输入输出形状与运算，提供可编辑 SVG 和 Python 源码。
```

## 工具与检查

按任务使用[数据图配方](references/data-plots.md)、[共用设计规范](references/design.md)和[工具说明](references/tools.md)。单图核对数据与最终尺寸；组合或复杂图增加有关的面板比较与可选 PDF 几何检查。见[分层质量检查](references/quality.md)。

遇到问题可[提交 issue](https://github.com/Lee-Eee-Eee/ohmyplt/issues/new/choose)，附最小脚本、可公开的样例输入和期望结果。中英文均可。

## 借鉴与许可

[Nature Figure skill](https://github.com/Yuan1z0825/nature-skills) 提供最终尺寸、矢量输出、字体与碰撞检查等工作流启发；本仓库保留两项原始检查工具及 Apache-2.0 许可。研究图与本项目的多轮实际修改形成了组件设计。详见[来源](references/sources.md)、[第三方说明](THIRD_PARTY_NOTICES.md)和 [Apache-2.0 许可](LICENSE)。
