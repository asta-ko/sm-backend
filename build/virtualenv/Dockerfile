#FROM alpine:3.7
FROM clutteredcode/python3-alpine-pandas

COPY python-libs.txt /tmp/
#RUN echo "@testing http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
RUN apk add --update --no-cache   git openssh bash postgresql-dev libpq py3-psycopg2 libstdc++ antiword freetype-dev libpng-dev openblas-dev \
  && apk --no-cache add --virtual build-deps linux-headers libc-dev ca-certificates gcc g++  \
  && pip install  -r /tmp/python-libs.txt \
  && apk del build-deps

WORKDIR /code/
