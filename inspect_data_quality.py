
import pandas as pd

file = "reports/invalid_measurements.csv"

df = pd.read_csv(file)

print("=" * 55)
print("INVALID DATA RECORD INSPECTION")
print("=" * 55)

print("\nTotal invalid records:", len(df))

print("\nInvalid records by pollutant:")
print(df["parameter_name"].value_counts())

print("\nInvalid records by station:")
print(df["station_name"].value_counts())

print("\nDetailed invalid records:")
columns = [
    "station_name",
    "parameter_name",
    "period_start",
    "mean",
    "min",
    "max",
    "n"
]

print(df[columns].to_string(index=False))

print("\nChecking invalidity reasons:")

print("Missing numeric values:",
      df[["mean", "min", "max", "n"]].isna().any(axis=1).sum())

print("Negative measurements:",
      ((df[["mean", "min", "max"]] < 0).any(axis=1)).sum())

print("Invalid observation counts:",
      (df["n"] <= 0).sum())

print("Mean below minimum:",
      (df["mean"] < df["min"]).sum())

print("Mean above maximum:",
      (df["mean"] > df["max"]).sum())

print("Minimum greater than maximum:",
      (df["min"] > df["max"]).sum())

