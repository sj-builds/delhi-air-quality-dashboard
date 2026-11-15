
import pandas as pd

df = pd.read_csv(
    "data/processed/delhi_air_quality_clean.csv"
)

print("\nTOP 10 STATIONS - PM2.5")

pm25 = (
    df.groupby("station_name")["PM2.5_mean"]
    .agg(["mean", "count"])
    .sort_values("mean", ascending=False)
    .head(10)
)

print(pm25.to_string())

print("\nTOP 10 STATIONS - PM10")

pm10 = (
    df.groupby("station_name")["PM10_mean"]
    .agg(["mean", "count"])
    .sort_values("mean", ascending=False)
    .head(10)
)

print(pm10.to_string())
