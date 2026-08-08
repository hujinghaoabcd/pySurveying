from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from matplotlib.patches import Ellipse

from pysurveying.adjustment import least_squares
from pysurveying.basic import (
    azimuth,
    distance,
    distance_intersection,
    forward_coordinate,
    forward_intersection,
    resection,
)
from pysurveying.engineering import polygon_area, polar_stakeout, slope
from pysurveying.leveling import leveling_route
from pysurveying.quality import error_ellipse, robust_least_squares
from pysurveying.transform import transform_coordinates
from pysurveying.traverse import closed_traverse, connected_traverse

st.set_page_config(page_title="pySurveying", page_icon="📐", layout="wide")
st.title("pySurveying")
st.caption("轻量级测量计算、测量平差与可视化工具包")

page = st.sidebar.radio(
    "功能",
    ["基础计算", "交会与后方交会", "导线", "水准", "平差与质量", "坐标转换", "工程测量"],
)

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
    a = st.number_input("方位角(°)", value=30.0)
    s = st.number_input("距离", value=100.0)
    if st.button("计算坐标"):
        x, y = forward_coordinate(x1, y1, a, s)
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
            rows = [[float(v) for v in row.split(",")] for row in text.splitlines() if row.strip()]
            station = resection([(r[0], r[1]) for r in rows], [r[2] for r in rows])
            st.success(f"X={station[0]:.4f}, Y={station[1]:.4f}, 定向={station[2]:.6f}°")

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
            pd.DataFrame({"point": range(len(result["heights"])), "height": result["heights"]}),
            use_container_width=True,
        )

elif page == "平差与质量":
    st.subheader("线性最小二乘 / Huber 抗差")
    st.caption("A：逗号分隔列、换行分隔行；L：每行一个值。")
    a_text = st.text_area("A", "1\n1\n1\n1")
    l_text = st.text_area("L", "10.01\n9.99\n10.00\n11.20")
    robust = st.checkbox("Huber 抗差", value=False)
    if st.button("计算平差"):
        A = np.array(
            [[float(value) for value in row.split(",")] for row in a_text.splitlines() if row.strip()]
        )
        L = np.array([float(value.strip()) for value in l_text.splitlines() if value.strip()])
        result = robust_least_squares(A, L) if robust else least_squares(A, L)
        st.write("参数", result.parameters)
        st.write("残差", result.residuals)
        st.write("σ₀", result.sigma0)
        if result.covariance is not None and result.covariance.shape[0] >= 2:
            ellipse = error_ellipse(result.covariance[:2, :2])
            st.write("误差椭圆", ellipse)
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
