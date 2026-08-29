FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
COPY pytest.ini .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY tests ./tests

EXPOSE 8000

CMD ["uvicorn", "app.liaControlApiApplication:application", "--host", "0.0.0.0", "--port", "8000"]
