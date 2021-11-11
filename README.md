# roku-remote-rest-server

## File Descriptions
  * `roku-finder.py` Finds rokus on your network (FIREWALLS WILL BLOCK THE DISCOVER SCRIPT) and writes the list to my-rokus.txt and creates an xml list of apps found on one of the rokus called roku-apps.xml.
    * `my-rokus.txt` - a dict of the rokus on the network, their names and their IP addresses
    * `roku-apps.xml` - an xml output of a roku's installed apps which allows a user to launch an app listed
  * `roku-remote-rest-server.py` - takes https requests to control a listed roku device.

## Create Secret
You must create a podman secret, AUTHKEY, before running. AUTHKEY is your username:password base64 encrypted  
`printf <secret> | podman secret create AUTHKEY -`

## Certificates
The script needs a certfile (fullchain.pem) and a keyfile (privkey.pem) to secure the socket. I use letsencrypt and create a volume to the certs folder and I use an ENV variable CERTPATH to provide the remaining path.
 
## Build  
`podman build -t roku-remote-rest-server -f ./Dockerfile`  
 `docker build . -t roku-remote-rest-server`
 
## Deploy  
`podman run -d -e CERTPATH='live/<SERVER NAME>' -e TZ='US/Eastern' --secret AUTHKEY -p 8889:8889 -v <LETSENCRYPT FOLDER>:/usr/src/app/certs/:z --healthcheck-command 'curl --fail -k -s https://localhost:8889/roku/health || exit 1' --label "io.containers.autoupdate=image" --name roku-remote roku-remote-rest-server`

## Systemd Connection
This will allow your server to restart the running pods on a server restart or if they are stopped.  
`podman generate systemd --new --name roku-remote | sudo tee ~/.config/systemd/user/container-roku-remote.service >/dev/null`  
Now you can use systemctl --user calls to enable, start, stop or view the status of your pod  
`systemctl --user enable container-roku-remote.service`  
`systemctl --user start container-roku-remote.service`

## REST Call
When running you can make calls to the rest server  
`https://<SERVER NAME>:8889/roku/<ROKU-NAME> <COMMANDS>`
 
### Commands
 * search <x> - opens a roku search for <x>
 * open <x> or launch <x> - launches the app <x> which must be listed in the roku-apps.xml
 * home, select, left, right, down, up, back, info, reverse, rewind, forward, play, pause, replay - which correspond to a button on the roku remote. These can be chained together in one request for example, `right right down select`

### Examples
 * You can use postman to test but you must have a header with KEY: "Authorization" and VALUE: "Basic Base64-encoded-username:password". Your request would be a GET `https://<SERVER NAME>:8889/roku/office right right down select`
 * IFTTT webhook url would be `https://username:password@<SERVER NAME>:8889/roku/{{TextField}}`. I have it connected to Google Assistant where I can say a phrase with a text ingredient and for What do you want to say? I have `Roku $`
