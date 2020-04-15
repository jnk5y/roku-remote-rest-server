#!/usr/bin/env python3
""" Roku Remote Rest Server

Authors: John Kyrus

Description: Python rest server to that gets commands from google assistant through ifttt
    which then sends commands to local rokus. Can give basic remote commands strung together 
    ex. roku bedroom [roku box name] left up left select [commands]
"""

##############################################################################
import re
import sys
import signal
import os
import json
import logging
import traceback
import time
from time import strftime
from datetime import datetime
from datetime import timedelta

from http.server import HTTPServer, BaseHTTPRequestHandler
import base64
import ssl
import httplib2
import requests

import pickle
from lxml import etree
import xml.etree.ElementTree as ET

LOCALPATH = '/usr/src/app/'

def read_secrets():
    try:
        # Read secret files
        logger.info("Reading secret files")

        f = open('/run/secrets/username', "r")
        username = f.readline().strip()
        f.close()

        f = open('/run/secrets/password', "r")
        password = f.readline().strip()
        f.close()
    except:
        logger.error("Exception reading secrets files: %s", sys.exc_info()[0])
        sys.exit(0)

    return username, password

def roku_listener(logger, action, my_rokus, my_apps_tree):
    rokuName = ''
    triggerType = ''
    trigger = ''
    triggered = False
    url = ''
    
    whichRoku = action.split('%20')
    for roku in my_rokus:
        if whichRoku[0] in roku.lower():
            rokuName = roku
            # Remove the roku name from the argument
            action = action.replace(whichRoku[0],'')
            action = action.lstrip()
    
    if rokuName != '':
        if 'search' in action:
            triggerType = 'search'
            action = action.replace('search','')
            action = action.lstrip()
            action = action.replace(' ','%20')
            trigger = 'browse?' + action
            triggered = True
        elif 'open' in action or 'launch' in action:
            triggerType = 'launch'
            action = action.replace('launch','')
            action = action.replace('open','')
            action = action.lstrip()
            for app in my_apps_tree.findall('app'):
                if action in app.text.lower():
                    trigger = app.get('id')
            triggered = True
        elif 'volume' in action:
            triggerType = 'keypress'
            action = action.replace('volume','')
            action = action.lstrip()
            commandList = action.split(' ')
            for command in commandList:
                triggered = False
                if command == 'up':
                    trigger = 'volumeup'
                    triggered = True
                elif command == 'down':
                    trigger = 'volumedown'
                    triggered = True
        else:
            triggerType = 'keypress'
            commandList = action.split('%20')
            for command in commandList:
                logging.info("Command %s", command)
                if command == 'home' or command == 'select' or \
                   command == 'left' or command == 'right' or \
                   command == 'down' or command == 'up' or \
                   command == 'back' or command == 'info':
                    trigger = command
                    triggered = True
                elif command == 'reverse' or command == 'rewind':
                    trigger = 'rev'
                    triggered = True
                elif command == 'forward':
                    trigger = 'fwd'
                    triggered = True
                elif command == 'play' or command == 'pause':
                    trigger = 'play'
                    triggered = True
                elif command == 'replay':
                    trigger = 'instantreplay'
                    triggered = True

                if triggered:
                    triggered = False
                    url = my_rokus[rokuName] + '/' + triggerType + '/' + trigger
                    try:
                        requests.post(url, timeout=2)
                    except requests.RequestException as e:
                        logger.error(e)
                    logger.info(url)
                    time.sleep(1)

        if triggered:
            url = my_rokus[rokuName] + '/' + triggerType + '/' + trigger
            try:
                requests.post(url, timeout=2)
            except requests.RequestException as e:
                logger.error(e)
            logger.info(url)
            time.sleep(1)

    return url

##############################################################################
# Main functionality
##############################################################################
# Set up logging
logger = logging.getLogger('roku_rest_server')
log_fmt = '%(asctime)-15s %(levelname)-8s %(message)s'
log_level = logging.INFO
LOG_FILENAME = "/var/log/roku_rest_server.log"

logging.basicConfig(format=log_fmt, level=log_level)
#logging.basicConfig(format=log_fmt, level=log_level, filename=LOG_FILENAME)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    ''' Main class for authentication. '''
    def do_GET(self):
        path = self.path.split('?_=',1)[0]
        path = path.split('/')
        trigger = path[1].lower()
        action = path[2].lower()
        response = ''
        
        if trigger == 'roku' and action == 'health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain');
            self.end_headers()
            response = 'healthy'
            self.wfile.write(response.encode())
            pass
        else:
            username, password = read_secrets()

            if( username == '' or password == ''):
                logger.error('no username or password')
                sys.exit(0)
        
            authentication = username + ':' + password
            key = base64.b64encode(authentication.encode())
        
            if self.headers.get('Authorization') == 'Basic '+ str(key,'utf-8'):
                if trigger == 'roku':
                    response = roku_listener(logger, action, my_rokus, my_apps_tree)

                self.send_response(200)
                self.send_header('Content-Type', 'text/plain');
                self.end_headers()
                self.wfile.write(response.encode())
                pass
            else:
                pass
            pass

try:
    CERTFILE_PATH = LOCALPATH + "certs/live/server.kyrus.xyz/fullchain.pem"
    KEYFILE_PATH = LOCALPATH + "certs/live/server.kyrus.xyz/privkey.pem"

    httpd = HTTPServer(('', 8889), SimpleHTTPRequestHandler)
    httpd.socket = ssl.wrap_socket (httpd.socket, keyfile=KEYFILE_PATH, certfile=CERTFILE_PATH, server_side=True)
    sa = httpd.socket.getsockname()

    # Banner
    logger.info("==========================================================")
    logger.info("Python REST Server")
    logger.info("Serving HTTPS on port %d", sa[1])

    ##############################################################################
    # Initiate roku information
    ##############################################################################
    logger.info("Listening for roku commands")
    
    #import dict of rokus
    my_rokus = {}
    try:
        with open(LOCALPATH + 'my_rokus.txt', 'rb') as myFile:
            my_rokus = pickle.load(myFile)
    except:
        logger.error("Exception opening my_rokus.txt: %s", sys.exc_info()[0])

    try:
        #Import apps and their IDs
        my_apps_tree = ET.parse(LOCALPATH + 'roku_apps.xml')
    except:
        logger.error("Exception opening roku_apps.xml: %s", sys.exc_info()[0])

    httpd.serve_forever()

except:
    logging.critical("Terminating process")

finally:
    logger.error("Exiting Python REST Server")
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
    sys.exit(0)
