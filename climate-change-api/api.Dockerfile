FROM python:3.10
WORKDIR /app
COPY ./src/app.py /app/src/
RUN pip install --no-cache-dir fastapi uvicorn
RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0"]
