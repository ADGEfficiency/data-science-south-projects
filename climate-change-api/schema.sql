CREATE TABLE IF NOT EXISTS api (
    co2_ppm REAL,
    date DATE UNIQUE,
    temperature_c REAL
);

CREATE TABLE IF NOT EXISTS log (
    run_time TEXT UNIQUE,
    data_length INTEGER
);
