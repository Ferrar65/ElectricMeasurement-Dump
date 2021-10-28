FROM python:2

RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends cron python-serial python-mysqldb
RUN pip install crcmod

COPY read.py /
RUN chmod 755 /read.py

ENV PYTHONPATH /usr/local/lib/python2.7/site-packages/

COPY jobs.txt /etc/crontab

RUN touch /etc/crontab /etc/cron.*/*

COPY job.sh /
RUN chmod 755 /job.sh

CMD ["cron", "-f"]
