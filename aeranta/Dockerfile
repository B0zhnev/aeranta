FROM python:3.12-slim
RUN groupadd -r groupdjango && useradd -r -g groupdjango userdj

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    proj-bin \
    proj-data \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
    
RUN pip install --upgrade pip
WORKDIR /app/www/aeranta
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

USER userdj
