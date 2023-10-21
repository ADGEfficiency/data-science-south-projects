FROM --platform=linux/amd64 python:3.10
WORKDIR /app
RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev jq
RUN pip install --no-cache-dir pandas requests fastparquet boto3 pyarrow awscli
RUN mkdir -p data
RUN wget https://github.com/benbjohnson/litestream/releases/download/v0.3.9/litestream-v0.3.9-linux-amd64.deb
RUN dpkg -i litestream-v0.3.9-linux-amd64.deb
COPY src/download.py src/process.py ./src/
COPY pipeline.sh schema.sql ./
CMD ["bash", "pipeline.sh"]
