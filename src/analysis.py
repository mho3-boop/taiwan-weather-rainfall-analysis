from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 120)

project_root = Path(__file__).resolve().parents[1]

processed_path = (
    project_root
    / "data"
    / "processed"
    / "taiwan_weather_daily_2020_2025.csv"
)

daily = pd.read_csv(processed_path)

print(daily.shape)
print(daily.head())

comparison = (
    daily.groupby("heavy_rain")[
        [
            "avg_temperature",
            "avg_humidity",
            "avg_pressure",
            "avg_wind_speed",
            "max_wind_speed",
            "total_rainfall",
        ]
    ]
    .mean()
)

print("\nAverage conditions by heavy-rain status:")
print(comparison)

summary = comparison[
    ["avg_humidity", "avg_pressure", "avg_wind_speed", "max_wind_speed"]
].T

summary.columns = ["Normal day", "Heavy-rain day"]

print("\nKey weather differences:")
print(summary)

percent_change = (
    (summary["Heavy-rain day"] - summary["Normal day"])
    / summary["Normal day"]
    * 100
)

print("\nPercent difference on heavy-rain days:")
print(percent_change.round(1))

percent_change.plot(kind="bar")

plt.title("Weather Differences on Heavy-Rain Days")
plt.xlabel("Weather Variable")
plt.ylabel("Percent Difference vs. Normal Days")
plt.axhline(0)
plt.tight_layout()

outputs_path = project_root / "outputs"
outputs_path.mkdir(parents=True, exist_ok=True)

chart_path = outputs_path / "heavy_rain_weather_differences.png"

plt.savefig(chart_path)
plt.close()

print(f"Saved chart to {chart_path}")