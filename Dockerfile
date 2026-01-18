# Author: eric vanoverbeke
# Date: 2026-01-18

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_DATA_DIR=/app/data

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY web ./web
COPY seed ./seed
COPY docs ./docs
COPY LICENSE README.md ./

RUN mkdir -p /app/data

EXPOSE 9999

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9999"]
