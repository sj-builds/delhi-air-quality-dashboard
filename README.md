# NCRAirLens - Delhi-NCR Air Quality Intelligence Dashboard

**See the Air. Understand the Data.**

NCRAirLens is an interactive air quality analytics platform designed to explore and understand Delhi's air pollution patterns through data analysis and visualization.

The project analyzes historical PM2.5 and PM10 measurements collected from monitoring stations across Delhi. It identifies pollution trends, seasonal variations, weekday patterns, and station-level differences through an interactive Streamlit dashboard.

<p align="center">

  **Live Dashboard:** [ADD YOUR STREAMLIT URL HERE](ADD_YOUR_STREAMLIT_URL)

  **GitHub Repository:** [NCRAirLens](ADD_YOUR_GITHUB_REPOSITORY_URL)

</p>

---

## Project Overview

Air pollution is a significant environmental challenge in Delhi. Understanding its patterns requires analyzing historical pollution measurements across different periods and monitoring locations.

NCRAirLens transforms raw air quality observations into meaningful analytical insights through data cleaning, exploratory data analysis, statistical techniques, and interactive visualizations.

The platform focuses on two major particulate matter indicators:

- **PM2.5:** Fine particulate matter with a diameter of 2.5 micrometres or less.
- **PM10:** Particulate matter with a diameter of 10 micrometres or less.

The dashboard enables users to explore how these pollutants vary across months, seasons, weekdays, and monitoring stations.

## Key Features

### 1. Interactive Overview
- Key air pollution statistics.
- Overall PM2.5 and PM10 summaries.
- Historical data coverage.
- Important analytical indicators.

### 2. Time and Seasonal Analysis
- Monthly pollution trends.
- Seasonal pollution comparisons.
- Weekday-based pollution analysis.
- Historical pattern exploration.

### 3. Monitoring Station Comparison
- Comparison of pollution levels across monitoring stations.
- Top 10 stations based on PM2.5 and PM10 averages.
- Station-level data exploration.
- Monitoring coverage analysis.

### 4. Data Explorer
- Interactive dataset filtering.
- Historical record exploration.
- Paginated data tables.
- Filtered data export in CSV format.

### 5. Data Quality Assessment
- Duplicate record checks.
- Invalid measurement identification.
- Missing-value analysis.
- Monitoring coverage assessment.
- Identification of incomplete historical periods.

---

## Dataset Information

The project uses historical air quality measurements obtained through the **XKDR Forum Air Quality API**, using CPCB CAAQM monitoring data.

| Dataset Attribute | Details |
|---|---|
| Geographic Coverage | Delhi, India |
| Monitoring Stations | 39 |
| Data Source | CPCB CAAQM |
| API Provider | XKDR Forum |
| Historical Coverage | January 2017 - September 2025 |
| Raw Records | 198,758 |
| Cleaned Records | 198,743 |
| PM2.5 Observations | 101,738 |
| PM10 Observations | 97,005 |
| Primary Variables | PM2.5 and PM10 |

**Note:** The available dataset ends on 1 September 2025. September 2025 is therefore only partially represented. The dataset should not be interpreted as complete through December 2025.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Data Manipulation | Pandas, NumPy |
| Data Visualization | Plotly, Matplotlib, Seaborn |
| Dashboard Development | Streamlit |
| API Integration | Python Requests |
| Development Environment | VS Code |
| Version Control | Git and GitHub |
| Deployment | Streamlit Community Cloud |

---

## Project Architecture

The project follows a structured data analytics workflow:

```text
              DATA SOURCE
                   |
                   v
          XKDR Forum Air Quality API
                   |
                   v
            RAW DATA COLLECTION
                   |
                   v
             DATA CLEANING
                   |
                   v
          DATA QUALITY VALIDATION
                   |
                   v
       EXPLORATORY DATA ANALYSIS
                   |
                   v
         STATISTICAL ANALYSIS
                   |
                   v
          DATA VISUALIZATION
                   |
                   v
           STREAMLIT DASHBOARD
                   |
                   v
          INTERACTIVE INSIGHTS
```

---

## Repository Structure

```text
Delhi_Air_Pollution_Analysis/
│
├── app.py
│
├── download_air_quality.py
├── clean_air_quality.py
├── inspect_data_quality.py
├── air_quality_analysis.py
├── generate_charts.py
│
├── data/
│   ├── raw/
│   │   ├── monthly/
│   │   ├── delhi_stations.csv
│   │   └── delhi_stations.json
│   │
│   └── processed/
│       └── delhi_air_quality_clean.csv
│
├── charts/
│   ├── monthly_data_coverage.png
│   ├── monthly_pollution_trend.png
│   ├── pollutant_correlation.png
│   ├── seasonal_pollution.png
│   ├── top_10_pm10_stations.png
│   ├── top_10_pm25_stations.png
│   └── weekday_pollution.png
│
├── reports/
│   ├── monthly_pollution_summary.csv
│   ├── seasonal_pollution_summary.csv
│   ├── weekday_pollution_summary.csv
│   └── station_pollution_summary.csv
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Installation and Local Setup

Follow these steps to run NCRAirLens on your local machine.

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Navigate to the Project Directory

```bash
cd Delhi_Air_Pollution_Analysis
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Dashboard

```bash
streamlit run app.py
```

The dashboard will be available at:

```text
http://localhost:8501
```

---

## Analytical Findings

The exploratory data analysis revealed several patterns in the available historical dataset.

### 1. Seasonal Variation

The observed seasonal averages indicate substantial differences in particulate matter concentrations.

| Season | Average PM2.5 | Average PM10 |
|---|---:|---:|
| Winter | 168.40 | 282.56 |
| Post-Monsoon | 166.23 | 300.32 |
| Summer | 79.20 | 207.07 |
| Monsoon | 42.72 | 116.77 |

Winter and post-monsoon periods show higher average particulate matter concentrations, while monsoon observations show considerably lower averages.

### 2. Monitoring Station Comparison

Some stations with higher observed average pollution levels include:

- Anand Vihar
- Jahangirpuri
- Bawana
- Mundka
- Wazirpur

These rankings are based on the available historical observations and should not be interpreted as permanent rankings.

### 3. PM2.5 and PM10 Relationship

The calculated correlation between PM2.5 and PM10 is approximately **0.86**, indicating a strong positive statistical association in paired observations.

Correlation does not establish causation.

### 4. Weekday Variation

Average pollution levels across weekdays were relatively close in the analyzed dataset. The analysis does not establish a substantial weekday effect.

---

## Data Cleaning and Processing

The raw dataset was processed before being used for analysis.

Major data preparation steps included:

1. Loading and inspecting raw measurements.
2. Checking for duplicate records.
3. Identifying missing and invalid observations.
4. Validating reported mean values against minimum and maximum measurements.
5. Assessing monitoring coverage.
6. Creating a cleaned dataset.
7. Transforming pollutant records into an analysis-ready format.
8. Extracting date-related attributes such as year, month, weekday, and season.

A total of 15 invalid measurement records were excluded from the cleaned dataset. The original raw dataset was retained for reference.

High pollution readings were not automatically removed simply because they were unusually high.

---

## Important Limitations

- The analysis covers Delhi monitoring stations rather than the entire NCR region.
- Historical coverage ends on 1 September 2025.
- Monitoring station availability and observation coverage vary over time.
- Missing observations may affect monthly and seasonal comparisons.
- Seasonal averages describe the available observations and are not necessarily equally weighted across stations or dates.
- PM2.5 and PM10 concentrations are analyzed separately from AQI.
- The dataset does not provide a direct AQI variable.
- Correlation results indicate statistical association, not causation.

These limitations should be considered when interpreting the dashboard.

---

## Future Enhancements

Potential future improvements include:

- Integration of regularly updated air quality data.
- Expansion to additional NCR monitoring stations.
- Interactive geographical pollution mapping.
- Advanced time-series forecasting.
- Machine learning-based pollution prediction.
- Automated data quality monitoring.
- Comparative analysis across multiple Indian cities.
- Downloadable analytical reports.

---

## Project Objective

The primary objective of NCRAirLens is to demonstrate how data analytics can transform historical environmental observations into understandable insights.

By combining Python-based data processing, statistical analysis, and interactive visualization, the project provides an accessible way to explore Delhi's historical air pollution patterns.

---

## Author

**Shreyansh Jain**

BCA Student  
Maharaja Agrasen Institute of Management Studies (MAIMS), Delhi

**Areas of Interest:**
- Data Analytics
- Python Programming
- Artificial Intelligence
- Software Development

---

## Acknowledgements

- Central Pollution Control Board (CPCB) - air quality monitoring data.
- XKDR Forum - API access to air quality measurements.
- Streamlit - interactive dashboard framework.
- Python open-source ecosystem - data analysis and visualization tools.

---

<p align="center">

  **NCRAirLens**

  *See the Air. Understand the Data.*

  Built with Python, Data Analytics and Streamlit.

</p>