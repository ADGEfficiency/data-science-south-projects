import collections
import datetime
import sqlite3

import fastapi
import pydantic

app = fastapi.FastAPI()


class Request(pydantic.BaseModel):
    start: datetime.date = pydantic.Field(datetime.date(year=2021, month=1, day=1), description="Start date (YYYY-MM-DD).")
    n: int = pydantic.Field(12, description="Number of months to return.")


class Response(pydantic.BaseModel):
    date: list[datetime.date] = pydantic.Field(
        ...,
        title="date",
        description="ISO8061 date YYYY-MM-DD."
    )
    temperature: list[float] = pydantic.Field(
        ...,
        title="temperature",
        description="Combined Land-Surface Air and Sea-Surface Water Temperature Anomalies (Land-Ocean Temperature Index, L-OTI). Temperature anomalies are the deviations from the corresponding 1951-1980 means. Monthly global average. Source: https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv. Reference: https://data.giss.nasa.gov/gistemp/",
    )
    co2: list[float] = pydantic.Field(
        ...,
        title="co2",
        description="Monthly mean carbon dioxide concentration measured at Mauna Loa Observatory, Hawaii. The carbon dioxide data on Mauna Loa constitute the longest record of direct measurements of CO2 in the atmosphere. Source: https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_daily_mlo.txt. Reference: https://gml.noaa.gov/ccgg/trends/data.html",
    )


@app.get("/api", response_model=Response)
async def get_climate_data(
    start: datetime.date = fastapi.Query(
        datetime.date(year=2021, month=1, day=1), description="Start date (YYYY-MM-DD)."
    ),
    n: int = fastapi.Query(
        12, description="Number of months after start date to return."
    ),
):
    request_model = Request(start=start, n=n)
    with sqlite3.connect("data/database.db") as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT date, temperature_c, co2_ppm FROM api WHERE date >= ? ORDER BY date ASC LIMIT ?",
            (request_model.start, request_model.n),
        )
        data = cur.fetchall()

    pkg = collections.defaultdict(list)
    for row in data:
        pkg["date"].append(row[0])
        pkg["temperature"].append(row[1])
        pkg["co2"].append(row[2])
    return pkg


@app.get("/")
async def root():
    return {
        "description": """Welcome to the Climate Data API. /api to retrieve monthly CO2 atmospheric concentration, measured in parts per million (PPM) and global temperatures, measured in in degrees Celcius (C). /docs for API documentation.""",
        "endpoints": [
            {
                "endpoint": "/api",
                "method": "GET",
                "request": Request.schema(),
                "response": Response.schema(),
            }
        ],
    }
