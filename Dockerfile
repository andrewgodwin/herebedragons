ARG IMAGE_HOST=python
ARG IMAGE_LABEL=3.11-slim-bullseye

FROM ${IMAGE_HOST}:${IMAGE_LABEL}

ENV PYTHONUNBUFFERED=1

COPY requirements.txt requirements.txt

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
        libxslt1.1 \
        nginx \
        busybox \
        netcat \
        gcc \
        libc6-dev \
        libpq-dev \
        libxslt1-dev \
        zlib1g-dev \
        postgresql-client \
        binutils \
        libproj-dev \
        gdal-bin \
    && python3 -m pip install --no-cache-dir --upgrade -r requirements.txt \
    && apt-get purge -y --auto-remove \
        gcc \
        libc6-dev \
        libpq-dev \
        libxslt1-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /cache

COPY . /hbd
WORKDIR /hbd

RUN python3 manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "herebedragons.wsgi:application", "-b", "0.0.0.0:8000"]
