FROM python:3-slim

COPY ./my-rokus.txt /usr/src/app/
COPY ./roku-apps.xml /usr/src/app/
COPY ./roku-remote-rest-server.py /usr/src/app/

RUN chmod +x /usr/src/app/roku-remote-rest-server.py

RUN apt-get update && apt-get install -y \
      python3-pip curl && \
    pip3 install --upgrade pip && \
    pip3 install requests httplib2 parse lxml

EXPOSE 8889

CMD [ "python3", "/usr/src/app/roku-remote-rest-server.py"]
