FROM alpine:3

RUN apk add --no-cache py3-pip tzdata libxml2-dev libxslt-dev gcc musl-dev python3-dev curl && \
	pip3 install --no-cache-dir requests httplib2 parse lxml

COPY ./my-rokus.txt /usr/src/app/
COPY ./roku-apps.xml /usr/src/app/
COPY ./roku-remote-rest-server.py /usr/src/app/

RUN chmod +x /usr/src/app/roku-remote-rest-server.py

EXPOSE 8889

CMD [ "python3", "/usr/src/app/roku-remote-rest-server.py"]
