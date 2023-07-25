FROM --platform=linux/amd64 python:3.10
WORKDIR /app
COPY ./src/app.py /app/src/
COPY ./restore-db.sh ./
RUN pip install --no-cache-dir fastapi uvicorn awscli
RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev jq
RUN wget https://github.com/benbjohnson/litestream/releases/download/v0.3.9/litestream-v0.3.9-linux-amd64.deb
RUN dpkg -i litestream-v0.3.9-linux-amd64.deb
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8080"]
