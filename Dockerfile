FROM python:3.7
MAINTAINER Stenio Araujo "stenioalt@hiaraujo.com"

RUN mkdir /app /data

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY . /app
RUN pip install /app

WORKDIR /data

VOLUME /data

ENV CONDUCTOR_SEARCHCOUNTER_DATABASE /data/search_history.db

ENTRYPOINT ["conductor-searchcounter"]
