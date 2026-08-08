<div align="center">

# pySurveying

**面向 Python 的轻量级测量计算、测量平差、质量控制与可视化工具包。**

[![tests](https://github.com/hujinghaoabcd/pySurveying/actions/workflows/tests.yml/badge.svg)](https://github.com/hujinghaoabcd/pySurveying/actions/workflows/tests.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)](CHANGELOG.md)

**导线 · 水准 · 交会 · 二维控制网 · 抗差平差 · 粗差筛查 · 误差椭圆 · 坐标转换 · Streamlit GUI**

[English](README.md) · **简体中文**

</div>

---

## 为什么做 pySurveying？

传统测量计算经常散落在教材程序、Excel 表格、一次性脚本和大型专业软件之间。pySurveying 的目标不是再做一个庞大的测绘平台，而是提供一个：

- **足够小**：核心 API 直接、函数优先，便于阅读和修改；
- **足够完整**：不仅算坐标，还包含平差、残差、`Qxx/Qvv`、冗余度、点位精度和误差椭圆；
- **可验证**：提供教材数值回归、透明示例数据和自动化测试；
- **可交互**：内置 Streamlit 界面，不写代码也可以完成常用计算；
- **Python 原生**：基于 NumPy / SciPy / pandas / pyproj，可直接嵌入科研和工程数据处理流程。

> 当前目标版本：**0.3.0 — 首次公开发布准备阶段**。

## 30 秒上手

正式发布到 PyPI 前：

```bash
git clone https://github.com/hujinghaoabcd/pySurveying.git
cd pySurveying
python -m pip install -e .
```

最简单的坐标计算：

```python
from pysurveying import distance, azimuth, forward_coordinate

A = (1000.0, 1000.0)
B = (1100.0, 1050.0)

print(distance(A, B))
print(azimuth(A, B))
print(forward_coordinate(*A, azimuth_deg=30.0, length=100.0))
```

启动可视化界面：

```bash
python -m pip install -e ".[ui]"
pysurveying-ui
```

正式发布后将可直接：

```bash
pip install pysurveying
pip install "pysurveying[ui]"
```

## 当前功能

| 模块 | 当前能力 |
| --- | --- |
| 基础测量计算 | 度分秒、距离、测量方位角、坐标正反算 |
| 交会 | 前方交会、距离交会、二维后方交会 |
| 导线 | 闭合/附合导线、角度闭合差、方位角推算、Bowditch 坐标平差 |
| 水准 | 水准路线、加权水准网平差 |
| 线性平差 | 独立/不等权/完整相关权阵最小二乘 |
| 二维控制网 | 距离、方位角、方向、水平角混合观测 |
| 自由网 / 抗差 | 最小范数自由网、Huber 控制网、Huber/IGG1/IGG3 线性 IRLS |
| 质量控制 | `Qxx`、`Qvv`、冗余度、标准化残差、迭代粗差筛查 |
| 精度评定 | 坐标中误差、点位中误差、置信误差椭圆 |
| 坐标转换 | pyproj CRS、WGS84/ECEF/ENU、二维四参数/六参数 |
| 工程辅助 | 极坐标放样、里程偏距、坡度、设计高程、面积 |
| 数据 IO | CSV、Excel、LandXML 点、Leica GSI 低层记录、Excel 结果导出 |
| GUI | Streamlit 可视化界面 |

## 坐标与角度约定

平面测量函数统一采用：

```text
+Y = 北
+X = 东
方位角 = 从北方向开始顺时针
```

- 平面坐标按 `(x, y)` 传入；
- 对外测量角默认使用十进制度；
- 同一次计算中的线性量必须保持一致单位；
- `Observation.sigma`：距离观测使用坐标线性单位，方位角/方向/水平角使用度。

CRS 转换部分遵循 `pyproj` 约定。

## 四个典型工作流

### 1. 内角闭合导线

```python
from pysurveying import closed_traverse_from_angles

result = closed_traverse_from_angles(
    start=(0.0, 0.0),
    start_azimuth_deg=90.0,
    interior_angles_deg=[90.01, 89.99, 90.02, 89.98],
    distances=[100.02, 99.98, 100.01, 99.99],
)

print(result["angle_adjustment"])
print(result["coordinates"])
```

### 2. 不等权水准网

```python
from pysurveying import LevelObservation, leveling_network

observations = [
    LevelObservation("BM", "A", 1.0000, sigma=0.0010),
    LevelObservation("A", "B", 2.0000, sigma=0.0020),
    LevelObservation("BM", "B", 3.0010, sigma=0.0015),
]

result = leveling_network(observations, {"BM": 100.0})
print(result.metadata["adjusted_heights"])
```

### 3. 二维控制网

```python
import math
from pysurveying import Point, Observation, adjust_control_network

points = [
    Point("A", 0.0, 0.0, fixed=True),
    Point("B", 100.0, 0.0, fixed=True),
    Point("C", 0.0, 100.0, fixed=True),
    Point("P", 39.0, 31.0),
]

observations = [
    Observation("distance", "A", "P", 50.0, sigma=0.01),
    Observation("distance", "B", "P", math.hypot(60, 30), sigma=0.01),
    Observation("distance", "C", "P", math.hypot(40, 70), sigma=0.01),
]

result = adjust_control_network(points, observations)
print(result.metadata["adjusted_points"])
```

### 4. 观测质量与点位精度

```python
from pysurveying import control_network_quality, control_network_precision

print(control_network_quality(result, observations))
print(control_network_precision(result))
```

## 教材数值验证

仓库已经加入宋力杰《测量平差程序设计》的两个精确数值回归：

- §3.1.5 独立观测参数平差；
- §3.2.5 相关观测参数平差（使用教材给出的完整相关权阵）。

运行：

```bash
python examples/textbook_parameter_adjustment.py
```

当前发布诊断覆盖 **52 个自动测试**，同时检查两个可运行示例、Ruff、wheel/sdist 构建和 `twine check`。

详细说明见：

- [`docs/STANDARD_EXAMPLES.md`](docs/STANDARD_EXAMPLES.md)
- [`docs/VALIDATION.md`](docs/VALIDATION.md)

## 示例数据

```text
examples/data/
├── control_points.csv
├── control_observations.csv
├── leveling_fixed.csv
├── leveling_observations.csv
├── traverse_angles.csv
└── common_points.csv
```

这些数据不是 README 装饰，而是会被自动测试实际读取执行。

完整示例：

```bash
python examples/example_data_workflow.py
```

## 可视化 GUI

```bash
pysurveying-ui
```

目前界面包含：

- 基础坐标计算；
- 交会与后方交会；
- 导线；
- 水准路线 / 水准网；
- 二维控制网；
- 观测质量、冗余度、点位精度与粗差筛查；
- 教材平差算例；
- 坐标转换；
- 常用工程测量辅助计算；
- 数据导入、示例 CSV 下载和 Excel 结果导出。

## 文档

| 文档 | 内容 |
| --- | --- |
| [`docs/QUICKSTART.md`](docs/QUICKSTART.md) | 快速上手与完整工作流 |
| [`docs/API.md`](docs/API.md) | 公开 API |
| [`docs/STANDARD_EXAMPLES.md`](docs/STANDARD_EXAMPLES.md) | 教材/外部依据与回归算例 |
| [`docs/VALIDATION.md`](docs/VALIDATION.md) | 数值与统计验证范围 |
| [`docs/ALGORITHMS.md`](docs/ALGORITHMS.md) | 算法说明 |
| [`docs/DATA_FORMATS.md`](docs/DATA_FORMATS.md) | 数据格式 |
| [`docs/FAQ.md`](docs/FAQ.md) | 常见问题 |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | 项目边界与路线图 |
| [`docs/RELEASE.md`](docs/RELEASE.md) | TestPyPI / PyPI 发布流程 |

## 当前明确不扩展的内容

0.3.0 发布前不再继续扩展：

- 大量仪器厂商专有格式；
- 道路/铁路曲线设计系统；
- 土方量平台；
- 变形监测平台；
- GNSS PPP/RTK；
- 摄影测量、点云、SLAM；
- GIS 桌面软件功能。

这不是“忘了开发”，而是为了保持 pySurveying 的定位：**小、清楚、可验证、适合 Python 科学计算工作流。**

## 参与项目

- 贡献指南：[`CONTRIBUTING.md`](CONTRIBUTING.md)
- 使用支持：[`SUPPORT.md`](SUPPORT.md)
- 安全策略：[`SECURITY.md`](SECURITY.md)
- 行为准则：[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)
- 版本历史：[`CHANGELOG.md`](CHANGELOG.md)

## 引用

科研或技术工作中使用 pySurveying 时，可使用 [`CITATION.cff`](CITATION.cff) 中的引用信息。GitHub 识别后会在仓库页面提供 **Cite this repository**。

```text
Hu, Jinghao. pySurveying: Lightweight surveying computation,
adjustment, quality control, and visualization for Python.
https://github.com/hujinghaoabcd/pySurveying
```

## 生产使用说明

pySurveying 适用于教学、科研、算法验证、工程数据检查和小型网络计算。对于法定测量、地籍测量、计量或高等级控制测量，请根据适用规范独立核查观测模型、基准、单位、统计检验和限差。

## License

MIT，见 [`LICENSE`](LICENSE)。
