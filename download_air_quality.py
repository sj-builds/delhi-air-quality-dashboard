
import pandas as pd
import requests
import json
import time
import calendar
from pathlib import Path
from io import StringIO
from getpass import getpass

# ==========================================
# 1. PROJECT CONFIGURATION
# ==========================================

BASE_URL = "https://airquality.xkdr.org"

START_DATE = "2017-01-01"
END_DATE = "2025-12-31"

SOURCE = "cpcb_caaqm"
CITY = "Delhi"

PARAMETERS = ["PM2.5", "PM10"]

BASE_DIR = Path(__file__).resolve().parent

RAW_DIR = BASE_DIR / "data" / "raw"
MONTHLY_DIR = RAW_DIR / "monthly"

RAW_DIR.mkdir(parents=True, exist_ok=True)
MONTHLY_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. API AUTHENTICATION
# ==========================================

API_KEY = getpass("Enter your XKDR API key: ")

if not API_KEY.strip():
    raise ValueError("API key cannot be empty.")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}

session = requests.Session()
session.headers.update(HEADERS)

# ==========================================
# 3. API REQUEST WITH RETRIES
# ==========================================

def api_request(url, params=None):

    for attempt in range(1, 5):

        try:
            response = session.get(
                url,
                params=params,
                timeout=120
            )

            # Check for unavailable historical data
            if response.status_code == 503:

                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {}

                if error_data.get("error") == "no_data":
                    return response

            # Retry temporary server/rate errors
            if response.status_code in [429, 500, 502, 503, 504]:

                if attempt == 4:
                    response.raise_for_status()

                wait = min(2 ** attempt, 30)

                print(
                    f"Request failed: {response.status_code}. "
                    f"Retrying in {wait} seconds..."
                )

                time.sleep(wait)
                continue

            response.raise_for_status()
            return response

        except requests.RequestException as error:

            if attempt == 4:
                raise

            wait = min(2 ** attempt, 30)

            print(f"Network error: {error}")
            print(f"Retrying in {wait} seconds...")

            time.sleep(wait)

    raise RuntimeError("API request failed after retries.")


# ==========================================
# 4. DOWNLOAD STATION METADATA
# ==========================================

print("\n" + "=" * 55)
print("DOWNLOADING DELHI MONITORING STATIONS")
print("=" * 55)

station_url = f"{BASE_URL}/v1/stations"

station_params = {
    "city": CITY,
    "source": SOURCE
}

response = api_request(
    station_url,
    params=station_params
)

station_data = response.json()

stations = station_data.get("data", [])

if not stations:
    raise RuntimeError("No monitoring stations returned by API.")

stations_df = pd.DataFrame(stations)

if "station_id" not in stations_df.columns:
    raise RuntimeError("Station metadata is missing station_id.")

stations_df = stations_df.drop_duplicates(
    subset=["station_id"]
)

stations_df.to_csv(
    RAW_DIR / "delhi_stations.csv",
    index=False
)

with open(
    RAW_DIR / "delhi_stations.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(station_data, file, indent=4)

print("Total monitoring stations:", len(stations_df))

print("\nStation names:")

if "station_name" in stations_df.columns:
    print(
        stations_df[
            ["station_id", "station_name"]
        ].to_string(index=False)
    )


# ==========================================
# 5. GENERATE MONTHLY DATE RANGES
# ==========================================

start = pd.Timestamp(START_DATE)
end = pd.Timestamp(END_DATE)

months = pd.date_range(
    start=start.replace(day=1),
    end=end,
    freq="MS"
)

# ==========================================
# 6. DOWNLOAD MONTHLY PM2.5 AND PM10 DATA
# ==========================================

print("\n" + "=" * 55)
print("STARTING AIR QUALITY DATA DOWNLOAD")
print("=" * 55)

all_data = []
download_log = []

measurement_url = f"{BASE_URL}/v1/measurements"

for index, month in enumerate(months, start=1):

    month_start = max(month, start)

    last_day = calendar.monthrange(
        month.year,
        month.month
    )[1]

    month_end = min(
        month.replace(day=last_day),
        end
    )

    start_str = month_start.strftime("%Y-%m-%d")
    end_str = month_end.strftime("%Y-%m-%d")

    month_name = month.strftime("%Y_%m")

    output_file = MONTHLY_DIR / (
        f"delhi_air_quality_{month_name}.csv"
    )

    print(
        f"\n[{index}/{len(months)}] "
        f"Downloading {month.strftime('%B %Y')}"
    )

    # Repeated parameter filters are intentional
    params = [
        ("city", CITY),
        ("source", SOURCE),
        ("parameter", "PM2.5"),
        ("parameter", "PM10"),
        ("start", start_str),
        ("end", end_str),
        ("agg", "daily"),
        ("format", "csv")
    ]

    try:

        response = api_request(
            measurement_url,
            params=params
        )

        if response.status_code == 503:

            print("No data published for this month.")

            download_log.append({
                "month": month_name,
                "status": "NO_DATA",
                "records": 0
            })

            continue

        # Detect incomplete API responses
        truncated = response.headers.get(
            "X-Truncated", "false"
        ).lower()

        if truncated == "true":
            raise RuntimeError(
                f"API returned truncated data for {month_name}."
            )

        if not response.text.strip():
            print("Empty response received.")

            download_log.append({
                "month": month_name,
                "status": "EMPTY",
                "records": 0
            })

            continue

        # Convert API CSV response into DataFrame
        monthly_df = pd.read_csv(
            StringIO(response.text)
        )

        if monthly_df.empty:

            print("No observations available.")

            download_log.append({
                "month": month_name,
                "status": "EMPTY",
                "records": 0
            })

            continue

        # Validate expected columns
        required_columns = {
            "station_id",
            "parameter_name",
            "period_start",
            "mean",
            "min",
            "max",
            "n"
        }

        missing_columns = (
            required_columns - set(monthly_df.columns)
        )

        if missing_columns:
            raise ValueError(
                f"Missing columns: {missing_columns}"
            )

        # Save individual monthly file
        monthly_df.to_csv(
            output_file,
            index=False
        )

        all_data.append(monthly_df)

        record_count = len(monthly_df)

        print(
            f"Downloaded successfully: "
            f"{record_count:,} records"
        )

        download_log.append({
            "month": month_name,
            "status": "SUCCESS",
            "records": record_count
        })

    except Exception as error:

        print(f"ERROR: {error}")

        download_log.append({
            "month": month_name,
            "status": "FAILED",
            "records": 0,
            "error": str(error)
        })

        # Stop instead of silently producing an
        # incomplete consolidated dataset.
        raise


# ==========================================
# 7. COMBINE MONTHLY DATASETS
# ==========================================

print("\n" + "=" * 55)
print("COMBINING MONTHLY DATA")
print("=" * 55)

if not all_data:
    raise RuntimeError("No monthly observations downloaded.")

combined_df = pd.concat(
    all_data,
    ignore_index=True
)

# ==========================================
# 8. ADD STATION INFORMATION
# ==========================================

station_columns = [
    column for column in [
        "station_id",
        "station_name",
        "state_name",
        "city_name",
        "source",
        "latitude",
        "longitude",
        "first_seen",
        "last_seen"
    ]
    if column in stations_df.columns
]

station_lookup = stations_df[station_columns].copy()

combined_df = combined_df.merge(
    station_lookup,
    on="station_id",
    how="left",
    validate="many_to_one"
)

# ==========================================
# 9. FORMAT AND SAVE DATASET
# ==========================================

combined_df["period_start"] = pd.to_datetime(
    combined_df["period_start"],
    errors="coerce"
)

combined_df["year"] = (
    combined_df["period_start"].dt.year
)

combined_df["month"] = (
    combined_df["period_start"].dt.month_name()
)

combined_df["day_of_week"] = (
    combined_df["period_start"].dt.day_name()
)

combined_df = combined_df.sort_values(
    ["period_start", "station_id", "parameter_name"]
)

combined_df = combined_df.reset_index(drop=True)

final_file = RAW_DIR / "delhi_air_quality_daily_raw.csv"

combined_df.to_csv(
    final_file,
    index=False
)

# ==========================================
# 10. SAVE DOWNLOAD LOG
# ==========================================

log_df = pd.DataFrame(download_log)

log_df.to_csv(
    RAW_DIR / "download_log.csv",
    index=False
)

# ==========================================
# 11. FINAL SUMMARY
# ==========================================

print("\n" + "=" * 55)
print("DOWNLOAD COMPLETED")
print("=" * 55)

print("Total records:", f"{len(combined_df):,}")

print(
    "Unique stations:",
    combined_df["station_id"].nunique()
)

print(
    "Available pollutants:",
    combined_df["parameter_name"].unique()
)

print(
    "Available date range:",
    combined_df["period_start"].min(),
    "to",
    combined_df["period_start"].max()
)

print("\nRecords by pollutant:")

print(
    combined_df["parameter_name"].value_counts()
)

print("\nDownload status:")

print(log_df["status"].value_counts())

print("\nFinal dataset saved at:")
print(final_file)

print("\nStation metadata saved at:")
print(RAW_DIR / "delhi_stations.csv")

print("\nDownload log saved at:")
print(RAW_DIR / "download_log.csv")

print("\nNext step: Inspect the downloaded dataset.")
