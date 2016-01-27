FROM python:2

ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip

RUN mkdir /app
WORKDIR /app

ADD requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

ADD bootstrap3 /app/bootstrap3
ADD manage.py /app/
ADD jwter /app/jwter

VOLUME /jwter-media
