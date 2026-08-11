# EU Labour Market & Global CO2 Emissions Dashboard

An interactive Streamlit dashboard built on two public datasets:

1. **[Eurostat](https://ec.europa.eu/eurostat)** — annual unemployment rate by
   country, age group, and sex (dataset `une_rt_a`), 2003–2025.
2. **[Our World in Data — CO2 and Greenhouse Gas Emissions](https://github.com/owid/co2-data)**
   — global CO2 emissions, per-capita figures, and fuel-source breakdown,
   1900–2024.

**Live demo:** _add your Streamlit Cloud URL here after deploying_

## What it shows

| Tab | Charts |
|---|---|
| 🇪🇺 EU Labour Market | Country-comparison trend line, EU-27 choropleth map, youth vs. overall unemployment bar chart |
| 🌍 Global CO2 Emissions | Country-comparison trend line (total or per-capita), world choropleth map, coal/oil/gas fuel-mix area chart |

Every chart has interactive filters (countries, year range, metric) and an
underlying-data table for transparency.

## Project structure

```
eu-employment-co2-dashboard/
├── app.py                  # Streamlit app (entry point)
├── requirements.txt
├── .streamlit/config.toml  # theme
└── data/
    ├── clean_data.py                    # raw -> clean transform script
    ├── eurostat_unemployment_clean.csv  # committed, used by the app
    └── owid_co2_clean.csv               # committed, used by the app
```

Raw downloads (`*_raw.csv`) are gitignored — re-fetch them with the commands
below if you want to refresh the data.

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Refreshing the data

```bash
cd data
curl -sL "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/une_rt_a/?format=SDMX-CSV&lang=en" -o eurostat_unemployment_raw.csv
curl -sL "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv" -o owid_co2_raw.csv
python3 clean_data.py
```

## Deploying to Streamlit Community Cloud

1. Push this folder to a public GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub.
3. Click **New app**, pick the repo/branch, and set the main file to `app.py`.
4. Deploy — Streamlit Cloud installs `requirements.txt` automatically.

## Tech stack

Python · pandas · Streamlit · Plotly

## License

Data is redistributed under its original sources' licenses (Eurostat: reuse
policy requires source attribution; OWID: CC BY 4.0). Code in this repo is
MIT-licensed — see [LICENSE](LICENSE).
