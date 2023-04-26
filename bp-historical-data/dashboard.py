import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

connection = create_engine(f"sqlite:///data/db.sqlite", echo=True)


def download_raw_data():
    raw = pd.read_csv(
        "https://raw.githubusercontent.com/ADGEfficiency/analyze-bp-historical-data/main/data/bp-stats-review-2022-consolidated-dataset-narrow-format.csv"
    )
    raw.to_sql("raw", if_exists="replace", con=connection)


def read_from_database():
    return pd.read_sql("SELECT * FROM raw", con=connection)


if __name__ == "__main__":
    download_raw_data()
    data = read_from_database()

    print(data[["Country", "Year", "Var", "Value"]].sample(3))

    st.header("BP Historical Energy Data")
    st.text("Analysis of the 2022 BP Statistical Review of World Energy dataset.")
    st.header("Raw Data")
    st.dataframe(data)

    st.header("Country Selector")

    #  get unique countries with sql
    countries = pd.read_sql(
        "SELECT DISTINCT Country FROM raw ORDER BY Country ASC", con=connection
    )
    #  get unique countries with pandas
    countries = sorted(data["Country"].unique().tolist())
    country_selector = st.sidebar.selectbox("Country:", countries, index=countries.index('United Kingdom'))

    #  filter on country with sql
    country_data = pd.read_sql(
        "SELECT * FROM raw WHERE Country = :country",
        params={"country": country_selector},
        con=connection,
    )

    #  filter on country with pandas
    mask = data["Country"] == country_selector
    country_data = data[mask]

    #  display the dataframe in the dashboard
    st.dataframe(country_data)

    st.header("Variable Chart")

    #  filter on country with sql
    country_data = pd.read_sql(
        "SELECT * FROM raw WHERE Country = :country",
        params={"country": country_selector},
        con=connection,
    )

    # unique variables with pandas
    variables = country_data["Var"].unique().tolist()
    variable_selector = st.sidebar.selectbox("Variable:", variables, index=variables.index("wind_twh"))

    #  filter with pandas
    single_var = country_data[country_data["Var"] == variable_selector]
    st.dataframe(single_var[["Country", "Region", "Year", "Var", "Value"]])

    #  matplotlib plot
    f, axes = plt.subplots(figsize=(15, 5))
    single_var.plot(x="Year", y="Value", ax=axes, label=variable_selector)
    axes.set_xlabel("Year")
    axes.set_ylabel(variable_selector)
    st.pyplot(f)
