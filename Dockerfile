# syntax=docker/dockerfile:1
FROM nginx/unit:1.26.1-python3.9
RUN mkdir -p /var/www/schemes
WORKDIR /var/www/schemes
ADD src /var/www/schemes/src
ADD schemes /var/www/schemes/schemes
ADD ./config/requirements.txt /var/www/schemes/
ADD ./config/config.json /docker-entrypoint.d
RUN apt update && apt install -y python3-pip && pip3 install -r requirements.txt
RUN rm requirements.txt