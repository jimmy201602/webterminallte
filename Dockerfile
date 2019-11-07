#Webterminal dockfile
FROM ubuntu:latest
LABEL maintainer zhengge2012@gmail.com
WORKDIR /opt
RUN apt-get update
RUN apt-get install -y vim python3 python3-dev nginx git libffi-dev gcc musl-dev  make  python3-pip libkrb5-dev libssh-dev libssl-dev redis-server
RUN sed -i 's/bind 127.0.0.1 ::1/bind 127.0.0.1/g' /etc/redis/redis.conf
RUN git clone https://github.com/jimmy201602/webterminallte
WORKDIR /opt/webterminallte
RUN pip3 install -r requirements.txt
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate
RUN python3 createsuperuser.py
RUN mkdir -p /var/log/web/
RUN mkdir -p /opt/webterminallte/media
ADD nginx.conf /etc/nginx/nginx.conf
ADD supervisord.conf /etc/supervisor/supervisord.conf
ADD docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
EXPOSE 80
CMD ["/docker-entrypoint.sh", "start"]
