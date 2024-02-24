FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install vim -y
RUN apt-get install python-dev
RUN apt-get install python-pip -y

RUN mkdir -p /etc/conf/lifeline

COPY pie_in_the_sky.py .

ENV PYTHONUNBUFFERED=0

ENTRYPOINT ["python", "-u", "./pie_in_the_sky.py"]