from pysurveying import Point, azimuth, distance
from pysurveying.traverse import closed_traverse


a = Point("A", 0.0, 0.0)
b = Point("B", 100.0, 100.0)
print("distance:", distance(a, b))
print("azimuth:", azimuth(a, b))

result = closed_traverse(
    (0.0, 0.0),
    [90.0, 0.0, 270.0, 180.0],
    [100.0, 100.0, 100.0, 100.0],
)
print("traverse:", result["coordinates"])
