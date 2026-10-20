# 工具与代码接口

## 运行环境

`pip install -r requirements.txt`安装Matplotlib、NumPy、PyMuPDF。默认使用系统的Arial与Times New Roman，字体文件由使用者提供；可用`--font-dir /path/to/fonts`或`OHMYPLT_FONT_DIR`注册本地字体。

```bash
python scripts/doctor.py
python scripts/doctor.py --glyphs "Σθη∂←→×"
```

doctor检查字体文件和字形覆盖。Windows自带Times可能缺少∈、∇；实际字体的检查结果决定写法。Linux功能测试可显式使用Liberation Sans/Serif；正式图按用户指定字体渲染。

## 毫米坐标组件

在脚本中把`scripts/`加入模块路径，导入`ohmyplt`。`Plate`使用左下角原点、毫米坐标；字体和线宽使用pt。

```python
from ohmyplt import Plate, configure, export
configure()
p = Plate(183, 90)
p.card(10, 30, 24, 16, z=3)
p.text(22, 38, 'Encoder', ha='center')
ports = p.sigma(50, 38)
p.wire([(34, 38), ports['left']])
p.wire([ports['right'], (67, 38)])
export(p.fig, 'output/figure')
```

| 接口 | 用途 |
|---|---|
| `configure(body_font, math_font, font_dir)` | 注册/核查字体，统一Matplotlib数学配置 |
| `Plate(width_mm, height_mm)` | 白底物理尺寸画布 |
| `text(x,y,label,size=None,...)` | 普通标签默认7 pt，含数学默认7.5 pt |
| `card(x,y,w,h,...,z)` | 分组或操作节点；组通常z<1，操作节点z=3 |
| `port(x,y,vertical=True)` | 在分组边框开口；贯通线另行绘制 |
| `wire(points,r=1.7,head=5,...)` | 整条圆角路径，首尾精确，支持线型与层级 |
| `sigma(x,y,radius=2.6)` | TimesΣ几何居中，返回四个圆周端口 |
| `matrix(...,A,contrast=False,columns=False)` | 有符号权重图形；返回实际显示的采样矩阵 |
| `history(...,t,signals,features)` | 采样曲线与逐时特征；前两数组按时间递增 |
| `gru(...,wi,wh)` | 接受PyTorch顺序的三组GRU输入/递归权重 |
| `dense(...,W,b)` | 代表神经元、带权连接、常数偏置入口 |
| `linear(...,W,b)` | 矩阵、偏置、形状与仿射运算 |
| `gelu(x,y,w,h)` | 实际erf定义的GELU曲线 |
| `apply_chart_style(ax)` | 简洁轴线与Times数字刻度 |
| `check_axes_alignment(fig,axes,mode)` | 核对同一比较组的绘图区，默认容差1.5 pt |
| `export(fig,stem,formats,dpi,source_files)` | 输出所需格式，记录字体、尺寸、输入哈希与警告 |

组件默认尺寸参考`examples/network.py`。改变节点宽高后，检查标签、图形和连线间距。`matrix(contrast=True)`使用有符号平方根；`columns=True`按列归一，适合结构示意。数值比较图使用统一标度与色条。

## PDF检查与局部预览

```bash
python scripts/preflight.py output/figure.pdf --out output/qa --min-pt 5
python scripts/preflight.py output/figure.pdf --out output/qa --allow-font Arial --allow-font TimesNewRoman
python scripts/preview.py output/figure.pdf --out output/final-size.png --dpi 108
python scripts/preview.py output/figure.pdf --out output/merge.png --dpi 288 --clip-mm 40 30 22 18
```

裁剪参数为左、下、宽、高，单位mm，与Plate同为左下角原点。108 dpi预览用于小尺寸目视，局部放大用于查看箭头、Σ与上下标。

preflight运行随仓库保存的Nature Figure字高与碰撞检查。日志和JSON报告位于输出的qa目录；非零退出码要求修复或进一步检查具体问题。检查对象是实际PDF中的文字与几何。

## 示例与扩展

`examples/network.py`演示采样、固定支路、可训练时序模块、Σ与更新回路。`examples/data_plot.py`演示配对案例、时间预测和重复面板对齐。输入由固定种子生成，保存到输出NPZ。

SVG可保留普通文本，PDF嵌入实际字体；字体替换会改变可编辑SVG的布局。精确的最终展示以导出的PNG/PDF预览为参照。示例图PNG在仓库中作为风格参考；新图按自己的方法与数据生成。
