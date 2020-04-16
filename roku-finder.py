#!/usr/bin/env python3

import logging
import time
import pickle
import urllib.request, urllib.error, urllib.parse
from lxml import etree
import xml.etree.ElementTree as ET
from parse import *
from lxml import etree
from roku import Roku

##############################################################################
# Main functionality
##############################################################################
class Roku_Finder(object):

    def main(self):
            
        # Banner
        print('==========================================================')
        print('Discovering Rokus')

        num_rokus = 0
        my_rokus = {}
        rokus = {}

        for x in range(0, 2):
            rokus = Roku.discover(10,1)
            if len(rokus) > 0:
                break
        else:
            print('No Rokus discovered on network. Exiting program.')
            quit()

        my_apps_xml = ''
        
        print(rokus)
        for device in rokus:
            device = parse("<Roku: {}:{}>", str(device))
            device_ip = device[0]
            device_port = device[1]
                
            baseurl = 'http://' + device_ip + ':' + device_port
            url = baseurl + '/query/device-info'
            print(url)
            try:
                response = urllib.request.urlopen(str(url))
                content = response.read()
            except urllib.error.HTTPError as e:
                print(('HTTPError = ' + str(e.code)))
                continue
            except urllib.error.URLError as e:
                print(('URLError = ' + str(e.reason)))
                continue
            except httplib.HTTPException as e:
                print('HTTPException')
                continue


            # find the names of the rokus
            device_tree = etree.XML(content)
            device_name = device_tree.find('user-device-name')
            my_rokus[device_name.text] = baseurl

            # find the apps installed on the first roku found
            if my_apps_xml == '':
                try:
                    response = urllib.request.urlopen(baseurl + '/query/apps')
                    my_apps_xml = response.read()
                except urllib.error.HTTPError as e:
                    print(('HTTPError = ' + str(e.code)))
                    continue
                except urllib.error.URLError as e:
                    print(('URLError = ' + str(e.reason)))
                    continue
                except httplib.HTTPException as e:
                    print('HTTPException')
                    continue

        # write the rokus to a file for use by the roku_trigger script
        with open("my-rokus.txt", "wb") as myFile:
            pickle.dump(my_rokus, myFile)

        # write the apps list xml to a file for use by the roku_trigger script
        with open("roku-apps.xml", "wb") as myFile:
            myFile.write(my_apps_xml)
 
        print('Saving the following Rokus and the apps installed on them')
        print(my_rokus)

if __name__ == "__main__":
        Roku_Finder().main()
