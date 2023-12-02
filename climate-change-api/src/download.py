import io
import pathlib
import time
from datetime import datetime

import boto3
import pandas as pd
import requests


def get_bucket_name():
    session = boto3.Session(region_name="ap-southeast-2")
    cf = session.client("cloudformation")
    response = cf.describe_stacks(StackName="BucketStack")
    outputs = response["Stacks"][0]["Outputs"]
    for output in outputs:
        if output["OutputKey"] == "APIBucketName":
            return output["OutputValue"]


def write_s3_text(bucket, key, data):
    session = boto3.Session(region_name="ap-southeast-2")
    resource = session.resource("s3")
    resource.Object(bucket, key).put(Body=str(data))
    print(f"write_s3_text: {bucket, key}")


def write_s3_parquet(bucket, key, data):
    session = boto3.Session(region_name="ap-southeast-2")
    resource = session.resource("s3")
    f = io.BytesIO()
    data.to_parquet(f, engine="pyarrow", index=False)
    obj = resource.Object(bucket, key)
    obj.put(Body=f.getvalue())
    print(f"write_s3_parquet: {bucket, key}")


def save_data(raw, processed, dataset, download_id):
    raw_fi = pathlib.Path(f"data/{dataset}/raw/{download_id}.txt")
    raw_fi.parent.mkdir(parents=True, exist_ok=True)
    raw_fi.write_text(raw)

    processed_fi = pathlib.Path(f"data/{dataset}/processed/{download_id}.parquet")
    processed_fi.parent.mkdir(parents=True, exist_ok=True)
    processed.to_parquet(processed_fi)
    print(f"\nsave_data: raw={raw_fi} processed={processed_fi}")

    try:
        bucket = get_bucket_name()
        write_s3_text(bucket, f"{dataset}/raw/{download_id}.txt", raw)
        write_s3_parquet(
            bucket, f"{dataset}/processed/{download_id}.parquet", processed
        )

    except Exception as err:
        print(f"unable to write to s3 {err}")


def clean_float_data(value):
    try:
        return float(value)
    except ValueError:
        if value.startswith("-."):
            return float(value.replace("-.", "-0."))
        else:
            return None


def download_co2():
    uri = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_daily_mlo.txt"
    download_id = time.time()
    response = requests.get(uri)

    assert (
        response.status_code == 200
    ), f"Unable to fetch daily CO2 data, status code: {response.status_code}"

    data = io.StringIO(response.text)
    processed = pd.read_csv(data, comment="#", delim_whitespace=True, header=None)
    processed.columns = ["year", "month", "day", "decimal", "co2_ppm"]
    processed["date"] = pd.to_datetime(processed[["year", "month", "day"]])
    processed = processed.groupby([
        processed['date'].dt.year,
        processed['date'].dt.month
    ]).mean()
    processed['date'] = processed.index.map(lambda x: datetime(year=x[0], month=x[1], day=1))
    processed = processed.reset_index(drop=True)
    save_data(response.text, processed, "co2", download_id)


def download_temperature():
    uri = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
    response = requests.get(uri)
    assert (
        response.status_code == 200
    ), f"Unable to fetch monthly temperature data, status code: {response.status_code}"

    data = io.StringIO(response.text)
    processed = pd.read_csv(data, header=1)
    download_id = time.time()

    processed = pd.melt(
        processed,
        id_vars=["Year"],
        value_vars=[
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ],
        var_name="month",
        value_name="temperature_c",
    )

    # convert year and month to a datetime
    processed["date"] = processed.apply(
        lambda row: datetime.strptime(
            f"{int(row['Year'])}-{row['month']}-01", "%Y-%b-%d"
        ),
        axis=1,
    )

    processed = processed.drop(columns=["Year", "month"])
    processed = processed[["date", "temperature_c"]]
    processed["download_id"] = download_id

    processed["temperature_c"] = processed["temperature_c"].apply(clean_float_data)
    processed = processed.sort_values("date")
    processed = processed.dropna()
    save_data(response.text, processed, "temperature", download_id)


if __name__ == "__main__":
    download_co2()
    download_temperature()
