---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.14.4
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Putting the BP Historical Dataset into a SQLite Database

This notebook follows an exploration of the BP Historical dataset in [analyze-bp-historical-data/notebooks/explore.ipynb](https://github.com/ADGEfficiency/analyze-bp-historical-data/blob/main/notebooks/explore.ipynb).

## Options for Interacting with SQLite

There are a number of ways to interact with SQLite in Python:

1. the `sqlite3` module from the Python standard library,
2. through the `sqlalchemy` Python module (third party),
3. through `pandas` and a little bit of `sqlalchemy`.

We will use the third way with `pandas`.

## Create SQLite Table with `pandas`

First let's load our raw data into a `pd.DataFrame`:

```python
import pandas as pd

raw = pd.read_csv("https://raw.githubusercontent.com/ADGEfficiency/analyze-bp-historical-data/main/data/bp-stats-review-2022-consolidated-dataset-narrow-format.csv")
raw.shape
```

Now we have our data, we need to next create a connection to our database using `sqlalchemy.create_engine`:

```python
from sqlalchemy import create_engine

connection = create_engine('sqlite:///./data/db.sqlite', echo=True)
```

Finally, we can bring `pandas` and `sqlalchemy` together by using the connection in `pd.DataFrame.to_sql`:

```python
raw.to_sql('raw', if_exists='replace', con=connection)
```

We use `if_exists='replace'` to completely replace the table each time we run `.to_sql`.

And that's it!  Pretty simple if you know the simple ways ^^


## Read Entire SQLite Table into `pandas`

Now we have a SQLite database - it's a file in the `data` folder:

```python
!ls ./data
```

We can read data from the database back into `pandas` by using `pd.read_sql`:

```python
out = pd.read_sql("SELECT * FROM raw", con=connection)
print(out.shape)
out.head(3)
```

We use a SQL statement `SELECT * FROM raw`.  This statement selects the entire `raw` table.

## Filter SQLite Table

We can also do analytics on the database directly.

Previously in [analyze-bp-historical-data/notebooks/explore.ipynb](https://github.com/ADGEfficiency/analyze-bp-historical-data/blob/main/notebooks/explore.ipynb) we manipulated data using pandas.

It's also possible to do analytics with the database.  When your database is a remote server (say Postgres), pushing computation back into the database can reduce the load on your local machine.  

Below we use a `SELECT` statement with a `WHERE` clause to get only wind data from New Zealand:

```python
out = pd.read_sql("SELECT * FROM raw WHERE Country = 'New Zealand' AND Var like '%wind%'", con=connection)
out.head(3)
```

Compare how short and sweet this is - SQL at it's best.

## Summary

Key takeaways:

- we can interact with SQLite from Python in a few ways,
- `pd.to_sql` is a simple way to create a `SQLite` table from a CSV,
- we can select all data using a `SELECT *` SQL query,
- we can filter data using a `SELECT * WHERE` SQL query.
