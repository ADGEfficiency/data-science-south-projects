FROM python:3.10.11
WORKDIR /src
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN mkdir -p /data
CMD ["python", "/src/main.py"]
