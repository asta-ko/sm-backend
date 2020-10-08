FROM python:3.7-slim-buster


RUN apt-get update

RUN apt-get -y install libpq-dev python3-dev gcc libsnappy-dev
RUN apt-get -y install g++
COPY python-libs.txt /tmp/
COPY python-test-libs.txt /tmp/
RUN pip install  -r /tmp/python-test-libs.txt
RUN pip install pandas==0.23.4
RUN apt-get -y install git
RUN apt-get purge --auto-remove -yqq $buildDeps && apt-get autoremove -yqq --purge \
    && apt-get clean && rm -rf var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/man \
        /usr/share/doc /usr/share/doc-base


ARG GITLAB_TOKEN
ARG GITLAB_USER
RUN pip install git+https://$GITLAB_USER:$GITLAB_TOKEN@gitlab.com/ovdinfo/oi-packages/django-jet-oi-edition.git
RUN pip install gevent

RUN mkdir /data/
RUN chmod  755 -R /data/
EXPOSE 8793

RUN apt-get -y install bash

WORKDIR /code/










