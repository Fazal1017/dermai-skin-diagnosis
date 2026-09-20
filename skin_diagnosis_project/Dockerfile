FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies required for some Python packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       gcc \
       libjpeg-dev \
       zlib1g-dev \
       curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy project files
COPY . /app

RUN chmod +x /app/entrypoint.sh || true

ENV PATH="/root/.local/bin:${PATH}"

EXPOSE 8000

CMD ["sh", "/app/entrypoint.sh"]
