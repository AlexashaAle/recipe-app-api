FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN  apk add --no-cache --virtual .build-deps gcc libffi-dev musl-dev && pip install -r requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN #adduser -D user
USER user

