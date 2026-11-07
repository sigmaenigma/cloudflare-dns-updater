FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py app_manual.py ./

# Run as an unprivileged user; the app needs no write access to the filesystem.
RUN useradd --system --no-create-home --shell /usr/sbin/nologin appuser
USER appuser

CMD ["python", "app.py"]
