import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split


def load_data():
    data = pd.read_csv("./earthquakes_NZ.csv")
    data["datetime"] = pd.to_datetime(data["origintime"], format="%Y-%m-%d%H:%M:%S.%f")
    data["year"] = data["datetime"].dt.year
    data["month"] = data["datetime"].dt.month
    data["day"] = data["datetime"].dt.day
    data.columns = [c.strip(" ") for c in data.columns]
    return data


def feature_engineering(data):
    days = (
        data["magnitude"]
        .groupby(
            [
                data["datetime"].dt.year,
                data["datetime"].dt.month,
                data["datetime"].dt.day,
            ]
        )
        .sum()
    )

    days = days.to_frame()
    for n in range(1, 11):
        days.loc[:, f"d-{n}"] = days["magnitude"].shift(n)

    days = days.dropna()
    assert days.isnull().sum().sum() == 0
    return days


def train_evaluate(data, mdl):
    tr, te = train_test_split(data, test_size=0.2, shuffle=False)

    tr_y = tr["magnitude"]
    tr_x = tr[[c for c in tr.columns if c.startswith("d-")]]
    assert "magnitude" not in tr_x.columns

    mdl.fit(tr_x, tr_y)

    tr_sc = mean_absolute_error(mdl.predict(tr_x), tr_y)

    te_y = te["magnitude"]
    te_x = te[[c for c in tr.columns if c.startswith("d-")]]
    assert "magnitude" not in tr_x.columns
    te_sc = mean_absolute_error(mdl.predict(te_x), te_y)
    return {
        "tr_sc": tr_sc,
        "te_sc": te_sc,
    }


def main():
    data = load_data()
    features = feature_engineering(data)
    mdl = DummyRegressor()
    naive_scores = train_evaluate(features, mdl)

    mdl = RandomForestRegressor()
    scores = train_evaluate(features, mdl)
    return naive_scores, scores


if __name__ == "__main__":
    print(main())
