import math

from pysurveying.basic import azimuth
from pysurveying.models import Observation, Point
from pysurveying.quality import control_network_data_snooping


def test_control_network_data_snooping_locates_gross_azimuth():
    true_x, true_y = 40.0, 30.0
    points = [Point("P", 39.0, 31.0)]
    observations = []
    noise_deg = [0.002, -0.001, 0.001, -0.002, 0.0015, -0.0015, 0.0, 0.001, -0.001, 5.0]

    for index in range(10):
        angle = 2.0 * math.pi * index / 10.0
        x = 50.0 + 100.0 * math.cos(angle)
        y = 50.0 + 100.0 * math.sin(angle)
        name = f"C{index}"
        points.append(Point(name, x, y, fixed=True))
        observed = azimuth((x, y), (true_x, true_y)) + noise_deg[index]
        observations.append(Observation("azimuth", name, "P", observed, sigma=0.1))

    report = control_network_data_snooping(
        points,
        observations,
        threshold=2.5,
        max_removals=2,
    )
    result = report["result"]

    assert result is not None
    assert report["removed_indices"] == [9]
    assert report["converged"]
    assert report["history"][0]["kind"] == "azimuth"
    x, y = result.metadata["adjusted_points"]["P"]
    assert math.isclose(x, true_x, abs_tol=0.02)
    assert math.isclose(y, true_y, abs_tol=0.02)
