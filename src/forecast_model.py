from pathlib import Path
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

import matplotlib.pyplot as plt

project_root = Path(__file__).resolve().parents[1]

processed_path = (
    project_root
    / "data"
    / "processed"
    / "taiwan_weather_daily_2020_2025.csv"
)

df = pd.read_csv(processed_path)

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["city", "date"])

feature_columns = [
    "avg_temperature",
    "avg_humidity",
    "avg_pressure",
    "avg_wind_speed",
    "max_wind_speed",
    "total_rainfall",
]

for column in feature_columns:
    df[f"prev_{column}"] = df.groupby("city")[column].shift(1)

model_data = df.dropna(
    subset=[f"prev_{column}" for column in feature_columns]
).copy()

print(model_data.shape)
print(model_data[
    [
        "city",
        "date",
        "prev_avg_humidity",
        "prev_avg_pressure",
        "prev_avg_wind_speed",
        "prev_total_rainfall",
        "heavy_rain",
    ]
].head())

features = [
    "prev_avg_temperature",
    "prev_avg_humidity",
    "prev_avg_pressure",
    "prev_avg_wind_speed",
    "prev_max_wind_speed",
    "prev_total_rainfall",
]

X = model_data[features]
y = model_data["heavy_rain"].astype(int)

model_data["year"] = model_data["date"].dt.year

train_mask = model_data["year"] <= 2024
test_mask = model_data["year"] == 2025

X_train = X.loc[train_mask]
X_test = X.loc[test_mask]

y_train = y.loc[train_mask]
y_test = y.loc[test_mask]

model = make_pipeline(
    StandardScaler(),
    LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
    )
)

model.fit(X_train, y_train)

logistic_model = model.named_steps["logisticregression"]

coefficients = pd.Series(
    logistic_model.coef_[0],
    index=features
).sort_values()

print("\nStandardized model coefficients:")
print(coefficients)

predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)[:, 1]

print("\nConfusion matrix:")
print(confusion_matrix(y_test, predictions))

print("\nClassification report:")
print(classification_report(y_test, predictions, digits=3))

print("ROC-AUC:", round(roc_auc_score(y_test, probabilities), 3))

pretty_labels = {
    "prev_avg_pressure": "Previous-day average pressure",
    "prev_avg_wind_speed": "Previous-day average wind speed",
    "prev_total_rainfall": "Previous-day rainfall",
    "prev_avg_humidity": "Previous-day average humidity",
    "prev_avg_temperature": "Previous-day average temperature",
    "prev_max_wind_speed": "Previous-day max wind speed",
}

coefficients_pretty = coefficients.rename(index=pretty_labels)

coefficients_sorted = coefficients_pretty.sort_values()

plt.figure(figsize=(8, 5))

coefficients_sorted.plot(kind="barh")

plt.title("Previous-Day Weather Signals for Next-Day Heavy Rain")
plt.xlabel("Coefficient")
plt.ylabel("Previous-Day Weather Feature")
plt.tight_layout()

outputs_path = project_root / "outputs"
outputs_path.mkdir(exist_ok=True)

coefficient_chart_path = outputs_path / "forecast_model_coefficients.png"

plt.savefig(coefficient_chart_path)
plt.close()

print(f"Saved coefficient chart to {coefficient_chart_path}")
