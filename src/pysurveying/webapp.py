from __future__ import annotations

import math
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from matplotlib.patches import Ellipse

from pysurveying.adjustment import (
    adjust_control_network,
    adjust_free_network,
    least_squares,
)
from pysurveying.basic import (
    azimuth,
    distance,
    distance_intersection,
    forward_coordinate,
    forward_intersection,
    resection,
)
from pysurveying.engineering import polygon_area, polar_stakeout, slope
from pysurveying.io import read_csv, read_excel, read_gsi, read_landxml_points
from pysurveying.leveling import leveling_route
from pysurveying.models import Observation, Point
from pysurveying.quality import (
    detect_outliers,
    error_ellipse,
    robust_least_squares,
    standardized_residuals,
)
from pysurveying.transform import transform_coordinates
from pysurveying.traverse import closed_traverse, connected_traverse

st.set_page_config(page_title="pySurveying", page_icon="📐", layout="wide")
st.title("pySurveying")
st.caption("轻量级测量计算、测量平差与可视化工具包")

page = st.sidebar.radio(
    "功能",
    [
        "基础计算",
        "交会与后方交会",
        "导线",
        "水准",
        "控制网",
        "平差与质量",
        "坐标转换",
        "工程测量",
        "数据格式",
    ],
)


def _network_plot(point_table: pd.DataFrame, observation_table: pd.DataFrame, adjusted=None):
    coordinates = {
        str(row["name"]): (float(row["x"]), float(row["y"]))
        for _, row in point_table.iterrows()
    }
    if adjusted:
        coordinates.update(adjusted)

    fig, ax = plt.subplots()
    drawn = set()
    for _, row in observation_table.iterrows():
        station = str(row["from_point"])
        target = str(row["to_point"])
        if station in coordinates and target in coordinates:
            edge = tuple(sorted((station, target)))
            if edge not in drawn:
                x1, y1 = coordinates[station]
                x2, y2 = coordinates[target]
                ax.plot([x1, x2], [y1, y2], linewidth=0.8)
                drawn.add(edge)
        target2 = row.get("target2")
        if pd.notna(target2) and str(target2).strip() and station in coordinates:
            target2 = str(target2)
            if target2 in coordinates:
                edge = tuple(sorted((station, target2)))
                if edge not in drawn:
                    x1, y1 = coordinates[station]
                    x2, y2 = coordinates[target2]
                    ax.plot([x1, x2], [y1, y2], linewidth=0.8)
                    drawn.add(edge)

    for name, (x, y) in coordinates.items():
        ax.scatter([x], [y])
        ax.annotate(name, (x, y))
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    return fig


if page == "基础计算":
    st.subheader("两点坐标计算")
    col1, col2 = st.columns(2)
    with col1:
        x1 = st.number_input("X1", value=1000.0)
        y1 = st.number_input("Y1", value=1000.0)
    with col2:
        x2 = st.number_input("X2", value=1100.0)
        y2 = st.number_input("Y2", value=1050.0)
    m1, m2 = st.columns(2)
    m1.metric("距离", f"{distance((x1, y1), (x2, y2)):.4f}")
    m2.metric("方位角", f"{azimuth((x1, y1), (x2, y2)):.6f}°")

    st.subheader("坐标正算")
    angle = st.number_input("方位角(°)", value=30.0)
    length = st.number_input("距离", value=100.0)
    if st.button("计算坐标"):
        x, y = forward_coordinate(x1, y1, angle, length)
        st.success(f"X={x:.4f}, Y={y:.4f}")

elif page == "交会与后方交会":
    tab1, tab2, tab3 = st.tabs(["前方交会", "距离交会", "后方交会"])
    with tab1:
        p1x = st.number_input("P1 X", value=0.0, key="f1x")
        p1y = st.number_input("P1 Y", value=0.0, key="f1y")
        a1 = st.number_input("P1 方位角", value=45.0)
        p2x = st.number_input("P2 X", value=100.0, key="f2x")
        p2y = st.number_input("P2 Y", value=0.0, key="f2y")
        a2 = st.number_input("P2 方位角", value=315.0)
        if st.button("前方交会"):
            x, y = forward_intersection((p1x, p1y), a1, (p2x, p2y), a2)
            st.success(f"P = ({x:.4f}, {y:.4f})")
    with tab2:
        p1x = st.number_input("P1 X", value=0.0, key="d1x")
        p1y = st.number_input("P1 Y", value=0.0, key="d1y")
        r1 = st.number_input("P1 距离", value=70.710678)
        p2x = st.number_input("P2 X", value=100.0, key="d2x")
        p2y = st.number_input("P2 Y", value=0.0, key="d2y")
        r2 = st.number_input("P2 距离", value=70.710678, key="r2")
        if st.button("距离交会"):
            q1, q2 = distance_intersection((p1x, p1y), r1, (p2x, p2y), r2)
            st.write("解 1", q1)
            st.write("解 2", q2)
    with tab3:
        st.caption("每行输入 X,Y,观测方向(°)，至少 3 行。")
        text = st.text_area(
            "已知点与方向",
            "0,0,225\n100,0,135\n100,100,45\n0,100,315",
        )
        if st.button("后方交会"):
            rows = [
                [float(value) for value in row.split(",")]
                for row in text.splitlines()
                if row.strip()
            ]
            station = resection([(row[0], row[1]) for row in rows], [row[2] for row in rows])
            st.success(
                f"X={station[0]:.4f}, Y={station[1]:.4f}, 定向={station[2]:.6f}°"
            )

elif page == "导线":
    st.subheader("导线 Bowditch 平差")
    mode = st.radio("类型", ["闭合导线", "附合导线"], horizontal=True)
    sx = st.number_input("起点 X", value=1000.0)
    sy = st.number_input("起点 Y", value=1000.0)
    end = None
    if mode == "附合导线":
        ex = st.number_input("终点 X", value=1200.0)
        ey = st.number_input("终点 Y", value=1200.0)
        end = (ex, ey)
    table = st.data_editor(
        pd.DataFrame(
            {
                "azimuth_deg": [90.0, 0.0, 270.0, 180.0],
                "distance": [100.0, 100.0, 100.0, 100.0],
            }
        ),
        num_rows="dynamic",
        use_container_width=True,
    )
    if st.button("平差导线"):
        if mode == "闭合导线":
            result = closed_traverse((sx, sy), table.azimuth_deg, table.distance)
        else:
            result = connected_traverse((sx, sy), end, table.azimuth_deg, table.distance)
        c1, c2, c3 = st.columns(3)
        c1.metric("fx", f"{result['misclosure_x']:.6f}")
        c2.metric("fy", f"{result['misclosure_y']:.6f}")
        ratio = result["relative_precision"]
        c3.metric("相对精度", "∞" if math.isinf(ratio) else f"1:{ratio:.0f}")
        coordinates = pd.DataFrame(result["coordinates"], columns=["X", "Y"])
        st.dataframe(coordinates, use_container_width=True)
        fig, ax = plt.subplots()
        ax.plot(coordinates["X"], coordinates["Y"], marker="o")
        for index, row in coordinates.iterrows():
            ax.annotate(str(index), (row["X"], row["Y"]))
        ax.set_aspect("equal", adjustable="datalim")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        st.pyplot(fig)

elif page == "水准":
    st.subheader("水准路线平差")
    h0 = st.number_input("起点高程", value=10.0)
    has_end = st.checkbox("已知终点高程", value=True)
    hend = st.number_input("终点高程", value=10.0) if has_end else None
    table = st.data_editor(
        pd.DataFrame({"dh": [1.002, -0.501, -0.503], "length": [1.0, 1.0, 1.0]}),
        num_rows="dynamic",
        use_container_width=True,
    )
    if st.button("平差水准路线"):
        result = leveling_route(h0, table.dh, end_height=hend, lengths=table.length)
        st.metric("闭合差", f"{result['misclosure']:.6f}")
        st.dataframe(
            pd.DataFrame(
                {"point": range(len(result["heights"])), "height": result["heights"]}
            ),
            use_container_width=True,
        )

elif page == "控制网":
    st.subheader("二维控制网平差")
    st.caption("支持 distance、azimuth 和 angle。angle 中 target2 为前视点。")
    free_network = st.checkbox("自由网（最小范数解）", value=False)

    default_points = pd.DataFrame(
        {
            "name": ["A", "B", "C", "P"],
            "x": [0.0, 100.0, 0.0, 39.0],
            "y": [0.0, 0.0, 100.0, 31.0],
            "fixed": [True, True, True, False],
        }
    )
    point_table = st.data_editor(
        default_points,
        num_rows="dynamic",
        use_container_width=True,
        key="network_points",
    )

    default_observations = pd.DataFrame(
        {
            "kind": ["distance", "distance", "distance"],
            "from_point": ["A", "B", "C"],
            "to_point": ["P", "P", "P"],
            "target2": ["", "", ""],
            "value": [50.0, 67.082039325, 80.622577483],
            "sigma": [0.01, 0.01, 0.01],
        }
    )
    observation_table = st.data_editor(
        default_observations,
        num_rows="dynamic",
        use_container_width=True,
        key="network_observations",
    )

    if st.button("平差控制网"):
        points = [
            Point(
                str(row["name"]),
                float(row["x"]),
                float(row["y"]),
                fixed=False if free_network else bool(row["fixed"]),
            )
            for _, row in point_table.iterrows()
        ]
        observations = []
        for _, row in observation_table.iterrows():
            target2 = row.get("target2")
            target2 = None if pd.isna(target2) or not str(target2).strip() else str(target2)
            observations.append(
                Observation(
                    kind=str(row["kind"]),
                    from_point=str(row["from_point"]),
                    to_point=str(row["to_point"]),
                    target2=target2,
                    value=float(row["value"]),
                    sigma=float(row["sigma"]),
                )
            )
        result = (
            adjust_free_network(points, observations)
            if free_network
            else adjust_control_network(points, observations)
        )
        adjusted = result.metadata["adjusted_points"]
        output = pd.DataFrame(
            [{"name": name, "x": xy[0], "y": xy[1]} for name, xy in adjusted.items()]
        )
        c1, c2, c3 = st.columns(3)
        c1.metric("收敛", "是" if result.converged else "否")
        c2.metric("迭代次数", result.iterations)
        c3.metric("σ₀", "—" if result.sigma0 is None else f"{result.sigma0:.6f}")
        st.dataframe(output, use_container_width=True)
        st.write("标准化观测残差", result.residuals)
        st.pyplot(_network_plot(point_table, observation_table, adjusted))

        if result.covariance is not None:
            unknown_names = result.metadata["point_order"]
            ellipse_rows = []
            for index, name in enumerate(unknown_names):
                block = result.covariance[index * 2 : index * 2 + 2, index * 2 : index * 2 + 2]
                if block.shape == (2, 2):
                    ellipse_rows.append({"name": name, **error_ellipse(block)})
            if ellipse_rows:
                st.write("点位误差椭圆")
                st.dataframe(pd.DataFrame(ellipse_rows), use_container_width=True)

elif page == "平差与质量":
    st.subheader("线性最小二乘 / Huber 抗差 / 粗差筛查")
    st.caption("A：逗号分隔列、换行分隔行；L：每行一个值。")
    a_text = st.text_area("A", "1\n1\n1\n1")
    l_text = st.text_area("L", "10.01\n9.99\n10.00\n11.20")
    robust = st.checkbox("Huber 抗差", value=False)
    threshold = st.number_input("粗差筛查阈值", min_value=0.1, value=3.0)
    if st.button("计算平差"):
        matrix = np.array(
            [
                [float(value) for value in row.split(",")]
                for row in a_text.splitlines()
                if row.strip()
            ]
        )
        vector = np.array(
            [float(value.strip()) for value in l_text.splitlines() if value.strip()]
        )
        result = robust_least_squares(matrix, vector) if robust else least_squares(matrix, vector)
        standardized = standardized_residuals(result)
        outliers = detect_outliers(result, threshold=threshold)
        st.write("参数", result.parameters)
        st.write("残差", result.residuals)
        st.write("标准化残差", standardized)
        st.write("σ₀", result.sigma0)
        st.write("疑似粗差观测索引", outliers if outliers else "未发现")

        if result.covariance is not None and result.covariance.shape[0] >= 2:
            ellipse = error_ellipse(result.covariance[:2, :2])
            st.write("前两个参数的误差椭圆", ellipse)
            fig, ax = plt.subplots()
            patch = Ellipse(
                (0, 0),
                width=2 * ellipse["semi_major"],
                height=2 * ellipse["semi_minor"],
                angle=90 - ellipse["azimuth"],
                fill=False,
            )
            ax.add_patch(patch)
            ax.autoscale_view()
            ax.set_aspect("equal")
            st.pyplot(fig)

elif page == "坐标转换":
    st.subheader("CRS 坐标转换")
    x = st.number_input("X / 经度", value=118.7969, format="%.8f")
    y = st.number_input("Y / 纬度", value=32.0603, format="%.8f")
    source = st.text_input("源 CRS", "EPSG:4326")
    target = st.text_input("目标 CRS", "EPSG:3857")
    if st.button("转换"):
        xx, yy = transform_coordinates(x, y, source, target)
        st.success(f"X={xx:.4f}, Y={yy:.4f}")

elif page == "工程测量":
    tab1, tab2, tab3 = st.tabs(["极坐标放样", "坡度", "面积"])
    with tab1:
        sx = st.number_input("测站 X", value=1000.0, key="esx")
        sy = st.number_input("测站 Y", value=1000.0, key="esy")
        tx = st.number_input("目标 X", value=1100.0, key="etx")
        ty = st.number_input("目标 Y", value=1050.0, key="ety")
        st.write(polar_stakeout((sx, sy), (tx, ty)))
    with tab2:
        horizontal = st.number_input("水平距离", value=100.0)
        dh = st.number_input("高差", value=2.0)
        st.write(f"坡度：{slope(horizontal, dh):.4f}%")
    with tab3:
        st.caption("每行输入 X,Y")
        points = st.text_area("多边形点", "0,0\n10,0\n10,10\n0,10")
        if st.button("计算面积"):
            coordinates = [
                [float(value) for value in row.split(",")]
                for row in points.splitlines()
                if row.strip()
            ]
            st.success(f"面积：{polygon_area(coordinates):.4f}")

elif page == "数据格式":
    st.subheader("测量数据导入预览")
    uploaded = st.file_uploader("CSV / XLSX / LandXML / GSI", type=["csv", "xlsx", "xml", "gsi"])
    if uploaded is not None:
        suffix = Path(uploaded.name).suffix.lower()
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
            temp.write(uploaded.getvalue())
            temp_path = Path(temp.name)
        try:
            if suffix == ".csv":
                data = read_csv(temp_path)
            elif suffix == ".xlsx":
                data = read_excel(temp_path)
            elif suffix == ".xml":
                data = read_landxml_points(temp_path)
            else:
                data = read_gsi(temp_path)
            st.dataframe(data, use_container_width=True)
            st.caption(f"读取 {len(data)} 条记录")
        finally:
            temp_path.unlink(missing_ok=True)
