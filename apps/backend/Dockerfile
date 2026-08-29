FROM python:3.14-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-por \
        tesseract-ocr-eng \
        tesseract-ocr-osd \
    && rm -rf /var/lib/apt/lists/*

COPY apps/backend/requirements.txt .
COPY apps/backend/pytest.ini .
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/backend/app ./app
COPY apps/backend/tests ./tests
COPY database ./database

EXPOSE 8000

CMD ["uvicorn", "app.liaBackendApplication:application", "--host", "0.0.0.0", "--port", "8000"]
