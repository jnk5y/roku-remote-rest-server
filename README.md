# roku-remote-rest-server

Two python scripts.
  * `roku-finder.py` Finds rokus on your network and writes the list to my-rokus.txt and creates an xml list of apps found on one of the rokus called roku-apps.xml:
    * my-rokus.txt - a dict of the rokus on the network, their names and their IP addresses
    * roku-apps.xml - an xml output of a roku's installed apps which allows a user to launch an app listed
    * FIREWALLS WILL BLOCK THE DISCOVER SCRIPT
  * `roku-remote-rest-server.py` takes https requests to control a listed roku device.
