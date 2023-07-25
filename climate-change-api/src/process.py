import pathlib
import sqlite3
import time
import datetime

import pandas as pd


if __name__ == "__main__":
    pkg = {}
    for dataset in ["co2", "temperature"]:
        files = [
            p
            for p in pathlib.Path(f"data/{dataset}/processed").iterdir()
            if p.suffix == ".parquet"
        ]
        files = sorted(files, key=lambda x: float(x.stem))
        latest = files[-1]
        pkg[dataset] = pd.read_parquet(latest)

    data = pd.merge(
        *pkg.values(), suffixes=[f":{key}" for key in pkg.keys()], on="date"
    )

    with sqlite3.connect("data/database.db") as conn:
        cur = conn.cursor()
        for index, row in data.iterrows():
            query = """
            INSERT OR IGNORE INTO api (co2_ppm, date, temperature_c)
            VALUES (?, ?, ?);
            """
            cur.execute(
                query, (row["co2_ppm"], row["date"].date(), row["temperature_c"])
            )

        cur.execute("SELECT COUNT(*) FROM api")
        count = cur.fetchone()[0]
        print(f"The number of rows in the 'api' table is {count}")

        query = """
        INSERT INTO log (run_time, data_length)
        VALUES (?, ?);
        """
        run_time = datetime.datetime.now().isoformat()
        cur.execute(query, (run_time, count))

    print("sleeping to let litestream replication catch up")
    time.sleep(2)
