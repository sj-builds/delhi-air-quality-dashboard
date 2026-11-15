
import os
import pandas as pd
import matplotlib.pyplot as plt

# Create charts directory if it does not exist
os.makedirs("charts", exist_ok=True)

# Load cleaned dataset
df = pd.read_csv("data/processed/delhi_air_quality_clean.csv")

df["period_start"] = pd.to_datetime(df["period_start"])

# Columns to analyze
pm25 = "PM2.5_mean"
pm10 = "PM10_mean"

# Use only available pollutant measurements
print("Generating Delhi Air Pollution Charts...")

# --------------------------------------------------
# 1. MONTHLY POLLUTION TREND
# --------------------------------------------------

df["year_month"] = df["period_start"].dt.to_period("M")

monthly = df.groupby("year_month")[[pm25, pm10]].mean()
monthly.index = monthly.index.astype(str)

plt.figure(figsize=(14, 6))
plt.plot(monthly.index, monthly[pm25], label="PM2.5")
plt.plot(monthly.index, monthly[pm10], label="PM10")

plt.title("Monthly PM2.5 and PM10 Pollution Trends in Delhi")
plt.xlabel("Month")
plt.ylabel("Average Concentration (dataset units)")
plt.xticks(rotation=90)
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("charts/monthly_pollution_trend.png", dpi=300)
plt.close()

# --------------------------------------------------
# 2. SEASONAL POLLUTION COMPARISON
# --------------------------------------------------

season_order = ["Winter", "Summer", "Monsoon", "Post-Monsoon"]

seasonal = (
    df.groupby("season")[[pm25, pm10]]
    .mean()
    .reindex(season_order)
)

seasonal.plot(kind="bar", figsize=(10, 6))

plt.title("Seasonal Comparison of PM2.5 and PM10 in Delhi")
plt.xlabel("Season")
plt.ylabel("Average Concentration (dataset units)")
plt.xticks(rotation=0)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("charts/seasonal_pollution.png", dpi=300)
plt.close()

# --------------------------------------------------
# 3. WEEKDAY POLLUTION COMPARISON
# --------------------------------------------------

weekday_order = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"
]

weekday = (
    df.groupby("day_of_week")[[pm25, pm10]]
    .mean()
    .reindex(weekday_order)
)

weekday.plot(kind="bar", figsize=(11, 6))

plt.title("Day-wise Average PM2.5 and PM10 Levels")
plt.xlabel("Day of Week")
plt.ylabel("Average Concentration (dataset units)")
plt.xticks(rotation=30)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("charts/weekday_pollution.png", dpi=300)
plt.close()

# --------------------------------------------------
# 4. TOP 10 STATIONS BY PM2.5
# --------------------------------------------------

station_pm25 = (
    df.groupby("station_name")[pm25]
    .mean()
    .dropna()
    .sort_values(ascending=False)
    .head(10)
    .sort_values()
)

plt.figure(figsize=(11, 7))
station_pm25.plot(kind="barh")

plt.title("Top 10 Delhi Stations by Average PM2.5")
plt.xlabel("Average PM2.5 Concentration (dataset units)")
plt.ylabel("Monitoring Station")
plt.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig("charts/top_10_pm25_stations.png", dpi=300)
plt.close()

# --------------------------------------------------
# 5. TOP 10 STATIONS BY PM10
# --------------------------------------------------

station_pm10 = (
    df.groupby("station_name")[pm10]
    .mean()
    .dropna()
    .sort_values(ascending=False)
    .head(10)
    .sort_values()
)

plt.figure(figsize=(11, 7))
station_pm10.plot(kind="barh")

plt.title("Top 10 Delhi Stations by Average PM10")
plt.xlabel("Average PM10 Concentration (dataset units)")
plt.ylabel("Monitoring Station")
plt.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig("charts/top_10_pm10_stations.png", dpi=300)
plt.close()

# --------------------------------------------------
# 6. PM2.5 AND PM10 CORRELATION
# --------------------------------------------------

paired = df[[pm25, pm10]].dropna()

# Limit plotted points for readability
plot_data = paired.sample(
    n=min(10000, len(paired)),
    random_state=42
)

plt.figure(figsize=(9, 6))
plt.scatter(
    plot_data[pm25],
    plot_data[pm10],
    alpha=0.25
)

plt.title("Relationship Between PM2.5 and PM10")
plt.xlabel("PM2.5 Concentration (dataset units)")
plt.ylabel("PM10 Concentration (dataset units)")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("charts/pollutant_correlation.png", dpi=300)
plt.close()

# --------------------------------------------------
# 7. MONTHLY DATA COVERAGE
# --------------------------------------------------

coverage = df.groupby("year_month").size()
coverage.index = coverage.index.astype(str)

plt.figure(figsize=(14, 5))
coverage.plot(kind="bar")

plt.title("Monthly Data Coverage in Delhi")
plt.xlabel("Month")
plt.ylabel("Number of Station-Date Records")
plt.xticks(rotation=90)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("charts/monthly_data_coverage.png", dpi=300)
plt.close()

# --------------------------------------------------
# COMPLETION
# --------------------------------------------------

print("\nCHART GENERATION COMPLETED!")
print("\nGenerated charts:")

for file in sorted(os.listdir("charts")):
    if file.endswith(".png"):
        print("-", file)
