#!/usr/bin/env python
########## find USA networks in 0.0.0.0/0

import csv
import os
import sys

import mysql.connector
from netaddr import *
import requests


divider = 12
checkerURL = 'https://www.ipqualityscore.com/api/json/ip/BGvBnwvenMqX6BhMYuODspdBG5CncD1s/'
output_File = open('usNetworks.txt', 'w')

allWorldNet = IPNetwork('0.0.0.0/0')
for subNetElem in allWorldNet.subnet(divider):
    print(checkerURL+str(subNetElem)[:-(len(str(divider))+1)])
    r = requests.get(checkerURL+str(subNetElem)[:-(len(str(divider))+1)])
    listFromRequest = r.text.split(',')
    for s in listFromRequest:
        if s.find('country_code') > 0:
            print(s.split(':')[1].strip('"'))
            if s.split(':')[1].strip('"') == 'US':
                print(subNetElem, 'belongs to US')
                output_File.write(str(subNetElem) + '\n')
