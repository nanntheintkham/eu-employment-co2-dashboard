"""One-off cleaning script: raw Eurostat / OWID downloads -> lean CSVs used by the app.
Run once after re-downloading the raw files (see README for source URLs).
"""
import pandas as pd

GEO_MAP = {
    "AT": ("Austria", "AUT"), "BA": ("Bosnia and Herzegovina", "BIH"), "BE": ("Belgium", "BEL"),
    "BG": ("Bulgaria", "BGR"), "CH": ("Switzerland", "CHE"), "CY": ("Cyprus", "CYP"),
    "CZ": ("Czechia", "CZE"), "DE": ("Germany", "DEU"), "DK": ("Denmark", "DNK"),
    "EE": ("Estonia", "EST"), "EL": ("Greece", "GRC"), "ES": ("Spain", "ESP"),
    "FI": ("Finland", "FIN"), "FR": ("France", "FRA"), "HR": ("Croatia", "HRV"),
    "HU": ("Hungary", "HUN"), "IE": ("Ireland", "IRL"), "IS": ("Iceland", "ISL"),
    "IT": ("Italy", "ITA"), "LT": ("Lithuania", "LTU"), "LU": ("Luxembourg", "LUX"),
    "LV": ("Latvia", "LVA"), "ME": ("Montenegro", "MNE"), "MK": ("North Macedonia", "MKD"),
    "MT": ("Malta", "MLT"), "NL": ("Netherlands", "NLD"), "NO": ("Norway", "NOR"),
    "PL": ("Poland", "POL"), "PT": ("Portugal", "PRT"), "RO": ("Romania", "ROU"),
    "RS": ("Serbia", "SRB"), "SE": ("Sweden", "SWE"), "SI": ("Slovenia", "SVN"),
    "SK": ("Slovakia", "SVK"), "TR": ("Turkey", "TUR"),
}
EU27 = {"AT","BE","BG","CY","CZ","DE","DK","EE","EL","ES","FI","FR","HR","HU","IE","IT",
        "LT","LU","LV","MT","NL","PL","PT","RO","SE","SI","SK"}

# ---------- Eurostat unemployment ----------
raw = pd.read_csv("eurostat_unemployment_raw.csv")
raw = raw[(raw["unit"] == "PC_ACT") & (raw["age"].isin(["Y15-74", "Y15-24"]))]
raw = raw[raw["geo"].isin(GEO_MAP.keys())]
raw = raw.rename(columns={"TIME_PERIOD": "year", "OBS_VALUE": "unemployment_rate", "sex": "sex_code"})
sex_labels = {"T": "Total", "M": "Male", "F": "Female"}
age_labels = {"Y15-74": "Overall (15-74)", "Y15-24": "Youth (15-24)"}
raw["sex"] = raw["sex_code"].map(sex_labels)
raw["age_group"] = raw["age"].map(age_labels)
raw["country"] = raw["geo"].map(lambda g: GEO_MAP[g][0])
raw["iso3"] = raw["geo"].map(lambda g: GEO_MAP[g][1])
raw["is_eu27"] = raw["geo"].isin(EU27)

clean = raw[["country", "iso3", "geo", "is_eu27", "year", "sex", "age_group", "unemployment_rate"]].dropna()
clean = clean.sort_values(["country", "year"])
clean.to_csv("eurostat_unemployment_clean.csv", index=False)
print("Eurostat clean rows:", len(clean), "| years:", clean.year.min(), "-", clean.year.max())

# ---------- OWID CO2 ----------
co2 = pd.read_csv("owid_co2_raw.csv")
keep_cols = [
    "country", "year", "iso_code", "population", "gdp",
    "co2", "co2_per_capita", "co2_growth_prct", "cumulative_co2",
    "coal_co2", "oil_co2", "gas_co2",
    "share_global_co2", "primary_energy_consumption", "energy_per_capita",
    "temperature_change_from_co2",
]
co2 = co2[keep_cols]
co2 = co2[co2["year"] >= 1900]
# drop non-country aggregate rows (World, continents, income groups) which have no iso_code
co2 = co2[co2["iso_code"].notna() & (co2["iso_code"].str.len() == 3)]
co2.to_csv("owid_co2_clean.csv", index=False)
print("OWID clean rows:", len(co2), "| years:", co2.year.min(), "-", co2.year.max())
