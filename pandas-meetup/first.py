"""
https://github.com/ADGEfficiency/data-science-south-projects

pip install pandas fastparquet
"""

import pathlib

import pandas as pd

if not pathlib.Path("raw.parquet").exists():
    raw = pd.read_csv(
        "https://www.emi.ea.govt.nz/Wholesale/Datasets/Generation/Generation_MD/202406_Generation_MD.csv"
    )
    raw.to_parquet("raw.parquet")
else:
    raw = pd.read_parquet("raw.parquet")

raw.iloc[0, 0]
raw.loc[0, "POC_Code"]
raw["POC_Code"]

data = raw.copy()

# datetime conversion & attribute access
data["year"] = pd.to_datetime(data["Trading_Date"]).dt.year
data["month"] = pd.to_datetime(data["Trading_Date"]).dt.month

data["Trading_Date"] = pd.to_datetime(data["Trading_Date"])
for col in ["year", "day"]:
    data[col] = getattr(data["Trading_Date"].dt, col)

# groupby
data[["TP1", "TP2", "day"]].groupby("day").agg(["sum", "mean"])

grp = (
    data[["TP1", "TP2", "Fuel_Code", "day"]]
    .groupby(["day", "Fuel_Code"])
    .agg(["sum", "mean"])
)
grp.columns = ["_".join(col).strip() for col in grp.columns.values]

# one way to plot - pd.Dataframe.plot
ax = grp["TP1_sum"].plot(kind="hist")
ax.get_figure().savefig("temp.png")

# second way to plot
import matplotlib.pyplot as plt

fig, axes = plt.subplots(ncols=2)
grp["TP1_sum"].plot(kind="hist", ax=axes[0])
grp["TP2_sum"].plot(kind="bar", ax=axes[1])
fig.savefig("temp2.png")

# three apis
import matplotlib.pyplot as plt

plt.plot(x=[1, 2, 3], y=[4, 5, 6])

fig, axes = plt.subplots(ncols=2)

pd.DataFrame.plot

# filtering
poc = "GLN0332"
mask = data["POC_Code"] == poc
data[mask]

# null values
data[data["TP50"].isna()]
