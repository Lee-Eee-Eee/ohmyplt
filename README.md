# ohmyplt

**Draw the method, down to the operations.**

An agent skill for scientific architecture diagrams and research plots. Turn model code, sketches, or plotting scripts into figures with meaningful components, precise routing, SVG with editable text, and PDF/PNG exports backed by Python source.

[简体中文](README.zh-CN.md) · [Install](#install) · [Quickstart](#quickstart) · [Gallery](#gallery)

[![Figure tests](https://github.com/Lee-Eee-Eee/ohmyplt/actions/workflows/smoke.yml/badge.svg)](https://github.com/Lee-Eee-Eee/ohmyplt/actions/workflows/smoke.yml)
[![Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

![Scientific architecture with physical inputs, sampling, shared decoding and training paths](assets/approved-network-v19.png)

A research-project figure that shaped this skill. The examples below demonstrate its reusable components.

## What you can draw

- **Model architectures:** sampled histories, GRU gates, weighted connections, biases, affine maps, residual sums, and training paths matched to the implementation.
- **Physical schematics:** objects connected to sensors, observations, models, and outputs.
- **Research plots:** paired cases, time series, aligned panels, and explicit units and statistical meaning.

Layouts use millimetres. Default typography is Arial for labels and Times New Roman for mathematics. Rounded paths meet explicit node ports. SVG keeps text editable, PDF embeds fonts, and Python source keeps the figure reproducible.

## Install

With the [Skills CLI](https://github.com/vercel-labs/skills) and Node.js 22.20+:

```bash
npx skills add Lee-Eee-Eee/ohmyplt --skill ohmyplt
```

Choose your agent when prompted; add `-g` for installation across projects. Install the Python dependencies in the environment that will run the scripts. For a manual Codex installation:

```bash
git clone https://github.com/Lee-Eee-Eee/ohmyplt.git ~/.codex/skills/ohmyplt
python -m pip install -r ~/.codex/skills/ohmyplt/requirements.txt
```

Invoke `$ohmyplt` in Codex. Other agents can load [SKILL.md](SKILL.md) through their own skill mechanism.

## Quickstart

Python 3.10+ is required. Clone into a working folder and generate three examples:

```bash
git clone https://github.com/Lee-Eee-Eee/ohmyplt.git
cd ohmyplt
python -m pip install -r requirements.txt
python scripts/quickstart.py --portable --out output
```

`--portable` explicitly selects Matplotlib's bundled DejaVu Sans/Serif. For the default Arial/Times style, use `python scripts/quickstart.py --out output`. Register your own fonts with `--font-dir PATH`, or choose `--body-font` and `--math-font` explicitly.

Open `output/network.png`, `output/data-plot.png`, and `output/style-comparison.png`. The folder also contains SVG/PDF files, sample data, font and input manifests, final-size previews, and PDF inspection reports. The output path is relative to where you run the command.

## Gallery

### Functional architecture

![Sampled history, fixed and trainable branches, GRU and affine maps, a residual sum and a loss update path](assets/gallery/network.png)

[Python](examples/network.py) · [SVG](assets/gallery/network.svg) · [PDF](assets/gallery/network.pdf)

Seeded demonstration signals and weights show how components represent operations. Reproduce: `python examples/network.py --out output`.

### Research data panels

![Paired observations and a sampled time forecast in aligned plotting areas](assets/gallery/data-plot.png)

[Python](examples/data_plot.py) · [SVG](assets/gallery/data-plot.svg) · [PDF](assets/gallery/data-plot.pdf)

Paired observations and a sampled signal use deterministic demonstration data. Reproduce: `python examples/data_plot.py --out output`.

### Same data, two styles

![Default Matplotlib and ohmyplt styles applied to identical data and axis ranges](assets/gallery/style-comparison.png)

[Python](examples/style_comparison.py) · [SVG](assets/gallery/style-comparison.svg) · [PDF](assets/gallery/style-comparison.pdf)

Both panels use identical data, scales, limits, and labels. The left uses Matplotlib defaults; the right applies ohmyplt. Reproduce: `python examples/style_comparison.py --out output`.

The ohmyplt-styled gallery elements use Arial/Times; the comparison baseline keeps Matplotlib defaults. Individual examples accept font arguments; the portable quickstart supplies bundled fonts to all three.

## Prompts to start with

**From model code**

```text
Use $ohmyplt to draw the architecture in model.py at 183 mm width.
Check input/output shapes, branches, biases, shared parameters, and the loss path.
Export SVG, PDF, PNG, and Python source.
```

**From a sketch**

```text
Use $ohmyplt to turn this sketch into a scientific schematic.
Keep the physical object, sensor locations, and data-flow relationships.
Use rounded port-based connections and export editable SVG plus Python source.
```

**From existing results**

```text
Use $ohmyplt to refine plot_results.py using the existing data.
Keep units, scales, pairing, and uncertainty definitions.
Align the comparison panels and inspect the PDF at its final size.
```

## Drawing and inspection tools

Helpers provide millimetre primitives, font/glyph inspection, PDF text-size and collision checks, and final-size/crop previews. See the [tools reference](references/tools.md). Automated findings guide the final visual check.

[Open a figure issue](https://github.com/Lee-Eee-Eee/ohmyplt/issues/new/choose) with a minimal script, safe sample input, and expected result. English and Chinese are welcome.

## Credits and license

[Nature Figure skill](https://github.com/Yuan1z0825/nature-skills) informed the final-size, vector-export, font, and collision-inspection workflow. Two original inspection tools and their Apache-2.0 license are retained. Research diagrams and this project's drawing iterations informed the component design. See [sources](references/sources.md), [third-party notices](THIRD_PARTY_NOTICES.md), and the [Apache-2.0 license](LICENSE).
