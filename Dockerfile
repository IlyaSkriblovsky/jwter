FROM python:2-slim

ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip

RUN mkdir /app
WORKDIR /app

ADD requirements.txt /app
RUN build_deps="build-essential" \
 && apt-get update \
 && apt-get install -y $build_deps \
 && pip install --no-cache-dir -r requirements.txt \
 && apt-get purge -y $build_deps \
 && rm -rf /var/lib/apt/lists/*

ADD bootstrap3 /app/bootstrap3
ADD manage.py /app/
ADD jwter /app/jwter

VOLUME /jwter-media
