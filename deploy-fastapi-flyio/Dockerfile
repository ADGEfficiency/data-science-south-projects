FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
WORKDIR /app
COPY ./app.py .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
