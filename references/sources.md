# 借鉴来源

## 使用过的skill

| 来源 | 吸收的做法 | 本skill的实现 |
|---|---|---|
| [nature-skills / nature-figure](https://github.com/Yuan1z0825/nature-skills/tree/6827ae57b62b201acd06b401619050411c0d82f6/skills/nature-figure) | 最终物理尺寸、内容层级、矢量输出、实际字高与碰撞、源数据记录 | 保留两项原始PDF检查工具；把构图经验适配到用户认可的字体与功能图形 |
| Codex `skill-creator` | 简洁入口、按需阅读、可运行资源、验证完整性 | SKILL.md与专项references分离，工具自包含，自动发现 |

Nature Figure使用的固定提交为`6827ae57b62b201acd06b401619050411c0d82f6`。相关文件的URL与哈希记录在`vendor/nature_figure/UPSTREAM.json`，许可见同目录LICENSE。

## 研究图的组织参考

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)：模块边界、残差与分支、参数重复、简洁标签和功能层级。
- [SHPNet, EAAI 2025](https://doi.org/10.1016/j.engappai.2025.112496)：表征/历史反演分阶段、耦合潜变量、共享解码及各物理场输出。图4由用户提供的全文核对。
- [NeuralGCM, Fig.1](https://www.nature.com/articles/s41586-024-07744-y/figures/1)：物理对象与算法的连接、整体与局部展开。
- [Senseiver, Fig.1](https://www.nature.com/articles/s42256-023-00746-x/figures/1)：传感器、观测与全场输出的对应。
- [SHRED-ROM, Fig.1](https://www.nature.com/articles/s41467-025-65126-y/figures/1)：物理切片、传感历史、时序网络与压缩表示。

## 排版与导出参考

- [Nature preparing figures](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/)
- [Nature building and exporting figure panels](https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/)
- [NIST symbol and type conventions](https://www.nist.gov/pml/special-publication-811/nist-guide-si-chapter-10-more-printing-and-using-symbols-and-numbers)
- [Matplotlib Mathtext](https://matplotlib.org/stable/users/explain/text/mathtext.html)

Arial正文、Times New Roman数学、Σ节点、圆角贯通路径和物理/时间输入的保留，来自本项目多轮审阅形成的用户偏好。上面的论文提供组织思路，示例PNG为本项目原创图稿。

示例PNG：`assets/approved-network-v19.png`，SHA-256：`7963d4a5c45e11e7d0cde7e20362e00ebf15eae1da64177e718bb71f2b81d5ac`。发布于2026-10-20，原图V19。
