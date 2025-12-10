ARG PYTHON_VERSION

FROM python:${PYTHON_VERSION}-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

ENV PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

CMD ["python", "-m", "src.app.main"]
