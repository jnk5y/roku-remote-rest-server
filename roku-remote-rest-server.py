#!/usr/bin/env python3
""" Roku Remote Rest Server

Authors: John Kyrus

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
        f = open('/run/secrets/AUTHKEY', "r")
        AUTHKEY = f.readline().strip()
        f.close()
    except:
        logger.error("Exception reading secrets files: %s", sys.exc_info()[0])

    return AUTHKEY

def write_tz():
    try:
        f = open('/etc/timezone',"w")
        f.write(os.getenv('TZ', 'US/Eastern'))
        f.close()
    except:
        logger.error("Exception writing timezone to file: %s", sys.exc_info()[0])

    return

def roku_listener(logger, action, my_rokus, my_apps_tree):
    rokuName = ''
    triggerType = ''
    trigger = ''
    triggered = False
    url = ''
    action.lstrip()
    commandList = action.split('%20')
    for roku in my_rokus:
        if len(commandList) > 1:
            if commandList[0] in roku.lower():
                rokuName = roku
                commandList.pop(0)

    if rokuName != '':
        if 'search' == commandList[0] and len(commandList) > 1:
            triggerType = 'search'
            trigger = 'browse?'
            commandList.pop(0)
            for command in commandList:
                trigger = trigger + command + ' '
            triggered = True
        elif ('open' == commandList[0] or 'launch' == commandList[0]) and len(commandList) > 1:
            for app in my_apps_tree.findall('app'):
                if commandList[1] in app.text.lower():
                    triggerType = 'launch'
                    trigger = app.get('id')
                    triggered = True
        elif ('off' == commandList[0] or 'power' == commandList[0]):
            triggerType = 'keypress'
            trigger = 'PowerOff'
        elif 'volume' == commandList[0] and len(commandList) > 1:
            commandList.pop(0)
            for command in commandList:
                if command == 'up':
                    trigger = 'volumeup'
                    triggered = True
                elif command == 'down':
                    trigger = 'volumedown'
                    triggered = True
                
                if triggered:
                    url = my_rokus[rokuName] + '/keydown/' + trigger
                    try:
                        requests.post(url, timeout=10)
                    except requests.RequestException as e:
                        logger.error(e)
                    logger.info(url)
                    
                    time.sleep(3)

                    url = my_rokus[rokuName] + '/keyup/' + trigger
                    try:
                        requests.post(url, timeout=10)
                    except requests.RequestException as e:
                        logger.error(e)
                    logger.info(url)
                    
                    triggered = False
        else:
            triggerType = 'keypress'
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
                requests.post(url, timeout=10)
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
        
        if len(path) > 1:
            trigger = path[1].lower()
            action = path[2].lower()
            response = ''
        
            if trigger == 'roku' and action == 'health':
#                self.send_response(200)
#                self.send_header('Content-Type', 'text/plain');
#                self.end_headers()
#                response = 'healthy'
#                self.wfile.write(response.encode())
                pass
            else:
                AUTHKEY = read_secrets()

                if AUTHKEY == '':
                    logger.error('Empty Authentication Key Environment Variable')
                    sys.exit(0)
                else:
                    if self.headers.get('Authorization') == ('Basic '+ AUTHKEY):
                        if trigger == 'roku':
                            response = roku_listener(logger, action, my_rokus, my_apps_tree)

                        self.send_response(200)
                        self.send_header('Content-Type', 'text/plain');
                        self.end_headers()
                        self.wfile.write(response.encode())
                    else:
                        logger.error("Not Authorized")
        else:
            logger.error('Bad Path')
try:
    # Banner
    logger.info("==========================================================")

    ##############################################################################
    # Initiate roku information
    ##############################################################################
    my_rokus = {}
    try:
        #import dict of rokus
        logger.info("Reading roku list")
        with open(LOCALPATH + 'my-rokus.txt', 'rb') as myFile:
            my_rokus = pickle.load(myFile)
    except:
        logger.error("Exception opening my-rokus.txt: %s", sys.exc_info()[0])
        sys.exit(0)

    try:
        #Import apps and their IDs
        logger.info("Reading roku apps list")
        my_apps_tree = ET.parse(LOCALPATH + 'roku-apps.xml')
    except:
        logger.error("Exception opening roku-apps.xml: %s", sys.exc_info()[0])

    CERTFILE = LOCALPATH + "certs/" + os.environ.get('CERTPATH') + "fullchain.pem"
    KEYFILE = LOCALPATH + "certs/" + os.environ.get('CERTPATH') + "privkey.pem"

    if not os.path.isfile(CERTFILE):
        logger.error("Certfile not found: %s", sys.exc_info()[0])
        sys.exit(0)
        
    if not os.path.isfile(KEYFILE):
        logger.error("Keyfile not found: %s", sys.exc_info()[0])
        sys.exit(0)
    
    httpd = HTTPServer(('', 8889), SimpleHTTPRequestHandler)
    httpd.socket = ssl.wrap_socket (httpd.socket, keyfile=KEYFILE, certfile=CERTFILE, server_side=True)
    sa = httpd.socket.getsockname()

    write_tz()

    logger.info("Python REST Server")
    logger.info("Serving HTTPS on port %d", sa[1])
    logger.info("Listening for roku commands")
    
    httpd.serve_forever()

except:
    logging.critical("Terminating process")

finally:
    logger.error("Exiting Python REST Server")
    
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
    sys.exit(0)
