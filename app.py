from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================================
# DELHI AIR QUALITY ANALYTICS DASHBOARD
# Reads the existing wide, cleaned dataset produced by clean_air_quality.py.
# No changes are made to source or processed data.
# ============================================================================

st.set_page_config(
    page_title="Delhi Air Quality | Analytics",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_DIR = Path(__file__).resolve().parent
DATA_PATH = APP_DIR / "data" / "processed" / "delhi_air_quality_clean.csv"

PM25 = "PM2.5_mean"
PM10 = "PM10_mean"
POLLUTANT_COLUMNS = [PM25, PM10]
POLLUTANT_LABELS = {PM25: "PM2.5", PM10: "PM10"}
POLLUTANT_COLORS = {"PM2.5": "#38BDF8", "PM10": "#F5B942"}
POLLUTANT_UNITS = "µg/m³"  # Confirmed in the source measurement sample.
SEASON_ORDER = ["Winter", "Summer", "Monsoon", "Post-Monsoon"]
WEEKDAY_ORDER = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]


# ============================================================================
# VISUAL THEME
# ============================================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

    :root {
        --app-bg: #0b1220;
        --panel: #111c2e;
        --panel-2: #152238;
        --line: rgba(148, 163, 184, .16);
        --muted: #91a2b8;
        --text: #edf4ff;
        --cyan: #38bdf8;
    }

    .stApp {
        background:
            radial-gradient(circle at 82% 0%, rgba(56,189,248,.09), transparent 28%),
            linear-gradient(180deg, #0b1220 0%, #0c1626 100%);
        color: var(--text);
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    [data-testid="stHeader"] { background: rgba(11, 18, 32, .84); }

    [data-testid="stSidebar"] {
        background: #0e192a;
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] > div:first-child { padding-top: 1.25rem; }

    h1, h2, h3 {
        font-family: 'Manrope', sans-serif !important;
        letter-spacing: -.035em;
        color: #f3f7ff;
    }
    h1 { font-size: 2.25rem !important; font-weight: 800 !important; }
    h2 { font-size: 1.45rem !important; font-weight: 750 !important; }
    h3 { font-size: 1.08rem !important; font-weight: 700 !important; }

    .hero {
        padding: 1.55rem 1.7rem;
        border: 1px solid rgba(125, 211, 252, .20);
        border-radius: 20px;
        background: linear-gradient(115deg, rgba(18,40,65,.98), rgba(15,27,46,.97));
        margin-bottom: 1.1rem;
        box-shadow: 0 18px 50px rgba(0,0,0,.18);
    }
    .eyebrow {
        color: #7dd3fc;
        font-size: .70rem;
        font-weight: 700;
        letter-spacing: .16em;
        text-transform: uppercase;
        margin-bottom: .45rem;
    }
    .hero-title {
        color: #f4f8ff;
        font-family: 'Manrope', sans-serif;
        font-size: clamp(1.65rem, 3vw, 2.45rem);
        line-height: 1.15;
        font-weight: 800;
        letter-spacing: -.045em;
    }
    .hero-subtitle {
        color: #a9bbd1;
        margin-top: .6rem;
        font-size: .94rem;
        max-width: 850px;
    }
    .section-kicker {
        color: #7dd3fc;
        font-size: .70rem;
        font-weight: 700;
        letter-spacing: .14em;
        text-transform: uppercase;
        margin: .2rem 0 .35rem;
    }
    .metric-card {
        background: linear-gradient(145deg, rgba(21,34,56,.98), rgba(16,28,46,.98));
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 1rem 1.1rem .95rem;
        min-height: 116px;
        box-shadow: 0 10px 30px rgba(0,0,0,.12);
    }
    .metric-label {
        color: #9eb0c7;
        font-size: .75rem;
        font-weight: 700;
        letter-spacing: .04em;
    }
    .metric-value {
        color: #f4f8ff;
        font-family: 'Manrope', sans-serif;
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -.04em;
        line-height: 1.15;
        margin-top: .45rem;
    }
    .metric-note { color: #8094ad; font-size: .70rem; margin-top: .42rem; }
    .small-note { color: #91a2b8; font-size: .78rem; }
    .stTabs [data-baseweb="tab-list"] {
        gap: .35rem;
        border-bottom: 1px solid var(--line);
    }
    .stTabs [data-baseweb="tab"] { color: #9fb0c5; padding: .65rem .95rem; }
    .stTabs [aria-selected="true"] { color: #7dd3fc !important; }
    div[data-testid="stDownloadButton"] button { border-radius: 10px; }
    div[data-testid="stAlert"] { border-radius: 12px; }
    #MainMenu, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
# DATA LOADING, VALIDATION AND DERIVED FIELDS
# ============================================================================

@st.cache_data(show_spinner="Loading and validating Delhi air-quality data...")
def load_data(file_path: str, file_mtime: float) -> pd.DataFrame:
    """Load the cleaned wide dataset and validate its analytical structure."""
    del file_mtime  # Included in the cache key so edits to the CSV invalidate cache.

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at: {path}\n"
            "Run clean_air_quality.py before starting the dashboard."
        )

    data = pd.read_csv(path, low_memory=False)
    required_columns = {"station_id", "station_name", "period_start", PM25, PM10}
    missing_columns = sorted(required_columns.difference(data.columns))
    if missing_columns:
        raise ValueError(
            "The cleaned dataset is missing required columns: "
            + ", ".join(missing_columns)
        )

    original_rows = len(data)
    data["period_start"] = pd.to_datetime(data["period_start"], errors="coerce")
    invalid_dates = int(data["period_start"].isna().sum())
    missing_station_ids = int(data["station_id"].isna().sum())
    data = data.dropna(subset=["period_start", "station_id"]).copy()

    negative_values_replaced = 0
    for column in POLLUTANT_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")
        # Negative particulate concentration is not physically meaningful.
        negative_mask = data[column] < 0
        negative_values_replaced += int(negative_mask.sum())
        data.loc[negative_mask, column] = np.nan

    data["station_id"] = data["station_id"].astype(str)
    data["station_name"] = data["station_name"].fillna(data["station_id"]).astype(str)

    # The cleaning pipeline uses these same seasonal month boundaries.
    # Deriving them from the date prevents stale or inconsistent text labels.
    month = data["period_start"].dt.month
    data["season"] = np.select(
        [month.isin([12, 1, 2]), month.isin([3, 4, 5]), month.isin([6, 7, 8, 9]), month.isin([10, 11])],
        ["Winter", "Summer", "Monsoon", "Post-Monsoon"],
        default="Unknown",
    )
    data["day_of_week"] = data["period_start"].dt.day_name()
    data["year"] = data["period_start"].dt.year
    data["year_month"] = data["period_start"].dt.to_period("M").astype(str)

    # A wide cleaned table should have one row per station and date.
    exact_duplicates_removed = int(data.duplicated().sum())
    data = data.drop_duplicates()
    duplicate_key_mask = data.duplicated(["station_id", "period_start"], keep=False)
    if duplicate_key_mask.any():
        sample_keys = (
            data.loc[duplicate_key_mask, ["station_id", "period_start"]]
            .drop_duplicates()
            .head(5)
            .astype(str)
            .to_dict("records")
        )
        raise ValueError(
            "The cleaned dataset contains multiple rows for the same station/date. "
            f"Example duplicate keys: {sample_keys}. Recheck the cleaning/pivot step."
        )

    data = data.sort_values(["period_start", "station_id"]).reset_index(drop=True)
    data.attrs["original_rows"] = original_rows
    data.attrs["invalid_dates"] = invalid_dates
    data.attrs["missing_station_ids"] = missing_station_ids
    data.attrs["exact_duplicates_removed"] = exact_duplicates_removed
    data.attrs["negative_values_replaced"] = negative_values_replaced
    data.attrs["rows_removed"] = original_rows - len(data)
    return data


def make_station_options(data: pd.DataFrame) -> dict[str, str]:
    """Return unique, readable labels mapped to station IDs."""
    station_map = (
        data[["station_id", "station_name"]]
        .drop_duplicates(subset=["station_id"])
        .sort_values(["station_name", "station_id"])
    )
    name_counts = station_map["station_name"].value_counts()
    options: dict[str, str] = {}
    for row in station_map.itertuples(index=False):
        name = row.station_name
        station_id = row.station_id
        # Disambiguate duplicate station names while preserving readable labels.
        label = f"{name} ({station_id})" if name_counts[name] > 1 else name
        options[label] = station_id
    return options


def metric_card(label: str, value: str, note: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_chart(fig: go.Figure, height: int = 390) -> go.Figure:
    """Apply a consistent dark theme to Plotly charts."""
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#cbd5e1", size=12),
        title=dict(font=dict(size=15, color="#edf4ff")),
        margin=dict(l=18, r=22, t=68, b=42),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        hoverlabel=dict(
            bgcolor="#142238",
            bordercolor="#334155",
            font=dict(color="#f8fafc"),
        ),
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="rgba(148,163,184,.2)",
        tickfont=dict(color="#9fb0c5"),
        title_font=dict(color="#a9bbd1"),
    )
    fig.update_yaxes(
        gridcolor="rgba(148,163,184,.12)",
        zeroline=False,
        linecolor="rgba(148,163,184,.2)",
        tickfont=dict(color="#9fb0c5"),
        title_font=dict(color="#a9bbd1"),
    )
    return fig


def melt_pollutants(
    data: pd.DataFrame,
    index_columns: list[str],
    *,
    drop_missing: bool = True,
) -> pd.DataFrame:
    long_data = data.melt(
        id_vars=index_columns,
        value_vars=POLLUTANT_COLUMNS,
        var_name="Pollutant",
        value_name="Concentration",
    )
    long_data["Pollutant"] = long_data["Pollutant"].map(POLLUTANT_LABELS)
    return long_data.dropna(subset=["Concentration"]) if drop_missing else long_data


def download_csv(data: pd.DataFrame, filename: str, label: str) -> None:
    csv_data = data.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label=label,
        data=csv_data,
        file_name=filename,
        mime="text/csv",
        width="content",
    )


def format_number(value: Any, decimals: int = 2) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{float(value):,.{decimals}f}"


# ============================================================================
# LOAD DATA
# ============================================================================

try:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Expected file: {DATA_PATH}\n"
            "Check that app.py is in the project root and the cleaned CSV is in "
            "data/processed/."
        )
    data = load_data(str(DATA_PATH), DATA_PATH.stat().st_mtime)
except Exception as error:
    st.error("The dashboard could not load the cleaned dataset.")
    st.exception(error)
    st.stop()

if data.empty:
    st.error("The cleaned dataset has no valid station-date records.")
    st.stop()

station_options = make_station_options(data)
station_labels = list(station_options.keys())


# ============================================================================
# SIDEBAR FILTERS
# ============================================================================

with st.sidebar:
    st.markdown('<div class="eyebrow">ENVIRONMENTAL INTELLIGENCE</div>', unsafe_allow_html=True)
    st.title("Delhi Air Quality")
    st.caption("Interactive particulate-matter analytics")
    st.divider()

    min_date = data["period_start"].min().date()
    max_date = data["period_start"].max().date()

    st.markdown("#### Observation period")
    chosen_dates = st.date_input(
        "Choose start and end dates",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        format="DD/MM/YYYY",
        label_visibility="collapsed",
    )
    if isinstance(chosen_dates, (tuple, list)):
        if len(chosen_dates) >= 2:
            start_date, end_date = chosen_dates[0], chosen_dates[-1]
        elif len(chosen_dates) == 1:
            # Streamlit can return a one-element tuple while a range is being selected.
            start_date = end_date = chosen_dates[0]
        else:
            # A cleared range falls back to the full available period.
            start_date, end_date = min_date, max_date
    elif chosen_dates is None:
        start_date, end_date = min_date, max_date
    else:
        start_date = end_date = chosen_dates

    st.markdown("#### Monitoring stations")
    selected_station_labels = st.multiselect(
        "Leave empty to include all stations",
        options=station_labels,
        default=[],
        placeholder="All monitoring stations",
        label_visibility="collapsed",
    )
    if selected_station_labels:
        selected_station_ids = [station_options[label] for label in selected_station_labels]
    else:
        selected_station_ids = list(station_options.values())

    st.markdown("#### Seasons")
    selected_seasons = st.multiselect(
        "Leave empty to include all seasons",
        options=SEASON_ORDER,
        default=[],
        placeholder="All seasons",
        label_visibility="collapsed",
    )
    if not selected_seasons:
        selected_seasons = SEASON_ORDER.copy()

    st.divider()
    st.caption(f"Available data: {min_date:%d %b %Y} - {max_date:%d %b %Y}")
    st.caption(f"Stations in dataset: {len(station_options)}")
    st.caption(f"Source records: {len(data):,}")


# ============================================================================
# FILTER DATA - ALL TABS USE THE SAME FILTERED DATAFRAME
# ============================================================================

start_timestamp = pd.Timestamp(start_date)
end_timestamp_exclusive = pd.Timestamp(end_date) + pd.Timedelta(days=1)
filtered = data.loc[
    (data["period_start"] >= start_timestamp)
    & (data["period_start"] < end_timestamp_exclusive)
    & data["station_id"].isin(selected_station_ids)
    & data["season"].isin(selected_seasons)
].copy()

if filtered.empty:
    st.warning("No records match the selected filters. Adjust the date, station or season filters.")
    st.stop()

paired = filtered[[PM25, PM10]].dropna()
pm25_average = filtered[PM25].mean()
pm10_average = filtered[PM10].mean()
station_count = filtered["station_id"].nunique()
record_count = len(filtered)
paired_count = len(paired)
paired_correlation = (
    paired[PM25].corr(paired[PM10]) if paired_count >= 2 else np.nan
)


# ============================================================================
# HEADER AND KPI SUMMARY
# ============================================================================

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">DELHI • AIR QUALITY ANALYTICS</div>
        <div class="hero-title">Understanding Delhi's Air Pollution</div>
        <div class="hero-subtitle">
            Explore PM2.5 and PM10 measurements across monitoring stations,
            seasons and time. Apply filters to investigate specific periods
            and locations.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-kicker">FILTERED DATASET OVERVIEW</div>', unsafe_allow_html=True)
st.caption(
    f"{start_date:%d %b %Y} to {end_date:%d %b %Y}  ·  "
    f"{station_count:,} stations  ·  {record_count:,} station-date records"
)

kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4, gap="medium")
with kpi_1:
    metric_card("AVERAGE PM2.5", format_number(pm25_average), f"Mean concentration ({POLLUTANT_UNITS})")
with kpi_2:
    metric_card("AVERAGE PM10", format_number(pm10_average), f"Mean concentration ({POLLUTANT_UNITS})")
with kpi_3:
    metric_card("MONITORING STATIONS", f"{station_count:,}", "Stations represented by filters")
with kpi_4:
    paired_rate = paired_count / record_count * 100 if record_count else 0
    metric_card("PAIRED OBSERVATIONS", f"{paired_count:,}", f"Both pollutants available · {paired_rate:.1f}%")

st.write("")


# ============================================================================
# DASHBOARD TABS
# ============================================================================

overview_tab, trends_tab, stations_tab, explorer_tab = st.tabs(
    ["Overview", "Time & Season Trends", "Station Comparison", "Data Explorer"]
)


# ----------------------------------------------------------------------------
# OVERVIEW
# ----------------------------------------------------------------------------
with overview_tab:
    st.subheader("Pollution snapshot")
    left_column, right_column = st.columns([1.55, 1], gap="large")

    monthly_summary = (
        filtered.assign(Month=filtered["period_start"].dt.to_period("M").dt.to_timestamp())
        .groupby("Month")[POLLUTANT_COLUMNS]
        .mean()
    )
    # Reinsert empty months so a line chart cannot imply continuous coverage
    # across periods for which the dataset contains no observations.
    complete_months = pd.period_range(
        start=pd.Timestamp(start_date).to_period("M"),
        end=pd.Timestamp(end_date).to_period("M"),
        freq="M",
    ).to_timestamp()
    monthly_summary = (
        monthly_summary.reindex(complete_months)
        .rename_axis("Month")
        .reset_index()
    )
    monthly_long = melt_pollutants(monthly_summary, ["Month"], drop_missing=False)

    with left_column:
        fig = px.line(
            monthly_long,
            x="Month",
            y="Concentration",
            color="Pollutant",
            markers=True,
            color_discrete_map=POLLUTANT_COLORS,
            labels={
                "Month": "Month",
                "Concentration": f"Mean concentration ({POLLUTANT_UNITS})",
                "Pollutant": "Pollutant",
            },
            title="Monthly particulate-matter trend",
        )
        fig.update_traces(line_width=2.6, marker_size=5, connectgaps=False)
        fig.update_xaxes(tickformat="%b\n%Y")
        st.plotly_chart(style_chart(fig, 425), width="stretch", config={"displaylogo": False})

    with right_column:
        seasonal_summary = (
            filtered.groupby("season")[POLLUTANT_COLUMNS]
            .mean()
            .reindex(SEASON_ORDER)
            .dropna(how="all")
            .reset_index()
        )
        seasonal_long = melt_pollutants(seasonal_summary, ["season"])
        fig = px.bar(
            seasonal_long,
            x="season",
            y="Concentration",
            color="Pollutant",
            barmode="group",
            text_auto=".1f",
            color_discrete_map=POLLUTANT_COLORS,
            labels={
                "season": "Season",
                "Concentration": f"Mean concentration ({POLLUTANT_UNITS})",
                "Pollutant": "Pollutant",
            },
            title="Seasonal comparison",
        )
        st.plotly_chart(style_chart(fig, 425), width="stretch", config={"displaylogo": False})

    st.subheader("Weekday pattern")
    weekday_summary = (
        filtered.groupby("day_of_week")[POLLUTANT_COLUMNS]
        .mean()
        .reindex(WEEKDAY_ORDER)
        .dropna(how="all")
        .reset_index()
    )
    weekday_long = melt_pollutants(weekday_summary, ["day_of_week"])
    fig = px.bar(
        weekday_long,
        x="day_of_week",
        y="Concentration",
        color="Pollutant",
        barmode="group",
        color_discrete_map=POLLUTANT_COLORS,
        labels={
            "day_of_week": "Day of week",
            "Concentration": f"Mean concentration ({POLLUTANT_UNITS})",
            "Pollutant": "Pollutant",
        },
        title="Average concentration by weekday",
    )
    st.plotly_chart(style_chart(fig, 380), width="stretch", config={"displaylogo": False})

    st.subheader("Relationship between PM2.5 and PM10")
    correlation_column, scatter_column = st.columns([1, 2], gap="large")
    with correlation_column:
        metric_card(
            "PEARSON CORRELATION",
            format_number(paired_correlation, 3),
            f"Calculated from {paired_count:,} paired observations",
        )
        st.markdown(
            '<p class="small-note">Correlation measures linear association. It does not establish causation, and pooled station data may reflect differences between locations and dates.</p>',
            unsafe_allow_html=True,
        )
    with scatter_column:
        if paired_count >= 2:
            scatter_data = paired.sample(n=min(7000, paired_count), random_state=42)
            fig = px.scatter(
                scatter_data,
                x=PM25,
                y=PM10,
                opacity=0.38,
                render_mode="webgl",
                labels={
                    PM25: f"PM2.5 ({POLLUTANT_UNITS})",
                    PM10: f"PM10 ({POLLUTANT_UNITS})",
                },
                title="Paired station-date observations",
            )
            fig.update_traces(marker=dict(color="#38BDF8", size=5))
            st.plotly_chart(style_chart(fig, 385), width="stretch", config={"displaylogo": False})
        else:
            st.info("At least two paired observations are required to calculate correlation.")


# ----------------------------------------------------------------------------
# TIME AND SEASON TRENDS
# ----------------------------------------------------------------------------
with trends_tab:
    st.subheader("Time-series analysis")
    frequency = st.radio(
        "Choose time aggregation",
        ["Monthly", "Quarterly", "Yearly"],
        horizontal=True,
    )
    period_codes = {"Monthly": "M", "Quarterly": "Q", "Yearly": "Y"}
    trend_data = filtered.copy()
    trend_data["Period"] = (
        trend_data["period_start"].dt.to_period(period_codes[frequency]).dt.to_timestamp()
    )
    trend_summary = trend_data.groupby("Period")[POLLUTANT_COLUMNS].mean()
    complete_periods = pd.period_range(
        start=pd.Timestamp(start_date).to_period(period_codes[frequency]),
        end=pd.Timestamp(end_date).to_period(period_codes[frequency]),
        freq=period_codes[frequency],
    ).to_timestamp()
    trend_summary = (
        trend_summary.reindex(complete_periods)
        .rename_axis("Period")
        .reset_index()
    )
    trend_long = melt_pollutants(trend_summary, ["Period"], drop_missing=False)
    fig = px.line(
        trend_long,
        x="Period",
        y="Concentration",
        color="Pollutant",
        markers=(frequency != "Monthly"),
        color_discrete_map=POLLUTANT_COLORS,
        labels={
            "Period": frequency,
            "Concentration": f"Mean concentration ({POLLUTANT_UNITS})",
            "Pollutant": "Pollutant",
        },
        title=f"{frequency} average particulate-matter concentration",
    )
    fig.update_traces(connectgaps=False)
    st.plotly_chart(style_chart(fig, 455), width="stretch", config={"displaylogo": False})

    st.subheader("Seasonal statistics")
    season_statistics = (
        filtered.groupby("season")[POLLUTANT_COLUMNS]
        .agg(["mean", "median", "count"])
        .reindex(SEASON_ORDER)
    )
    season_statistics.columns = [
        f"{POLLUTANT_LABELS[pollutant]}_{statistic}"
        for pollutant, statistic in season_statistics.columns
    ]
    st.dataframe(
        season_statistics.style.format("{:,.2f}", na_rep="—"),
        width="stretch",
    )

    st.subheader("Monthly data coverage")
    coverage = (
        filtered.assign(Month=filtered["period_start"].dt.to_period("M").astype(str))
        .groupby("Month")
        .agg(
            Station_date_records=("station_id", "size"),
            Stations=("station_id", "nunique"),
            PM25_available=(PM25, "count"),
            PM10_available=(PM10, "count"),
        )
    )
    complete_month_labels = pd.period_range(
        start=pd.Timestamp(start_date).to_period("M"),
        end=pd.Timestamp(end_date).to_period("M"),
        freq="M",
    ).astype(str)
    coverage = (
        coverage.reindex(complete_month_labels, fill_value=0)
        .rename_axis("Month")
        .reset_index()
    )
    fig = px.bar(
        coverage,
        x="Month",
        y="Station_date_records",
        labels={
            "Month": "Month",
            "Station_date_records": "Station-date records",
        },
        title="Available station-date records by month",
    )
    fig.update_traces(marker_color="#648CFF")
    st.plotly_chart(style_chart(fig, 350), width="stretch", config={"displaylogo": False})
    st.dataframe(coverage, width="stretch", hide_index=True)
    download_csv(coverage, "delhi_monthly_data_coverage.csv", "Download monthly coverage")


# ----------------------------------------------------------------------------
# STATION COMPARISON
# ----------------------------------------------------------------------------
with stations_tab:
    st.subheader("Compare monitoring stations")
    pollutant_column = st.selectbox(
        "Pollutant to rank",
        options=POLLUTANT_COLUMNS,
        format_func=lambda column: POLLUTANT_LABELS[column],
    )

    station_statistics = (
        filtered.groupby(["station_id", "station_name"])[pollutant_column]
        .agg(Mean="mean", Median="median", Observations="count")
        .dropna(subset=["Mean"])
        .reset_index()
    )

    if station_statistics.empty:
        st.info("No valid measurements are available for this pollutant in the selected filters.")
    else:
        maximum_observations = int(station_statistics["Observations"].max())
        minimum_observations = st.slider(
            "Minimum observations required for ranking",
            min_value=1,
            max_value=max(1, maximum_observations),
            value=1,
            help="Increase this threshold to exclude stations with limited data coverage.",
        )
        eligible_stations = station_statistics.loc[
            station_statistics["Observations"] >= minimum_observations
        ].copy()

        if eligible_stations.empty:
            st.warning("No station meets this minimum-observation threshold.")
        else:
            station_name_counts = eligible_stations["station_name"].value_counts()
            eligible_stations["station_display"] = eligible_stations.apply(
                lambda row: (
                    f"{row['station_name']} ({row['station_id']})"
                    if station_name_counts[row["station_name"]] > 1
                    else row["station_name"]
                ),
                axis=1,
            )
            top_maximum = min(30, len(eligible_stations))
            default_top = min(10, top_maximum)
            top_n = st.slider(
                "Number of stations to display",
                min_value=1,
                max_value=top_maximum,
                value=default_top,
            )
            ranked = (
                eligible_stations.sort_values("Mean", ascending=False)
                .head(top_n)
            )

            chart_data = ranked.sort_values("Mean", ascending=True)
            fig = px.bar(
                chart_data,
                x="Mean",
                y="station_display",
                orientation="h",
                text="Mean",
                hover_data={
                    "station_id": True,
                    "Median": ":.2f",
                    "Observations": True,
                    "Mean": ":.2f",
                },
                labels={
                    "Mean": f"Mean concentration ({POLLUTANT_UNITS})",
                    "station_display": "Monitoring station",
                },
                title=f"Top {len(ranked)} stations by {POLLUTANT_LABELS[pollutant_column]}",
            )
            fig.update_traces(
                marker_color="#38BDF8",
                texttemplate="%{text:.1f}",
                textposition="outside",
                cliponaxis=False,
            )
            fig.update_layout(yaxis=dict(automargin=True))
            st.plotly_chart(
                style_chart(fig, max(420, len(ranked) * 35)),
                width="stretch",
                config={"displaylogo": False},
            )

            st.dataframe(
                ranked.style.format({"Mean": "{:,.2f}", "Median": "{:,.2f}"}),
                width="stretch",
                hide_index=True,
            )
            download_csv(ranked, "delhi_station_comparison.csv", "Download station comparison")

    st.subheader("Station data coverage")
    station_coverage = (
        filtered.groupby(["station_id", "station_name"])
        .agg(
            Available_PM25=(PM25, "count"),
            Available_PM10=(PM10, "count"),
            Station_date_records=("period_start", "nunique"),
        )
        .reset_index()
        .sort_values("Station_date_records", ascending=False)
    )
    st.dataframe(station_coverage, width="stretch", hide_index=True)
    download_csv(station_coverage, "delhi_station_coverage.csv", "Download station coverage")


# ----------------------------------------------------------------------------
# DATA EXPLORER AND QUALITY CHECKS
# ----------------------------------------------------------------------------
with explorer_tab:
    st.subheader("Explore filtered observations")
    st.caption(
        "Search, inspect and export the station-date records selected by the sidebar filters. "
        "Missing pollutant observations remain blank; they are not converted to zero."
    )

    search_text = st.text_input(
        "Search station name or ID",
        placeholder="Start typing a station name or station ID...",
    )
    display_data = filtered.copy()
    if search_text.strip():
        search_pattern = search_text.strip()
        match_mask = (
            display_data["station_name"].str.contains(search_pattern, case=False, na=False, regex=False)
            | display_data["station_id"].str.contains(search_pattern, case=False, na=False, regex=False)
        )
        display_data = display_data.loc[match_mask]

    preferred_columns = [
        "period_start", "station_id", "station_name",
        PM25, PM10, "PM2.5_n", "PM10_n", "season", "day_of_week",
    ]
    visible_columns = [column for column in preferred_columns if column in display_data.columns]

    display_data = display_data.sort_values("period_start")
    st.caption(f"{len(display_data):,} records match the current filters and search.")

    # Avoid sending the entire 100k+ row dataset to the browser at once.
    rows_per_page = st.selectbox(
        "Rows per page",
        options=[100, 250, 500, 1000],
        index=1,
    )
    total_pages = max(1, int(np.ceil(len(display_data) / rows_per_page)))
    page_number = st.number_input(
        "Page",
        min_value=1,
        max_value=total_pages,
        value=1,
        step=1,
    )
    first_row = (int(page_number) - 1) * rows_per_page
    last_row = min(first_row + rows_per_page, len(display_data))
    st.caption(
        f"Showing rows {first_row + 1:,}-{last_row:,} of {len(display_data):,}. "
        "The download includes every matching record, not just this page."
    )
    st.dataframe(
        display_data.iloc[first_row:last_row][visible_columns],
        width="stretch",
        hide_index=True,
        height=480,
    )
    download_csv(display_data, "delhi_air_quality_filtered.csv", "Download all matching observations (CSV)")

    st.subheader("Data quality snapshot")
    quality_col_1, quality_col_2, quality_col_3, quality_col_4 = st.columns(4)
    with quality_col_1:
        metric_card(
            "MISSING PM2.5",
            f"{display_data[PM25].isna().sum():,}",
            "Unavailable PM2.5 measurements",
        )
    with quality_col_2:
        metric_card(
            "MISSING PM10",
            f"{display_data[PM10].isna().sum():,}",
            "Unavailable PM10 measurements",
        )
    with quality_col_3:
        both_missing = int(display_data[POLLUTANT_COLUMNS].isna().all(axis=1).sum())
        metric_card("BOTH MISSING", f"{both_missing:,}", "Neither pollutant available")
    with quality_col_4:
        both_available = int(display_data[POLLUTANT_COLUMNS].notna().all(axis=1).sum())
        metric_card("BOTH AVAILABLE", f"{both_available:,}", "Paired pollutant measurements")

    # Preserve extreme readings but make them visible for quality review.
    st.markdown(
        '<p class="small-note">High values are retained rather than silently removed. ' 
        'Review them against the source data before deciding whether they are valid observations.</p>',
        unsafe_allow_html=True,
    )
    extreme_threshold = st.number_input(
        f"Flag measurements above ({POLLUTANT_UNITS})",
        min_value=0.0,
        value=500.0,
        step=50.0,
    )
    extreme_rows = display_data.loc[
        (display_data[PM25] > extreme_threshold)
        | (display_data[PM10] > extreme_threshold),
        [column for column in ["period_start", "station_id", "station_name", PM25, PM10] if column in display_data.columns],
    ].copy()
    st.caption(f"{len(extreme_rows):,} station-date rows exceed the selected review threshold.")
    if not extreme_rows.empty:
        with st.expander("Inspect flagged high measurements"):
            st.dataframe(extreme_rows, width="stretch", hide_index=True)
            download_csv(extreme_rows, "delhi_measurements_for_review.csv", "Download flagged measurements")

    with st.expander("Dataset loading and validation log"):
        validation_summary = pd.DataFrame(
            {
                "Validation check": [
                    "Rows in source CSV",
                    "Invalid dates excluded",
                    "Rows with missing station ID excluded",
                    "Exact duplicate rows removed",
                    "Negative pollutant values replaced with missing",
                    "Rows available to dashboard",
                ],
                "Count": [
                    data.attrs.get("original_rows", len(data)),
                    data.attrs.get("invalid_dates", 0),
                    data.attrs.get("missing_station_ids", 0),
                    data.attrs.get("exact_duplicates_removed", 0),
                    data.attrs.get("negative_values_replaced", 0),
                    len(data),
                ],
            }
        )
        st.dataframe(validation_summary, width="stretch", hide_index=True)


# ============================================================================
# FOOTER AND METHODOLOGY DISCLOSURE
# ============================================================================

st.divider()
st.markdown(
    f"""
    <div class="small-note">
        <b>Data period:</b> {data['period_start'].min():%d %B %Y} to {data['period_start'].max():%d %B %Y}.
        <b>Measurement:</b> PM2.5 and PM10 concentrations in {POLLUTANT_UNITS}.
        <br><br>
        <b>Methodology:</b> Averages are calculated from available station-date measurements
        in the selected dataset. Each available station-date row contributes equally to the
        displayed mean. Coverage can differ across stations and dates; therefore, the result
        is not a population-weighted or personal-exposure estimate for Delhi. PM2.5 and PM10
        concentrations are not AQI values.
    </div>
    """,
    unsafe_allow_html=True,
)
