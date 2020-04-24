FROM python:3-slim

RUN apt-get update && apt-get install -y \
	python3-pip curl && \
	pip install --no-cache-dir requests httplib2 parse lxml

COPY ./my-rokus.txt /usr/src/app/
COPY ./roku-apps.xml /usr/src/app/
COPY ./roku-remote-rest-server.py /usr/src/app/

RUN chmod +x /usr/src/app/roku-remote-rest-server.py

EXPOSE 8889

CMD [ "python", "/usr/src/app/roku-remote-rest-server.py"]
