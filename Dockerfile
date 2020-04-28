FROM alpine:3

RUN apk add --no-cache py3-pip libxml2-dev libxslt-dev gcc python3-dev && \
	pip3 install --no-cache-dir requests httplib2 parse lxml && \
	apk del .build-deps

COPY ./my-rokus.txt /usr/src/app/
COPY ./roku-apps.xml /usr/src/app/
COPY ./roku-remote-rest-server.py /usr/src/app/

RUN chmod +x /usr/src/app/roku-remote-rest-server.py

EXPOSE 8889

CMD [ "python", "/usr/src/app/roku-remote-rest-server.py"]
