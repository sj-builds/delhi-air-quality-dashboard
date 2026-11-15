
import pandas as pd
import numpy as np

# Load cleaned dataset
df = pd.read_csv("data/processed/delhi_air_quality_clean.csv")

# Convert date column
df["period_start"] = pd.to_datetime(df["period_start"])

print("=" * 60)
print("DELHI AIR POLLUTION - EXPLORATORY DATA ANALYSIS")
print("=" * 60)

# 1. Dataset overview
print("\n1. DATASET OVERVIEW")
print("-" * 40)

print("Dataset Shape:", df.shape)
print("Unique Stations:", df["station_id"].nunique())
print("Date Range:", df["period_start"].min(), "to", df["period_start"].max())

# 2. Missing values
print("\n2. MISSING VALUES")
print("-" * 40)

print(df.isnull().sum())

# 3. Descriptive statistics
print("\n3. DESCRIPTIVE STATISTICS")
print("-" * 40)

pollutants = ["PM2.5_mean", "PM10_mean"]

for pollutant in pollutants:
    if pollutant in df.columns:
        print(f"\n{pollutant}")
        print(df[pollutant].describe())

# 4. Monthly pollution averages
print("\n4. MONTHLY POLLUTION AVERAGES")
print("-" * 40)

df["year_month"] = df["period_start"].dt.to_period("M").astype(str)

monthly = df.groupby("year_month")[pollutants].mean()

print(monthly.tail(12))

# 5. Seasonal pollution averages
print("\n5. SEASONAL POLLUTION AVERAGES")
print("-" * 40)

seasonal = df.groupby("season")[pollutants].mean()

print(seasonal)

# 6. Day-wise pollution averages
print("\n6. DAY-WISE POLLUTION AVERAGES")
print("-" * 40)

weekday = df.groupby("day_of_week")[pollutants].mean()

print(weekday)

# 7. Station-wise pollution averages
print("\n7. STATION-WISE POLLUTION AVERAGES")
print("-" * 40)

station = df.groupby("station_name")[pollutants].mean()

print(station.sort_values("PM2.5_mean", ascending=False).head(10))

# 8. Correlation
print("\n8. POLLUTANT CORRELATION")
print("-" * 40)

print(df[pollutants].corr())

# 9. Save analysis results
monthly.to_csv("reports/monthly_pollution_summary.csv")
seasonal.to_csv("reports/seasonal_pollution_summary.csv")
weekday.to_csv("reports/weekday_pollution_summary.csv")
station.to_csv("reports/station_pollution_summary.csv")

print("\nEDA RESULTS SAVED SUCCESSFULLY!")
