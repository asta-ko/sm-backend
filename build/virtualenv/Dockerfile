FROM alpine:3.7
FROM clutteredcode/python3-alpine-pandas

COPY python-libs.txt /tmp/
RUN apk add --update --no-cache   git openssh bash postgresql-dev libpq py3-psycopg2 py3-gevent libstdc++ antiword
RUN apk --no-cache add --virtual build-deps linux-headers libc-dev ca-certificates gcc g++ libffi-dev
RUN apk --no-cache add make
ARG GITLAB_TOKEN
ARG GITLAB_USER
RUN pip install git+https://$GITLAB_USER:$GITLAB_TOKEN@gitlab.com/ovdinfo/oi-packages/django-jet-oi-edition.git
RUN pip install gevent
RUN pip install  -r /tmp/python-libs.txt
RUN apk del build-deps

WORKDIR /code/
