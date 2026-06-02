# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LaTeX PhD dissertation for Northeastern University (Shenyang, China), based on the [NEU-Thesis](https://github.com/sci-m-wang/NEU-Thesis) template. The thesis covers real-time train rescheduling methods for intercity high-speed railways under passenger flow disturbances, using advanced control theory (RMPC, ILC, fuzzy/T-S model, IL-FPC).

## Build Commands

```bash
# Quick compile (no bibliography)
xelatex --output-directory=Tmp main.tex

# Full build with bibtex bibliography
bash build.sh ab

# Full build with biber bibliography
bash build.sh bb

# Build without bibliography processing
bash build.sh x
```

The build script uses `xelatex` as the compiler and outputs intermediate files to `Tmp/`. The output PDF is `main.pdf`.

## Architecture

### Document class (`Style/neuthesis.cls`)
Custom class built on `ctexbook`, loaded as `\documentclass[printcopy,fontset=windows]{Style/neuthesis}`. Supports options:
- Layout: `singlesided`, `doublesided`, `printcopy`
- Draft: `draftversion` (shows version info watermark)
- Review: `review` (blind review mode, hides author info)
- Font: `fontset=<windows|mac|adobe|fandol>`

### Style packages
- **`Style/artratex.sty`** — Modular style package loaded with options: `bibtex`/`biber`, `myhdr` (headers/footers), `table`, `list`, `geometry`, `math`.
- **`Style/artracom.sty`** — User-defined convenience commands.
- **`Style/neuthesis.cfg`** — Chinese localization strings.

### Document structure (`main.tex`)
1. **Frontmatter** — `Tex/Frontpages.tex` (cover page), `Tex/Abstract.tex` (Chinese + English abstracts), TOC, figure/table lists
2. **Mainmatter** — `Tex/Mainmatter.tex` includes: `Chap_Intro` (introduction), `Chap_03`~`Chap_07` (content chapters)
3. **Backmatter** — Bibliography (`Biblio/ref.bib`, GB/T 7714 format), `Tex/Backmatter.tex` (acknowledgments, publications)

### Thesis Chapters
- Chap_01: 符号和缩写说明 (Symbols and Abbreviations)
- Chap_Intro: 绪论 (Introduction — literature review, research status)
- Chap_03: 状态空间建模 (State-space modeling for M>N scenarios)
- Chap_04: 鲁棒模型预测控制/RMPC (Robust MPC under uncertain passenger flow)
- Chap_05: 迭代学习控制/ILC + 模糊逻辑 (ILC + Fuzzy for abrupt passenger flow)
- Chap_06: 迭代学习模糊预测控制/IL-FPC (Iterative Learning Fuzzy Predictive Control)
- Chap_07: 总结与展望 (Conclusions and Future Work)

### Template-only files (not part of the thesis)
- `Tex/Chap_Guide.tex` — LaTeX usage guide (template documentation, commented out in Mainmatter)
- `Tex/Chap_Format.tex` — Formatting specification (template documentation, commented out in Mainmatter)
- `Tex/Chap_02.tex` / `Tex/Chap_02_new.tex` — Template chapter, not in use

### Fonts
Chinese fonts (SimSun, SimHei, SimKai, SimFang) are bundled as `.ttf`/`.ttc` files for compilation compatibility.

### Key data points to update
Title page fields in `Tex/Frontpages.tex`: `\title`, `\author`, `\advisor`, `\degree`, `\degreetype`, `\major`, `\institute`, `\authorno`, dates, and English equivalents. Items marked `TODO` need to be filled in.

### Conditional content
`\reviewORprint{<review>}{<print>}` toggles content between blind review and final print modes.
