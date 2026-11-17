# 借鉴来源

## 使用过的skill

| 来源 | 吸收的做法 | 本skill的实现 |
|---|---|---|
| [nature-skills / nature-figure](https://github.com/Yuan1z0825/nature-skills/tree/6827ae57b62b201acd06b401619050411c0d82f6/skills/nature-figure) | 最终物理尺寸、内容层级、矢量输出、实际字高与碰撞、源数据记录 | 保留两项原始PDF检查工具；把构图经验适配到用户认可的字体与功能图形 |
| Codex `skill-creator` | 简洁入口、按需阅读、可运行资源、验证完整性 | SKILL.md与专项references分离，工具自包含，自动发现 |

Nature Figure使用的固定提交为`6827ae57b62b201acd06b401619050411c0d82f6`。相关文件的URL与哈希记录在`vendor/nature_figure/UPSTREAM.json`，许可见同目录LICENSE。

## 研究图的组织参考

- [FlashAttention, NeurIPS 2022](https://proceedings.neurips.cc/paper_files/paper/2022/file/67d57c32e20fd0a7a302cb81d36e40d5-Paper-Conference.pdf)，图1：把存储层级、计算方法和运行时间按阅读关系排列，标签贴近对象，小型柱图直接标注。
- [FlashAttention-2, ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/file/98ed250b203d1ac6b24bbcf263e3d4a7-Paper-Conference.pdf)，图2--4：面板来自真实比较维度，同一对象跨面板保持编码，数据区及可比尺度协调。以上为对论文图形的编辑判断，按实际输出尺寸重新安排文字密度。

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)：模块边界、残差与分支、参数重复、简洁标签和功能层级。
- [SHPNet, EAAI 2025](https://doi.org/10.1016/j.engappai.2025.112496)：表征/历史反演分阶段、耦合潜变量、共享解码及各物理场输出。图4由用户提供的全文核对。
- [NeuralGCM, Fig.1](https://www.nature.com/articles/s41586-024-07744-y/figures/1)：物理对象与算法的连接、整体与局部展开。
- [Senseiver, Fig.1](https://www.nature.com/articles/s42256-023-00746-x/figures/1)：传感器、观测与全场输出的对应。
- [SHRED-ROM, Fig.1](https://www.nature.com/articles/s41467-025-65126-y/figures/1)：物理切片、传感历史、时序网络与压缩表示。

## 排版与导出参考

- [NeurIPS 2026官方模板](https://media.neurips.cc/Conferences/NeurIPS2026/Formatting_Instructions_For_NeurIPS_2026.zip)：正文宽139.7 mm，图应清楚可辨、线条适合复制、图注在图下，PDF采用Type 1或嵌入的TrueType字体。
- [ICLR 2027官方模板](https://media.iclr.cc/Conferences/ICLR2027/iclr-2027-style-files.zip)：正文宽139.7 mm，图应清楚、整洁、可辨，图与下方图注保持在一起。
- [NeurIPS 2021作者无障碍指南](https://neurips.cc/Conferences/2021/PaperInformation/Author-Guidelines)：历史官方建议，包括高对比、颜色之外的识别方式、足够大的图内文字、字体嵌入与替代文本。按年份及建议性质使用。
- [Okabe与Ito的Color Universal Design](https://jfly.uni-koeln.de/color/index.html)：具名定性调色板与颜色之外的辅助识别。
- [Paul Tol的颜色方案](https://sronpersonalpages.nl/~pault/)：high-contrast、bright等定性配色的原始定义与使用说明。
- [Matplotlib色图说明](https://matplotlib.org/stable/users/explain/colors/colormaps.html)：数据含义、明度与顺序/发散色图的选择。
- [Matplotlib字体与导出](https://matplotlib.org/stable/users/explain/text/fonts.html)：PDF字体嵌入与SVG活文字/路径输出。
- [清华校徽规范](https://vi.tsinghua.edu.cn/gk/xxbz/xh.htm)、[标准组合](https://vi.tsinghua.edu.cn/gk/xxbz/bzzh1.htm)：官方标志的比例、颜色、字样、组合与最小尺寸。具体约束按具体机构核定。

- [Nature preparing figures](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/)
- [Nature building and exporting figure panels](https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/)
- [NIST symbol and type conventions](https://www.nist.gov/pml/special-publication-811/nist-guide-si-chapter-10-more-printing-and-using-symbols-and-numbers)
- [Matplotlib Mathtext](https://matplotlib.org/stable/users/explain/text/mathtext.html)

Arial说明文字、Times New Roman数学是本项目的默认排版选择，项目与期刊约定可覆盖。Σ节点、圆角路径和物理/时间输入的保留，来自具体架构图的多轮审阅；这些局部表达按当前图的内容选用。上面的论文提供示意图组织思路，示例PNG为本项目原创图稿。

示例PNG：`assets/approved-network-v19.png`，SHA-256：`7963d4a5c45e11e7d0cde7e20362e00ebf15eae1da64177e718bb71f2b81d5ac`。发布于2026-10-20，原图V19。
