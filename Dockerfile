FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

RUN python -c "from pathlib import Path; p=Path('requirements.txt'); b=p.read_bytes(); \
import sys; \
is_utf16 = b[:2] in (b'\xff\xfe', b'\xfe\xff'); \
txt = b.decode('utf-16') if is_utf16 else b.decode('utf-8', errors='ignore'); \
Path('requirements.utf8.txt').write_text(txt, encoding='utf-8');" \
 && pip install --upgrade pip \
 && pip install -r requirements.utf8.txt

COPY . /app

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
