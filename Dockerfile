FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \ 
    PYTHONPATH=/app

EXPOSE 8000

CMD ["sh", "-c", "python -m migrations.migrate && python -m migrations.seed && uvicorn app.main:app --host 0.0.0.0 --port 8000"]

