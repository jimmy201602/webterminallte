#Webterminal dockfile
FROM webterminallte:latest
LABEL maintainer zhengge2012@gmail.com
#WORKDIR /tmp
#RUN apk update
#RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories
#RUN apk add --no-cache python3 python3-dev nginx git libffi-dev gcc musl-dev linux-headers krb5-dev openssl-dev make zlib-dev libjpeg-turbo-dev 
#RUN wget https://bootstrap.pypa.io/get-pip.py
#RUN python3 get-pip.py
#RUN apk add --no-cache redis
#RUN pip install -r requirements.txt -i  https://pypi.doubanio.com/simple
#RUN mkdir -p /run/openrc
#RUN touch /run/openrc/softlevel
#RUN mkdir -p /var/log/web/

ADD docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
EXPOSE 80
CMD ["/docker-entrypoint.sh", "start"]