FROM python:3.12.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=UTC

WORKDIR /app

COPY pyproject.toml README.md ./
COPY xauusd ./xauusd
RUN python -m pip install --no-cache-dir . \
    && groupadd --system xauusd \
    && useradd --system --gid xauusd --home-dir /app xauusd \
    && mkdir -p /app/data /app/reports /app/logs \
    && chown -R xauusd:xauusd /app

USER xauusd
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=3)"
CMD ["python", "-m", "uvicorn", "xauusd.dashboard:app", "--host", "0.0.0.0", "--port", "8080"]
