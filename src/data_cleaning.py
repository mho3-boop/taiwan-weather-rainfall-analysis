from pathlib import Path
import pandas as pd

import matplotlib.pyplot as plt

project_root = Path(__file__).resolve().parents[1]
raw_path = project_root / "data" / "raw" / "taiwan_weather_2020_2025.csv"

df = pd.read_csv(raw_path)

df["time"] = pd.to_datetime(df["time"])

print(df.shape)
print(df.head())
print(df.dtypes)
print(df.isna().sum())
print("Duplicate rows:", df.duplicated().sum())

print(df.describe())
df["date"] = df["time"].dt.date

daily = (
    df.groupby(["city", "date"])
    .agg(
        total_rainfall=("precipitation", "sum"),
        avg_temperature=("temperature_2m", "mean"),
        min_temperature=("temperature_2m", "min"),
        max_temperature=("temperature_2m", "max"),
        avg_humidity=("relative_humidity_2m", "mean"),
        avg_pressure=("surface_pressure", "mean"),
        avg_wind_speed=("wind_speed_10m", "mean"),
        max_wind_speed=("wind_speed_10m", "max"),
        max_weather_code=("weather_code", "max"),
    )
    .reset_index()
)

print(daily.shape)
print(daily.head())

daily["heavy_rain"] = (daily["total_rainfall"] >= 50).astype(int)

print(daily["heavy_rain"].value_counts())

processed_path = (
    project_root
    / "data"
    / "processed"
    / "taiwan_weather_daily_2020_2025.csv"
)

processed_path.parent.mkdir(parents=True, exist_ok=True)
daily.to_csv(processed_path, index=False)

print(f"Saved processed daily data to {processed_path}")

heavy_rain_by_city = (
    daily.groupby("city")["heavy_rain"]
    .sum()
    .sort_values(ascending=False)
)

print("\nHeavy-rain days by city:")
print(heavy_rain_by_city)

outputs_path = project_root / "outputs"
outputs_path.mkdir(exist_ok=True)

chart_path = outputs_path / "heavy_rain_by_city.png"

heavy_rain_by_city.plot(kind="bar")

plt.title("Heavy-Rain Days by City, 2020–2025")
plt.xlabel("City")
plt.ylabel("Number of Days with ≥50 mm Rainfall")
plt.tight_layout()

chart_path = outputs_path / "heavy_rain_by_city.png"
plt.savefig(chart_path)
plt.close()

print(f"Saved chart to {chart_path}")

daily["month"] = pd.to_datetime(daily["date"]).dt.month

heavy_rain_by_month = (
    daily.groupby("month")["heavy_rain"]
    .sum()
)

print("\nHeavy-rain days by month:")
print(heavy_rain_by_month)

heavy_rain_by_month.plot(kind="bar")

plt.title("Heavy-Rain Days by Month, 2020–2025")
plt.xlabel("Month")
plt.ylabel("Number of Heavy-Rain Days")
plt.tight_layout()

month_chart_path = outputs_path / "heavy_rain_by_month.png"
plt.savefig(month_chart_path)
plt.close()

print(f"Saved chart to {month_chart_path}")