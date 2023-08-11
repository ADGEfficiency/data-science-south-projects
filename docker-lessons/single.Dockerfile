FROM python:3.8
RUN apt-get update && apt-get upgrade -y && apt-get clean
RUN apt-get install cron -y
WORKDIR /src
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN (crontab -l ; echo "0 * * * * python /src/main.py") | crontab
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
