# 工具与代码接口

## 环境与后端

在运行绘图脚本的 Python 3.10+ 环境安装 `python -m pip install -r requirements.txt`。
普通绘图使用 Matplotlib、NumPy；PDF 检查与预览使用 PyMuPDF。
组件沿用当前 Matplotlib 后端，不主动切换到 Agg。保留用户的 notebook、交互窗口或其他有效后端；无显示环境可由运行环境选择 Agg。
以下命令在仓库目录执行；从用户项目调用时使用脚本完整路径，并将输出指向用户工作目录。

## 普通单图

将技能目录的 `scripts/` 加入 Python 模块搜索路径后，可直接在现有 Matplotlib 脚本中使用共用接口。
可运行完整示例见 `examples/simple_plot.py`；下面展示已有数组的最短绘图段：

```python
from ohmyplt import configure, apply_chart_style, export
import matplotlib.pyplot as plt

configure()
fig, ax = plt.subplots(figsize=(85 / 25.4, 58 / 25.4), layout="constrained")
ax.plot(x, y)
ax.set(xlabel="Time $t$ (s)", ylabel="Signal $s$ (V)")
apply_chart_style(ax)
export(fig, "output/signal")
```

`configure()` 注册并核查所选字体，修改进程内的 Matplotlib 全局 `rcParams`；应在创建新图前调用。
默认 Arial 普通标签、Times New Roman 数学与数值刻度，项目或用户指定的字体优先。
修改已有图时检查其现存标签、图例和注释对象；全局设置不会自动重设所有对象。
`apply_chart_style(ax, boxed=False)` 调整轴线、刻度与字体。空间场等需要完整边框时使用 `boxed=True`。

| 共用接口 | 用途 |
|---|---|
| `configure(body_font, math_font, font_dir)` | 注册字体并设置全局绘图起点 |
| `apply_chart_style(ax, boxed=False)` | 轻量轴样式；`boxed=True` 显示完整边框 |
| `check_axes_alignment(fig, axes, mode)` | 比较相同布局要求的绘图区，默认容差1.5 pt |
| `export(fig, stem, formats, dpi, source_files)` | 导出格式并记录字体、尺寸、输入哈希与警告 |

`export()` 默认输出 PDF、SVG、PNG；可用 `formats=("svg", "png")` 等元组选择需要的格式。
SVG 保留普通文本，PDF 嵌入所用字体；SVG 的字体替换可能影响布局。源码与数据保存在研究项目中，按实际导出结果检查。

## 选择可运行示例

```bash
python scripts/quickstart.py --portable --out output
python scripts/quickstart.py --example calibration --portable --out output
```

默认 `--example simple` 只生成一张普通数据图。`--portable` 明确选择 Matplotlib 自带的 DejaVu Sans/Serif。
省略它使用默认 Arial/Times；也可指定 `--body-font` 与 `--math-font`。

| `--example` | 绘图入口 | 输出文件前缀 |
|---|---|---|
| `simple` | `examples/simple_plot.py` | `simple-plot` |
| `calibration` / `spectrum` / `heatmap` / `distribution` | `examples/scientific_plots.py --kind 类型` | 对应类型名 |
| `data` | `examples/data_plot.py` | `data-plot` |
| `optical` | `examples/optical_schematic.py` | `optical-schematic` |
| `comparison` | `examples/style_comparison.py` | `style-comparison` |
| `network` | `examples/network.py` | `network` |

科研配方可独立运行 `python examples/scientific_plots.py --kind spectrum --out output`；`--kind` 可选四种类型或 `all`。
输出路径相对于调用目录，也可使用绝对路径。示例保存合成数据、图注和清单。
需要检查某张示例时加 `--check`；开发或 CI 才显式运行全量：

```bash
python scripts/quickstart.py --example all --portable --check --out output
```

## 字体与检查工具

`--font-dir /path/to/fonts` 或 `OHMYPLT_FONT_DIR` 可注册自备 TTF/OTF 文件，字体文件由使用者提供。
遇到缺字、字体替换或指定字族问题时，按需运行：

```bash
python scripts/doctor.py
python scripts/doctor.py --glyphs "Σθη∂←→×"
```

doctor 检查字体文件与字形覆盖；以实际字体结果决定字形或排版方案。
各层检查的选择见[质量检查](quality.md)。需要 PDF 字高、碰撞与字体信息，或最终尺寸/局部预览时可独立调用：

```bash
python scripts/preflight.py output/figure.pdf --out output/qa --min-pt 5
python scripts/preflight.py output/figure.pdf --out output/qa --allow-font Arial --allow-font TimesNewRoman
python scripts/preview.py output/figure.pdf --out output/final-size.png --dpi 108
python scripts/preview.py output/figure.pdf --out output/detail.png --dpi 288 --clip-mm 40 30 22 18
```

`--min-pt` 按成图与实际要求调整。裁剪参数为左、下、宽、高，单位 mm、左下角原点。
preflight 调用随仓库保存的 Nature Figure 字高与碰撞工具，日志和 JSON 报告写入所选目录。
非零退出码对应需要定位的具体问题；结合当前图的结构检查相关文字与几何。

## 可选：结构示意组件

实验对象、方法流程或模型架构需要自由摆放时，使用 `Plate`。原点在左下角，坐标单位 mm，字号和线宽单位 pt。

```python
from ohmyplt import Plate, configure, export
configure()
p = Plate(183, 90)
p.card(10, 30, 24, 16, z=3)
p.text(22, 38, "Acquire", ha="center")
p.card(49, 30, 30, 16, z=3)
p.text(64, 38, "Calibrate", ha="center")
p.wire([(34, 38), (49, 38)])
export(p.fig, "output/schematic")
```

| `Plate` 接口 | 用途 |
|---|---|
| `Plate(width_mm, height_mm)` | 毫米坐标画布 |
| `text(x, y, label, size=None, ...)` | 普通标签默认7 pt，含数学默认7.5 pt |
| `card(x, y, w, h, ..., z)` | 分组或操作区域，按层级放置 |
| `port(x, y, vertical=True)` | 给分组边框留开口，贯通线另行绘制 |
| `wire(points, r=1.7, head=5, ...)` | 连续圆角路径、端点与线型 |
| `sigma(x, y, radius=2.6)` | 几何居中的 Times Σ，返回四个圆周端口 |
| `matrix(..., A, contrast=False, columns=False)` | 权重示意与实际显示的采样矩阵 |
| `history(..., t, signals, features)` | 按时间排列的采样曲线与特征 |
| `gru(..., wi, wh)` | PyTorch r/z/n 顺序的输入/递归权重 |
| `dense(..., W, b)` | 代表神经元、带权连接和偏置 |
| `linear(..., W, b)` | 仿射矩阵、偏置与形状 |
| `gelu(x, y, w, h)` | erf 定义的 GELU 曲线 |

组件用法见 `examples/network.py`，具体规则见[结构示意](architecture.md)。
`matrix(contrast=True)` 使用有符号平方根，`columns=True` 按列归一；它们用于结构展示，数值比较采用有定义的统一尺度与色条。
架构案例的 NumPy 前向计算见 `examples/residual_model.py`。18 秒导览由 `scripts/build_demo.py` 从实际导出文件合成，重建另需 ffmpeg。
