FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY app ./app

RUN pip install --no-cache-dir -e ".[api]"

CMD ["sh", "-c", "python -m uvicorn app.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
