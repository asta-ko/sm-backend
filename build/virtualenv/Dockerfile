#FROM alpine:3.7
FROM python:3.6-alpine3.7

COPY python-libs.txt /tmp/

RUN apk --no-cache add  git openssh bash postgresql-dev libpq py3-psycopg2 libstdc++ antiword \
  && apk --no-cache add --virtual build-deps linux-headers libc-dev ca-certificates gcc g++  \
  && pip install  -r /tmp/python-libs.txt \
  && apk del build-deps

WORKDIR /code/