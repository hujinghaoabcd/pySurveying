# Public launch checklist

This document covers repository presentation and discoverability for the first public pySurveying release. It complements `RELEASE.md`, which covers package publishing mechanics.

## 1. GitHub About description

Recommended repository description:

```text
Lightweight Python toolkit for surveying computation, least-squares adjustment, control networks, robust estimation, quality control, coordinate transformation, and visualization.
```

Shorter alternative:

```text
Lightweight Python toolkit for surveying computation, adjustment, control networks, quality control, and visualization.
```

Avoid a generic description such as `A Python package for surveying` because it loses the searchable technical terms that distinguish the project.

## 2. Recommended GitHub Topics

Use focused topics that match the actual implementation:

```text
python
surveying
geomatics
geodesy
least-squares
least-squares-adjustment
control-network
traverse
leveling
robust-estimation
error-ellipse
coordinate-transformation
geospatial
scientific-computing
streamlit
```

Do not add unrelated high-traffic topics simply for visibility.

## 3. Homepage / website field

Before PyPI publication, leaving the homepage field empty or pointing to the repository is reasonable.

After PyPI publication, either keep the repository as the main homepage or point the field to a future documentation site if one is created.

## 4. Social Preview

Recommended canvas:

```text
1280 × 640 px
```

Suggested composition:

```text
[pySurveying mark/logo]
pySurveying
Lightweight surveying computation & adjustment for Python

Traverse · Leveling · Control Networks · Robust QC · Error Ellipses

[small clean control-network / error-ellipse visual]
```

Design guidance:

- keep the project name readable at small preview sizes;
- use one strong visual instead of many tiny charts;
- avoid excessive “AI/tech” visual effects;
- use a surveying/cartographic visual language rather than generic circuitry;
- reserve enough safe margin for social-card cropping;
- make the image understandable even without reading the README.

## 5. README first screen

The README first screen should answer these questions in roughly ten seconds:

1. What is pySurveying?
2. Which surveying workflows does it cover?
3. Is the project active/tested?
4. How do I install/run it?
5. Why would I use it instead of another script/spreadsheet?

The current README is structured around this sequence:

```text
Project name
→ one-line promise
→ badges
→ searchable feature keywords
→ Why pySurveying?
→ 30-second start
```

## 6. Screenshots / demo media to prepare

Before the first promotion push, capture 1–3 clean GUI screenshots:

### Screenshot A — control-network adjustment

Show:

- point/observation table;
- adjusted coordinates;
- network plot;
- quality/precision tabs.

### Screenshot B — observation quality

Show:

- residuals;
- standardized residuals;
- redundancy numbers;
- flagged observation behavior.

### Screenshot C — textbook example

Show the built-in §3.1.5 or §3.2.5 example with the green “reference reproduced” result.

A short GIF/video can be more effective than many screenshots if it demonstrates:

```text
open GUI → load example → adjust network → inspect residuals → export Excel
```

## 7. Release headline

Recommended English headline:

```text
pySurveying 0.3.0 — a lightweight Python toolkit for surveying adjustment and quality control
```

Recommended Chinese headline:

```text
pySurveying 0.3.0 发布：一个轻量级 Python 测量计算、平差与质量控制工具箱
```

## 8. Short release pitch

### English

```text
pySurveying is a lightweight Python toolkit for traditional surveying computation and adjustment. It covers traverse and leveling workflows, intersections/resection, small 2D control networks, robust estimation, standardized-residual screening, redundancy and error ellipses, coordinate transformations, data helpers, and a Streamlit GUI. The first public release includes textbook-backed least-squares regressions, transparent example datasets, and automated package validation.
```

### 中文

```text
pySurveying 是一个轻量级 Python 测量计算与平差工具包，覆盖导线、水准、交会/后方交会、二维控制网、抗差估计、标准化残差粗差筛查、冗余度、误差椭圆、坐标转换、基础数据读写和 Streamlit 可视化界面。首个公开版本同时提供教材数值回归、透明示例数据和自动化验证，重点是“小、清楚、可复现”。
```

## 9. Longer launch post structure

A good launch post can follow:

```text
Problem
→ why another package is useful
→ 5–8 concrete features
→ screenshot/GIF
→ one installation command
→ 10-line example
→ validation story
→ clear limitations
→ repository link
```

Avoid leading with implementation details or a long development history.

## 10. Search terms to include naturally

Documentation already uses the major terms that target users may search for:

```text
surveying computation
surveying adjustment
least-squares adjustment
control network adjustment
traverse adjustment
leveling network adjustment
robust estimation
Huber
IGG1
IGG3
gross-error detection
standardized residual
redundancy number
error ellipse
coordinate transformation
resection
LandXML
Leica GSI
```

Use full technical names alongside abbreviations when introducing new concepts.

## 11. Release event sequence

Recommended first-public-release sequence:

```text
final docs + screenshots
→ TestPyPI dry run
→ clean install verification
→ production PyPI 0.3.0
→ GitHub Release v0.3.0
→ update README install command / PyPI badge
→ set Social Preview
→ publish launch posts within a short window
→ collect issues and fix real onboarding problems
```

## 12. Promotion channels appropriate to this project

Prioritize communities that actually contain likely users:

- surveying / geomatics / GIS communities;
- Python scientific-computing communities;
- geospatial Python communities;
- university surveying/GIS teaching circles;
- Chinese technical communities such as Zhihu, CSDN, Juejin, WeChat technical accounts when relevant;
- broader developer communities only when the post emphasizes the open-source/software-engineering angle.

Do not post the same promotional copy indiscriminately everywhere. Adapt the first paragraph and example to the audience.

## 13. What not to do

- do not buy or exchange fake stars;
- do not add misleading GitHub topics;
- do not present synthetic tests as external standards;
- do not claim production certification that the package does not have;
- do not promote every repository at once;
- do not turn the README into an exhaustive API dump.

## 14. After the first release

The most useful growth loop is:

```text
users try example
→ onboarding problem becomes issue
→ documentation/test improves
→ patch release
→ release note becomes another discovery event
```

For pySurveying, real independent validation cases and practical teaching examples are likely to create more long-term value than rapidly adding unrelated feature modules.
