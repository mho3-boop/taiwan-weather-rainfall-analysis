"""
Data collection module for the Taiwan Weather & Rainfall Analysis project.

Fetches historical hourly weather data from the Open-Meteo Historical Weather API
(https://open-meteo.com/en/docs/historical-weather-api) for a list of Taiwanese
cities and returns it as a pandas DataFrame. No API key required.
"""

from pathlib import Path
import time
import requests
import pandas as pd

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

# Approximate city-center coordinates for the four cities we're studying.
CITIES = {
    "Taipei":    (25.033, 121.565),
    "Taichung":  (24.147, 120.674),
    "Tainan":    (22.999, 120.227),
    "Kaohsiung": (22.627, 120.301),
}

# The hourly variables we care about for this project.
# (Full list of valid names: https://open-meteo.com/en/docs/historical-weather-api)
HOURLY_VARS = [
    "temperature_2m",        # air temp, °C
    "relative_humidity_2m",  # %
    "precipitation",         # mm, sum of the preceding hour
    "surface_pressure",      # hPa
    "wind_speed_10m",        # km/h
    "weather_code",          # WMO code, e.g. 65 = heavy rain, 95 = thunderstorm
]


def fetch_city_hourly(city, lat, lon, start_date, end_date):
    """
    Fetch hourly historical weather data for ONE city from Open-Meteo.

    Parameters
    ----------
    city : str
        Name of the city (used only for labeling the output, not sent to the API)
    lat, lon : float
        Coordinates of the city
    start_date, end_date : str
        Dates in 'YYYY-MM-DD' format

    Returns
    -------
    pandas.DataFrame
        One row per hour, with a 'city' column added so that when we later
        combine all four cities into one big DataFrame, we can still tell
        rows apart.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ",".join(HOURLY_VARS),
        # Using Taiwan's local timezone means the API's day boundaries (used
        # later for daily aggregation) line up with an actual Taiwan calendar
        # day, not a UTC day.
        "timezone": "Asia/Taipei",
    }

    print(f"Requesting {city} ({start_date} to {end_date})...")
    response = requests.get(ARCHIVE_URL, params=params, timeout=30)
    response.raise_for_status()  # raises an exception if the HTTP status isn't 200
    payload = response.json()

    # payload["hourly"] looks like: {"time": [...], "temperature_2m": [...], ...}
    # pandas can turn that dict-of-lists directly into a DataFrame.
    df = pd.DataFrame(payload["hourly"])
    df["city"] = city
    return df


def fetch_all_cities(start_date, end_date, cities=CITIES, pause_seconds=1):
    """
    Loop over all cities, fetch each one, and stack them into a single
    DataFrame (long format: city is just another column, not separate files).
    """
    frames = []
    for city, (lat, lon) in cities.items():
        df = fetch_city_hourly(city, lat, lon, start_date, end_date)
        frames.append(df)
        time.sleep(pause_seconds)  # polite pause between requests
    return pd.concat(frames, ignore_index=True)

if __name__ == "__main__":
    # Fetch the full study period for all four cities.
    # Run this file directly to download the raw hourly dataset used in the analysis.
    data = fetch_all_cities("2020-01-01", "2025-12-31")
    print(data.shape)
    print(data.head())
    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "data" / "raw" / "taiwan_weather_2020_2025.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")
