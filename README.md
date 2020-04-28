[![Build Status](https://travis-ci.com/jnk5y/roku-remote-rest-server.svg?branch=master)](https://travis-ci.com/jnk5y/roku-remote-rest-server)
[![Docker Stars](https://img.shields.io/docker/stars/jnk5y/roku-remote-rest-server.svg)](https://hub.docker.com/r/jnk5y/shepherd/)
[![Docker Pulls](https://img.shields.io/docker/pulls/jnk5y/roku-remote-rest-server.svg)](https://hub.docker.com/r/jnk5y/roku-remote-rest-server/)

# roku-remote-rest-server

Two python scripts.
  * `roku-finder.py` Finds rokus on your network and writes the list to my-rokus.txt and creates an xml list of apps found on one of the rokus called roku-apps.xml:
    * my-rokus.txt - a dict of the rokus on the network, their names and their IP addresses
    * roku-apps.xml - an xml output of a roku's installed apps which allows a user to launch an app listed
    * FIREWALLS WILL BLOCK THE DISCOVER SCRIPT
  * `roku-remote-rest-server.py` takes https requests to control a listed roku device.

You must create a docker secret, AUTHKEY, before running. AUTHKEY is your username:password base64 encrypted
 * `printf "place-your-AUTHKEY-here" | docker secret create AUTHKEY -`
 
To build the container image from the main folder
 * `docker build . -t roku-remote-rest-server`
 
To deploy to docker swarm from the main folder
 * `docker stack deploy --compose-file docker-compose.yaml roku-remote-rest-service`
 
When running you can make calls to the rest server
 * `https://your-server-name:8889/roku/roku-name commands-list`
 
Command List
 * search $ - opens a roku search for $
 * open or launch $ - launches the app $ which must be listed in the roku-apps.xml
 * volume [up|down] - should raise or lower the volume, still having issues with this one
 * home, select, left, right, down, up, back, info, reverse or rewind, forward, play or pause, replay - which correspond to a button on the roku remote. These can be chained together in one request for example, right right down select
 
Examples
 * You can use postman to test but you must have a header with KEY: "Authorization" and VALUE: "Basic Base64-encoded-username:password". Your request would be GET https://your-server-ip-or-name:8889/roku/office pause 
 * IFTTT webhook url would be https://username:password@your-server-ip-or-name:8889/roku/{{TextField}}. I have it connected to Google Assistant - Say a phrase with a text ingredient and for What do you want to say? I have Roku $
