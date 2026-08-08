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
    adjust_control_network_robust,
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
from pysurveying.engineering import (
    chainage_offset,
    grade_elevation,
    polar_stakeout,
    polygon_area,
    slope,
)
from pysurveying.io import read_points
from pysurveying.leveling import leveling_network, leveling_route
from pysurveying.models import LevelObservation, Observation, Point
from pysurveying.quality import data_snooping, error_ellipse, robust_least_squares
from pysurveying.transform import (
    fit_affine_2d,
    fit_similarity_2d,
    geodetic_to_enu,
    transform_coordinates,
)
from pysurveying.traverse import closed_traverse, closed_traverse_from_angles, connected_traverse

st.set_page_config(page_title="pySurveying", page_icon="📐", layout="wide")
st.title("pySurveying 0.2")
st.caption("轻量级测量计算、测量平差与可视化工具包")
st.sidebar.caption("平面计算约定：+Y 为北、+X 为东，方位角从北顺时针。")

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


def _traverse_plot(coordinates):
    table = pd.DataFrame(coordinates, columns=["X", "Y"])
    fig, ax = plt.subplots()
    ax.plot(table["X"], table["Y"], marker="o")
    for index, row in table.iterrows():
        ax.annotate(str(index), (row["X"], row["Y"]))
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    return table, fig


def _parse_xy_text(text: str) -> list[list[float]]:
    return [
        [float(value.strip()) for value in row.split(",")]
        for row in text.splitlines()
        if row.strip()
    ]


if page == "基础计算":
    st.subheader("坐标正反算")
    col1, col2 = st.columns(2)
    with col1:
        x1 = st.number_input("X1", value=1000.0)
        y1 = st.number_input("Y1", value=1000.0)
    with col2:
        x2 = st.number_input("X2", value=1100.0)
        y2 = st.number_input("Y2", value=1050.0)

    m1, m2 = st.columns(2)
    m1.metric("两点距离", f"{distance((x1, y1), (x2, y2)):.4f}")
    m2.metric("坐标方位角", f"{azimuth((x1, y1), (x2, y2)):.6f}°")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        forward_azimuth = st.number_input("正算方位角(°)", value=30.0)
    with col2:
        forward_distance = st.number_input("正算距离", value=100.0)
    if st.button("坐标正算"):
        x, y = forward_coordinate(x1, y1, forward_azimuth, forward_distance)
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
        if st.button("计算前方交会"):
            x, y = forward_intersection((p1x, p1y), a1, (p2x, p2y), a2)
            st.success(f"P=({x:.4f}, {y:.4f})")

    with tab2:
        p1x = st.number_input("P1 X", value=0.0, key="d1x")
        p1y = st.number_input("P1 Y", value=0.0, key="d1y")
        r1 = st.number_input("P1 距离", value=70.710678)
        p2x = st.number_input("P2 X", value=100.0, key="d2x")
        p2y = st.number_input("P2 Y", value=0.0, key="d2y")
        r2 = st.number_input("P2 距离", value=70.710678, key="r2")
        if st.button("计算距离交会"):
            q1, q2 = distance_intersection((p1x, p1y), r1, (p2x, p2y), r2)
            st.write("解 1", q1)
            st.write("解 2", q2)

    with tab3:
        st.caption("每行：X,Y,观测方向(°)，至少 3 个已知点。")
        text = st.text_area(
            "已知点与方向",
            "0,0,225\n100,0,135\n100,100,45\n0,100,315",
        )
        if st.button("计算后方交会"):
            rows = _parse_xy_text(text)
            station = resection([(row[0], row[1]) for row in rows], [row[2] for row in rows])
            st.success(
                f"X={station[0]:.4f}, Y={station[1]:.4f}, 定向={station[2]:.6f}°"
            )

elif page == "导线":
    st.subheader("导线计算")
    tab1, tab2 = st.tabs(["已知方位角", "内角闭合导线"])

    with tab1:
        mode = st.radio("导线类型", ["闭合导线", "附合导线"], horizontal=True)
        sx = st.number_input("起点 X", value=1000.0, key="t1sx")
        sy = st.number_input("起点 Y", value=1000.0, key="t1sy")
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
            key="traverse_azimuths",
        )
        if st.button("平差导线", key="traverse_by_azimuth"):
            if mode == "闭合导线":
                result = closed_traverse((sx, sy), table.azimuth_deg, table.distance)
            else:
                result = connected_traverse((sx, sy), end, table.azimuth_deg, table.distance)
            c1, c2, c3 = st.columns(3)
            c1.metric("fx", f"{result['misclosure_x']:.6f}")
            c2.metric("fy", f"{result['misclosure_y']:.6f}")
            ratio = result["relative_precision"]
            c3.metric("相对精度", "∞" if math.isinf(ratio) else f"1:{ratio:.0f}")
            coordinates, fig = _traverse_plot(result["coordinates"])
            st.dataframe(coordinates, use_container_width=True)
            st.pyplot(fig)

    with tab2:
        st.caption("先平差内角闭合差，再推算方位角，最后用 Bowditch 分配坐标闭合差。")
        sx = st.number_input("起点 X", value=0.0, key="t2sx")
        sy = st.number_input("起点 Y", value=0.0, key="t2sy")
        start_azimuth = st.number_input("第一边方位角(°)", value=90.0)
        turn = st.radio("转角方向", ["right", "left"], horizontal=True)
        table = st.data_editor(
            pd.DataFrame(
                {
                    "angle_deg": [90.01, 89.99, 90.02, 89.98],
                    "distance": [100.0, 100.0, 100.0, 100.0],
                }
            ),
            num_rows="dynamic",
            use_container_width=True,
            key="traverse_angles",
        )
        if st.button("角度与坐标联合计算"):
            result = closed_traverse_from_angles(
                (sx, sy),
                start_azimuth,
                table.angle_deg,
                table.distance,
                turn=turn,
            )
            angle_result = result["angle_adjustment"]
            c1, c2, c3 = st.columns(3)
            c1.metric("角度闭合差", f"{angle_result['misclosure']:.6f}°")
            c2.metric("坐标闭合差", f"{result['linear_misclosure']:.6f}")
            ratio = result["relative_precision"]
            c3.metric("相对精度", "∞" if math.isinf(ratio) else f"1:{ratio:.0f}")
            angle_table = pd.DataFrame(
                {
                    "观测角": table.angle_deg,
                    "改正数": angle_result["corrections"],
                    "平差角": angle_result["adjusted_angles"],
                    "边方位角": result["azimuths"],
                }
            )
            st.dataframe(angle_table, use_container_width=True)
            coordinates, fig = _traverse_plot(result["coordinates"])
            st.dataframe(coordinates, use_container_width=True)
            st.pyplot(fig)

elif page == "水准":
    st.subheader("水准测量")
    tab1, tab2 = st.tabs(["水准路线", "水准网"])

    with tab1:
        h0 = st.number_input("起点高程", value=10.0)
        has_end = st.checkbox("已知终点高程", value=True)
        hend = st.number_input("终点高程", value=10.0) if has_end else None
        table = st.data_editor(
            pd.DataFrame({"dh": [1.002, -0.501, -0.503], "length": [1.0, 1.0, 1.0]}),
            num_rows="dynamic",
            use_container_width=True,
            key="level_route",
        )
        if st.button("平差水准路线"):
            result = leveling_route(h0, table.dh, end_height=hend, lengths=table.length)
            st.metric("闭合差", f"{result['misclosure']:.6f}")
            output = pd.DataFrame(
                {
                    "point": range(len(result["heights"])),
                    "height": result["heights"],
                }
            )
            st.dataframe(output, use_container_width=True)

    with tab2:
        st.caption("高差定义为 H_to - H_from；sigma 为高差标准差。")
        fixed = st.data_editor(
            pd.DataFrame({"name": ["BM"], "height": [100.0]}),
            num_rows="dynamic",
            use_container_width=True,
            key="level_fixed",
        )
        observations = st.data_editor(
            pd.DataFrame(
                {
                    "from_point": ["BM", "A", "BM"],
                    "to_point": ["A", "B", "B"],
                    "dh": [1.000, 2.000, 3.001],
                    "sigma": [0.001, 0.001, 0.001],
                }
            ),
            num_rows="dynamic",
            use_container_width=True,
            key="level_network",
        )
        if st.button("平差水准网"):
            fixed_heights = {
                str(row["name"]): float(row["height"]) for _, row in fixed.iterrows()
            }
            level_observations = [
                LevelObservation(
                    str(row["from_point"]),
                    str(row["to_point"]),
                    float(row["dh"]),
                    float(row["sigma"]),
                )
                for _, row in observations.iterrows()
            ]
            result = leveling_network(level_observations, fixed_heights)
            st.metric("σ₀", "—" if result.sigma0 is None else f"{result.sigma0:.6f}")
            heights = pd.DataFrame(
                [
                    {"name": name, "height": height}
                    for name, height in result.metadata["adjusted_heights"].items()
                ]
            )
            st.dataframe(heights, use_container_width=True)
            st.write("残差", result.residuals)

elif page == "控制网":
    st.subheader("二维控制网平差")
    st.caption(
        "支持 distance、azimuth、direction、angle。direction 自动估计测站定向未知数；"
        "azimuth 表示绝对方位角。"
    )
    free_network = st.checkbox("自由网（最小范数）", value=False)
    robust_network = st.checkbox("Huber 抗差", value=False, disabled=free_network)
    huber_k = st.number_input("Huber k", min_value=0.1, value=1.5, disabled=not robust_network)

    point_table = st.data_editor(
        pd.DataFrame(
            {
                "name": ["A", "B", "C", "P"],
                "x": [0.0, 100.0, 0.0, 39.0],
                "y": [0.0, 0.0, 100.0, 31.0],
                "fixed": [True, True, True, False],
            }
        ),
        num_rows="dynamic",
        use_container_width=True,
        key="network_points",
    )
    observation_table = st.data_editor(
        pd.DataFrame(
            {
                "kind": ["distance", "distance", "distance"],
                "from_point": ["A", "B", "C"],
                "to_point": ["P", "P", "P"],
                "target2": ["", "", ""],
                "value": [50.0, 67.082039325, 80.622577483],
                "sigma": [0.01, 0.01, 0.01],
            }
        ),
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

        if free_network:
            result = adjust_free_network(points, observations)
        elif robust_network:
            result = adjust_control_network_robust(points, observations, huber_k=huber_k)
        else:
            result = adjust_control_network(points, observations)

        adjusted = result.metadata["adjusted_points"]
        output = pd.DataFrame(
            [{"name": name, "x": xy[0], "y": xy[1]} for name, xy in adjusted.items()]
        )
        c1, c2, c3 = st.columns(3)
        c1.metric("收敛", "是" if result.converged else "否")
        c2.metric("迭代次数", result.iterations)
        c3.metric("σ₀", "—" if result.sigma0 is None else f"{result.sigma0:.6f}")
        st.dataframe(output, use_container_width=True)
        st.write("归一化观测残差", result.residuals)
        if result.metadata.get("orientations"):
            st.write("测站定向参数", result.metadata["orientations"])
        if robust_network:
            st.write("Huber 权", result.metadata["robust_weights"])
        st.pyplot(_network_plot(point_table, observation_table, adjusted))

        if result.covariance is not None:
            ellipse_rows = []
            for index, name in enumerate(result.metadata["point_order"]):
                block = result.covariance[
                    index * 2 : index * 2 + 2,
                    index * 2 : index * 2 + 2,
                ]
                if block.shape == (2, 2):
                    ellipse_rows.append({"name": name, **error_ellipse(block)})
            if ellipse_rows:
                st.write("95% 点位误差椭圆")
                st.dataframe(pd.DataFrame(ellipse_rows), use_container_width=True)

elif page == "平差与质量":
    st.subheader("线性最小二乘 / 抗差 / 粗差筛查")
    st.caption("A：逗号分隔列、换行分隔行；L：每行一个值。")
    a_text = st.text_area("A", "1\n1\n1\n1\n1")
    l_text = st.text_area("L", "10.00\n10.00\n10.00\n10.00\n20.00")
    robust = st.checkbox("Huber 抗差线性平差", value=False)
    threshold = st.number_input("标准化残差阈值", min_value=0.1, value=3.0)
    if st.button("计算平差"):
        matrix = np.array(_parse_xy_text(a_text), dtype=float)
        vector = np.array(
            [float(value.strip()) for value in l_text.splitlines() if value.strip()],
            dtype=float,
        )
        result = robust_least_squares(matrix, vector) if robust else least_squares(matrix, vector)
        st.write("参数", result.parameters)
        st.write("残差", result.residuals)
        st.write("σ₀", result.sigma0)
        if not robust:
            screening = pd.DataFrame(data_snooping(result, threshold=threshold))
            st.write("粗差筛查")
            st.dataframe(screening, use_container_width=True)

        if result.covariance is not None and result.covariance.shape[0] >= 2:
            ellipse = error_ellipse(result.covariance[:2, :2])
            st.write("前两个参数的 95% 误差椭圆", ellipse)
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
    st.subheader("坐标转换")
    tab1, tab2, tab3 = st.tabs(["CRS", "四/六参数", "本地 ENU"])

    with tab1:
        x = st.number_input("X / 经度", value=118.7969, format="%.8f")
        y = st.number_input("Y / 纬度", value=32.0603, format="%.8f")
        source = st.text_input("源 CRS", "EPSG:4326")
        target = st.text_input("目标 CRS", "EPSG:3857")
        if st.button("执行 CRS 转换"):
            xx, yy = transform_coordinates(x, y, source, target)
            st.success(f"X={xx:.4f}, Y={yy:.4f}")

    with tab2:
        st.caption("输入同名点：x,y 为源坐标；X,Y 为目标坐标。")
        common = st.data_editor(
            pd.DataFrame(
                {
                    "x": [0.0, 100.0, 0.0, 100.0],
                    "y": [0.0, 0.0, 100.0, 100.0],
                    "X": [1000.0, 1100.0, 1000.0, 1100.0],
                    "Y": [2000.0, 2000.0, 2100.0, 2100.0],
                }
            ),
            num_rows="dynamic",
            use_container_width=True,
            key="common_points",
        )
        model = st.radio("模型", ["四参数相似变换", "六参数仿射变换"], horizontal=True)
        if st.button("拟合转换参数"):
            source_points = common[["x", "y"]].to_numpy(float)
            target_points = common[["X", "Y"]].to_numpy(float)
            result = (
                fit_similarity_2d(source_points, target_points)
                if model == "四参数相似变换"
                else fit_affine_2d(source_points, target_points)
            )
            st.write("参数", result["parameters"])
            st.metric("同名点 RMSE", f"{result['rmse']:.6f}")
            if model == "四参数相似变换":
                st.write(
                    {
                        "平移 X": result["tx"],
                        "平移 Y": result["ty"],
                        "比例尺": result["scale"],
                        "旋转角(°)": result["rotation_deg"],
                    }
                )
            st.dataframe(
                pd.DataFrame(result["residuals"], columns=["vX", "vY"]),
                use_container_width=True,
            )

    with tab3:
        st.caption("WGS84 经纬度/椭球高 → 以指定原点建立的 East-North-Up。")
        lon = st.number_input("目标经度", value=118.7970, format="%.8f")
        lat = st.number_input("目标纬度", value=32.0604, format="%.8f")
        height = st.number_input("目标椭球高", value=30.0)
        lon0 = st.number_input("原点经度", value=118.7969, format="%.8f")
        lat0 = st.number_input("原点纬度", value=32.0603, format="%.8f")
        height0 = st.number_input("原点椭球高", value=25.0)
        if st.button("计算 ENU"):
            east, north, up = geodetic_to_enu(lon, lat, height, lon0, lat0, height0)
            st.success(f"E={east:.4f} m, N={north:.4f} m, U={up:.4f} m")

elif page == "工程测量":
    st.subheader("工程测量常用计算")
    tab1, tab2, tab3, tab4 = st.tabs(["极坐标放样", "里程偏距", "坡度高程", "面积"])

    with tab1:
        sx = st.number_input("测站 X", value=1000.0, key="esx")
        sy = st.number_input("测站 Y", value=1000.0, key="esy")
        tx = st.number_input("目标 X", value=1100.0, key="etx")
        ty = st.number_input("目标 Y", value=1050.0, key="ety")
        result = polar_stakeout((sx, sy), (tx, ty))
        st.write(result)

    with tab2:
        start_x = st.number_input("基线起点 X", value=0.0)
        start_y = st.number_input("基线起点 Y", value=0.0)
        end_x = st.number_input("基线终点 X", value=0.0)
        end_y = st.number_input("基线终点 Y", value=100.0)
        px = st.number_input("待求点 X", value=3.0)
        py = st.number_input("待求点 Y", value=50.0)
        st.write(chainage_offset((px, py), (start_x, start_y), (end_x, end_y)))

    with tab3:
        horizontal = st.number_input("水平距离", value=100.0)
        dh = st.number_input("高差", value=2.0)
        st.write(f"坡度：{slope(horizontal, dh):.4f}%")
        start_height = st.number_input("设计起点高程", value=100.0)
        grade = st.number_input("设计坡度(%)", value=2.0)
        chainage = st.number_input("设计距离", value=50.0)
        st.write(f"设计高程：{grade_elevation(start_height, chainage, grade):.4f}")

    with tab4:
        points_text = st.text_area("多边形点，每行 X,Y", "0,0\n10,0\n10,10\n0,10")
        if st.button("计算面积"):
            coordinates = _parse_xy_text(points_text)
            st.success(f"面积：{polygon_area(coordinates):.4f}")

elif page == "数据格式":
    st.subheader("测量数据导入")
    st.caption("支持 CSV、XLSX、LandXML/XML、Leica GSI；CSV/XLSX 会尝试统一常见点号与坐标列名。")
    uploaded = st.file_uploader(
        "选择文件",
        type=["csv", "xlsx", "xlsm", "xml", "landxml", "gsi", "gsi8", "gsi16"],
    )
    if uploaded is not None:
        suffix = Path(uploaded.name).suffix.lower()
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
            temp.write(uploaded.getvalue())
            temp_path = Path(temp.name)
        try:
            data = read_points(temp_path)
            st.dataframe(data, use_container_width=True)
            st.caption(f"读取 {len(data)} 条记录")
            st.download_button(
                "导出为 CSV",
                data.to_csv(index=False).encode("utf-8-sig"),
                file_name=f"{Path(uploaded.name).stem}_normalized.csv",
                mime="text/csv",
            )
        finally:
            temp_path.unlink(missing_ok=True)
