FROM python:3.12.7-bookworm
RUN apt-get update && apt-get install -y vim cron
RUN pip install langchain langchain-core langchain-community langchain-chroma chromadb
COPY main.py /root/main.py

# COPY crontab /etc/cron.d/crontab
# RUN chmod 0644 /etc/cron.d/crontab
# RUN crontab /etc/cron.d/crontab

COPY crontab /var/spool/cron/crontabs/root
RUN chmod 0644 /var/spool/cron/crontabs/root
RUN crontab /var/spool/cron/crontabs/root

RUN touch /var/log/cron.log && chmod 0666 /var/log/cron.log

CMD cron && tail -f /var/log/cron.log
