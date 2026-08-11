"""
EU Labour Market & Global CO2 Emissions Dashboard
Portfolio project — two public datasets, one Streamlit app.

Data sources:
  1. Eurostat  - Unemployment rate, annual (une_rt_a)   https://ec.europa.eu/eurostat
  2. Our World in Data - CO2 and Greenhouse Gas Emissions  https://github.com/owid/co2-data
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------- palette --
# Fixed-order categorical palette (validated for CVD-safe adjacent contrast).
CATEGORICAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
               "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
SEQUENTIAL_BLUE = ["#cde2fb", "#9ec5f4", "#5598e7", "#2a78d6", "#184f95", "#0d366b"]
MUTED = "#898781"
GRID = "#e1e0d9"

st.set_page_config(
    page_title="EU Labour Market & Global CO2 Emissions",
    page_icon="📊",
    layout="wide",
)


def style_fig(fig, y_title=None, x_title=None):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#52514e", family="system-ui, -apple-system, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=10, r=10, t=40, b=10),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=False, linecolor=GRID, title=x_title)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, title=y_title)
    return fig


@st.cache_data
def load_unemployment():
    return pd.read_csv("data/eurostat_unemployment_clean.csv")


@st.cache_data
def load_co2():
    return pd.read_csv("data/owid_co2_clean.csv")


unemp = load_unemployment()
co2 = load_co2()

st.title("📊 EU Labour Market & Global CO2 Emissions")
st.caption(
    "Two public datasets, one dashboard — built as a portfolio piece. "
    "Sources: [Eurostat](https://ec.europa.eu/eurostat) unemployment statistics "
    "and [Our World in Data](https://github.com/owid/co2-data) CO2 & GHG emissions."
)

tab1, tab2 = st.tabs(["🇪🇺 EU Labour Market", "🌍 Global CO2 Emissions"])

# =============================================================== TAB 1 =====
with tab1:
    st.subheader("Unemployment across Europe, 2003–2025")

    col_a, col_b, col_c = st.columns([2, 1, 1])
    with col_a:
        default_countries = ["Germany", "France", "Spain", "Italy", "Poland", "Sweden"]
        countries = st.multiselect(
            "Countries", sorted(unemp["country"].unique()),
            default=default_countries, max_selections=8, key="u_countries",
        )
    with col_b:
        age_group = st.radio("Age group", ["Overall (15-74)", "Youth (15-24)"], key="u_age")
    with col_c:
        sex = st.radio("Sex", ["Total", "Male", "Female"], key="u_sex")

    yr_min, yr_max = int(unemp["year"].min()), int(unemp["year"].max())
    year_range = st.slider("Year range", yr_min, yr_max, (2010, yr_max), key="u_years")

    filtered = unemp[
        (unemp["country"].isin(countries))
        & (unemp["age_group"] == age_group)
        & (unemp["sex"] == sex)
        & (unemp["year"].between(*year_range))
    ]

    if filtered.empty or not countries:
        st.info("Select at least one country to see the trend.")
    else:
        fig = px.line(
            filtered.sort_values("year"), x="year", y="unemployment_rate", color="country",
            color_discrete_sequence=CATEGORICAL, markers=True,
            labels={"unemployment_rate": "Unemployment rate (%)", "year": "Year", "country": "Country"},
        )
        fig.update_traces(line=dict(width=2))
        st.plotly_chart(style_fig(fig, y_title="Unemployment rate (%)"), use_container_width=True)

    st.divider()
    map_col, bar_col = st.columns(2)

    with map_col:
        st.markdown("**EU-27 map — most recent year**")
        latest_year = int(unemp[unemp["is_eu27"]]["year"].max())
        eu_latest = unemp[
            (unemp["is_eu27"]) & (unemp["year"] == latest_year)
            & (unemp["age_group"] == "Overall (15-74)") & (unemp["sex"] == "Total")
        ]
        fig_map = px.choropleth(
            eu_latest, locations="iso3", color="unemployment_rate",
            scope="europe", color_continuous_scale=SEQUENTIAL_BLUE,
            hover_name="country", labels={"unemployment_rate": "Unemployment (%)"},
        )
        fig_map.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=10, b=0),
            coloraxis_colorbar=dict(title="%"),
        )
        st.plotly_chart(fig_map, use_container_width=True)
        st.caption(f"Data year: {latest_year}")

    with bar_col:
        st.markdown("**Youth vs. overall unemployment — most recent year**")
        comp = unemp[
            (unemp["country"].isin(countries)) & (unemp["sex"] == "Total")
            & (unemp["year"] == unemp[unemp["country"].isin(countries)]["year"].max())
        ]
        if not comp.empty:
            fig_bar = px.bar(
                comp, x="country", y="unemployment_rate", color="age_group",
                barmode="group", color_discrete_sequence=CATEGORICAL,
                labels={"unemployment_rate": "Unemployment rate (%)", "country": "", "age_group": ""},
            )
            st.plotly_chart(style_fig(fig_bar, y_title="Unemployment rate (%)"), use_container_width=True)

    with st.expander("View underlying data (Eurostat)"):
        st.dataframe(filtered, use_container_width=True)

# =============================================================== TAB 2 =====
with tab2:
    st.subheader("CO2 Emissions, 1900–2024")

    col_a, col_b = st.columns([2, 1])
    with col_a:
        default_geo = ["United States", "China", "India", "European Union (27)", "United Kingdom"]
        avail_geo = sorted(co2["country"].unique())
        default_geo = [g for g in default_geo if g in avail_geo] or list(avail_geo[:5])
        geos = st.multiselect(
            "Countries / regions", avail_geo, default=default_geo,
            max_selections=8, key="c_geo",
        )
    with col_b:
        metric = st.radio("Metric", ["Total CO2 (Mt)", "CO2 per capita (t)"], key="c_metric")

    co2_yr_min, co2_yr_max = int(co2["year"].min()), int(co2["year"].max())
    co2_year_range = st.slider(
        "Year range", co2_yr_min, co2_yr_max, (1950, co2_yr_max), key="c_years"
    )

    metric_col = "co2" if metric.startswith("Total") else "co2_per_capita"
    filtered_co2 = co2[
        (co2["country"].isin(geos)) & (co2["year"].between(*co2_year_range))
    ].dropna(subset=[metric_col])

    if filtered_co2.empty or not geos:
        st.info("Select at least one country or region to see the trend.")
    else:
        fig2 = px.line(
            filtered_co2.sort_values("year"), x="year", y=metric_col, color="country",
            color_discrete_sequence=CATEGORICAL,
            labels={metric_col: metric, "year": "Year", "country": "Country"},
        )
        fig2.update_traces(line=dict(width=2))
        st.plotly_chart(style_fig(fig2, y_title=metric), use_container_width=True)

    st.divider()
    map_col2, mix_col2 = st.columns(2)

    with map_col2:
        st.markdown("**World map — CO2 per capita, most recent year**")
        latest_co2_year = int(co2["year"].max())
        world_latest = co2[
            (co2["year"] == latest_co2_year) & (co2["co2_per_capita"].notna())
        ]
        fig_map2 = px.choropleth(
            world_latest, locations="iso_code", color="co2_per_capita",
            color_continuous_scale=SEQUENTIAL_BLUE,
            hover_name="country", labels={"co2_per_capita": "t / person"},
        )
        fig_map2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=10, b=0),
            coloraxis_colorbar=dict(title="t/person"),
        )
        st.plotly_chart(fig_map2, use_container_width=True)
        st.caption(f"Data year: {latest_co2_year}")

    with mix_col2:
        st.markdown("**Fuel-source mix over time**")
        mix_country = st.selectbox("Country / region", geos if geos else avail_geo, key="c_mix_country")
        mix_data = co2[
            (co2["country"] == mix_country) & (co2["year"].between(*co2_year_range))
        ][["year", "coal_co2", "oil_co2", "gas_co2"]].melt(
            "year", var_name="source", value_name="emissions"
        )
        mix_data["source"] = mix_data["source"].map(
            {"coal_co2": "Coal", "oil_co2": "Oil", "gas_co2": "Gas"}
        )
        fig_mix = px.area(
            mix_data.dropna(), x="year", y="emissions", color="source",
            color_discrete_sequence=CATEGORICAL,
            labels={"emissions": "CO2 (Mt)", "year": "Year", "source": ""},
        )
        st.plotly_chart(style_fig(fig_mix, y_title="CO2 (Mt)"), use_container_width=True)

    with st.expander("View underlying data (Our World in Data)"):
        st.dataframe(filtered_co2, use_container_width=True)

st.divider()
st.caption(
    "Built with Streamlit + Plotly. Source code: see repository README for data "
    "refresh instructions. Not for investment or policy decisions — for portfolio "
    "demonstration purposes."
)
