
import pandas as pd
import numpy as np
from pathlib import Path

# ==========================================
# 1. PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

RAW_FILE = (
    BASE_DIR / "data" / "raw" /
    "delhi_air_quality_daily_raw.csv"
)

PROCESSED_DIR = BASE_DIR / "data" / "processed"
REPORT_DIR = BASE_DIR / "reports"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. LOAD DATA
# ==========================================

print("=" * 60)
print("DELHI AIR QUALITY DATA CLEANING")
print("=" * 60)

df = pd.read_csv(RAW_FILE)

print("\nOriginal Dataset Shape:", df.shape)

# ==========================================
# 3. VALIDATE REQUIRED COLUMNS
# ==========================================

required_columns = [
    "station_id",
    "parameter_name",
    "period_start",
    "mean",
    "min",
    "max",
    "n"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Required columns missing: {missing_columns}"
    )

# ==========================================
# 4. CONVERT DATA TYPES
# ==========================================

df["period_start"] = pd.to_datetime(
    df["period_start"],
    errors="coerce"
)

numeric_columns = ["mean", "min", "max", "n"]

for col in numeric_columns:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# ==========================================
# 5. REMOVE INVALID DATES
# ==========================================

invalid_dates = df[df["period_start"].isna()].copy()

invalid_dates.to_csv(
    REPORT_DIR / "invalid_dates.csv",
    index=False
)

df = df[df["period_start"].notna()].copy()

# ==========================================
# 6. STANDARDIZE POLLUTANT NAMES
# ==========================================

df["parameter_name"] = (
    df["parameter_name"]
    .astype(str)
    .str.strip()
    .str.upper()
)

df["parameter_name"] = (
    df["parameter_name"]
    .replace({"PM2.5": "PM2.5", "PM10": "PM10"})
)

df = df[
    df["parameter_name"].isin(["PM2.5", "PM10"])
].copy()

# ==========================================
# 7. CHECK DUPLICATE RECORDS
# ==========================================

duplicate_columns = [
    "station_id",
    "parameter_name",
    "period_start"
]

exact_duplicates = df.duplicated(
    keep="first"
)

print(
    "\nExact duplicate records:",
    exact_duplicates.sum()
)

df = df.drop_duplicates().copy()

key_duplicates = df[
    df.duplicated(
        subset=duplicate_columns,
        keep=False
    )
].copy()

key_duplicates.to_csv(
    REPORT_DIR / "duplicate_station_records.csv",
    index=False
)

if not key_duplicates.empty:

    raise ValueError(
        "Conflicting duplicate station-date-pollutant "
        "records found. Inspect reports/"
        "duplicate_station_records.csv before proceeding."
    )

# ==========================================
# 8. IDENTIFY INVALID MEASUREMENTS
# ==========================================

invalid_mask = (
    df[["mean", "min", "max", "n"]].isna().any(axis=1)
    | (df["mean"] < 0)
    | (df["min"] < 0)
    | (df["max"] < 0)
    | (df["n"] <= 0)
    | (df["min"] > df["max"])
    | (df["mean"] < df["min"])
    | (df["mean"] > df["max"])
)

invalid_records = df[invalid_mask].copy()

invalid_records.to_csv(
    REPORT_DIR / "invalid_measurements.csv",
    index=False
)

print(
    "Invalid measurement records:",
    len(invalid_records)
)

# Keep invalid records separately.
# Exclude them from the analytical dataset.
clean_df = df[~invalid_mask].copy()

# ==========================================
# 9. ADD TIME-BASED COLUMNS
# ==========================================

clean_df["year"] = clean_df["period_start"].dt.year

clean_df["month_number"] = (
    clean_df["period_start"].dt.month
)

clean_df["month"] = (
    clean_df["period_start"].dt.month_name()
)

clean_df["day"] = (
    clean_df["period_start"].dt.day
)

clean_df["day_of_week"] = (
    clean_df["period_start"].dt.day_name()
)

clean_df["quarter"] = (
    clean_df["period_start"].dt.quarter
)

# Delhi seasonal grouping
def get_season(month):

    if month in [12, 1, 2]:
        return "Winter"

    elif month in [3, 4, 5]:
        return "Summer"

    elif month in [6, 7, 8, 9]:
        return "Monsoon"

    else:
        return "Post-Monsoon"


clean_df["season"] = (
    clean_df["month_number"].apply(get_season)
)

# ==========================================
# 10. FLAG LOW OBSERVATION COUNTS
# ==========================================

# 18 observations = 75% of a 24-hour day.
# This is a screening threshold, not an automatic deletion rule.

clean_df["coverage_flag"] = np.where(
    clean_df["n"] < 18,
    "Low Coverage",
    "Adequate Coverage"
)

# ==========================================
# 11. SAVE CLEANED LONG-FORMAT DATA
# ==========================================

clean_df = clean_df.sort_values(
    ["period_start", "station_id", "parameter_name"]
)

long_file = (
    PROCESSED_DIR / "delhi_air_quality_clean_long.csv"
)

clean_df.to_csv(
    long_file,
    index=False
)

# ==========================================
# 12. CONVERT TO WIDE FORMAT
# ==========================================

index_columns = [
    "station_id",
    "period_start"
]

metadata_columns = [
    col for col in [
        "station_name",
        "state_name",
        "city_name",
        "latitude",
        "longitude"
    ]
    if col in clean_df.columns
]

value_columns = ["mean", "min", "max", "n"]

wide_df = clean_df.pivot(
    index=index_columns,
    columns="parameter_name",
    values=value_columns
)

wide_df.columns = [
    f"{pollutant}_{measurement}"
    for measurement, pollutant in wide_df.columns
]

wide_df = wide_df.reset_index()

# Attach station information
station_metadata = (
    clean_df[
        ["station_id"] + metadata_columns
    ]
    .drop_duplicates(subset=["station_id"])
)

wide_df = wide_df.merge(
    station_metadata,
    on="station_id",
    how="left",
    validate="many_to_one"
)

# Add time-based columns
wide_df["year"] = wide_df["period_start"].dt.year

wide_df["month_number"] = (
    wide_df["period_start"].dt.month
)

wide_df["month"] = (
    wide_df["period_start"].dt.month_name()
)

wide_df["day_of_week"] = (
    wide_df["period_start"].dt.day_name()
)

wide_df["season"] = (
    wide_df["month_number"].apply(get_season)
)

# ==========================================
# 13. SAVE FINAL WIDE DATASET
# ==========================================

wide_file = (
    PROCESSED_DIR / "delhi_air_quality_clean.csv"
)

wide_df.to_csv(
    wide_file,
    index=False
)

# ==========================================
# 14. GENERATE QUALITY REPORT
# ==========================================

quality_report = pd.DataFrame({
    "Metric": [
        "Original Records",
        "Valid Records",
        "Invalid Records",
        "Exact Duplicates Removed",
        "Conflicting Duplicate Records",
        "Unique Stations",
        "PM2.5 Records",
        "PM10 Records",
        "Wide Format Rows",
        "Low Coverage Records"
    ],

    "Value": [
        len(df) + len(invalid_dates),
        len(clean_df),
        len(invalid_records),
        exact_duplicates.sum(),
        len(key_duplicates),
        clean_df["station_id"].nunique(),
        (clean_df["parameter_name"] == "PM2.5").sum(),
        (clean_df["parameter_name"] == "PM10").sum(),
        len(wide_df),
        (clean_df["coverage_flag"] == "Low Coverage").sum()
    ]
})

quality_report.to_csv(
    REPORT_DIR / "data_quality_report.csv",
    index=False
)

# ==========================================
# 15. DISPLAY FINAL SUMMARY
# ==========================================

print("\n" + "=" * 60)
print("DATA CLEANING COMPLETED")
print("=" * 60)

print("\nOriginal Dataset:", len(df))
print("Cleaned Records:", len(clean_df))
print("Invalid Records:", len(invalid_records))

print(
    "Unique Stations:",
    clean_df["station_id"].nunique()
)

print(
    "Date Range:",
    clean_df["period_start"].min(),
    "to",
    clean_df["period_start"].max()
)

print("\nCleaned Dataset Shape:", clean_df.shape)
print("Wide Dataset Shape:", wide_df.shape)

print("\nPollutant Records:")
print(clean_df["parameter_name"].value_counts())

print("\nCoverage Status:")
print(clean_df["coverage_flag"].value_counts())

print("\nSaved Files:")
print(long_file)
print(wide_file)
print(REPORT_DIR / "data_quality_report.csv")

print("\nDATA CLEANING SUCCESSFUL!")
