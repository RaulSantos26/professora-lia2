FROM pytorch/pytorch:2.12.1-cuda13.0-cudnn9-runtime

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/cache/huggingface \
    TRANSFORMERS_CACHE=/cache/huggingface \
    PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

RUN apt-get update \
    && apt-get install -y --no-install-recommends fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --break-system-packages -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.imageServiceApplication:application", "--host", "0.0.0.0", "--port", "8000"]
