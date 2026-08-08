"""Small leveling-network adjustment example."""

from pysurveying import LevelObservation, leveling_network

observations = [
    LevelObservation("BM", "A", 1.000, sigma=0.001),
    LevelObservation("A", "B", 2.000, sigma=0.001),
    LevelObservation("BM", "B", 3.001, sigma=0.001),
]

result = leveling_network(observations, {"BM": 100.0})
print("adjusted heights:", result.metadata["adjusted_heights"])
print("residuals:", result.residuals)
print("sigma0:", result.sigma0)
