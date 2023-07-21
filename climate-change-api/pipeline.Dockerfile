FROM python:3.10
WORKDIR /app
COPY src/download.py src/process.py ./src/
COPY pipeline.sh schema.sql ./
RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev
RUN pip install --no-cache-dir pandas requests fastparquet
RUN mkdir -p data
RUN sqlite3 data/database.db < schema.sql
CMD ["bash", "pipeline.sh"]
