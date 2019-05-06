#!/usr/bin/env python
########## python inteface to RSDB

import os
import sys
import socket
digitRange = ['0','1','2','3','4','5','6','7','8','9']

input("""
        This script requeres 4(!!!) files to be in current working directory
        client2.conf
        client.key
        ca.crt
        client.crt
        and it will create an final config with IP address as a name and all keys and sertificates included
        also it will include some windows specific directives
        
        Press any key to continue...""")

configLinesList = []

client2File = open('client2.conf','r')
caFile = open('ca.crt','r')
clientcrtFile = open('client.crt','r')
clientkeyFile = open('client.key','r')

for line in client2File:
    if (line.find('ca ca.crt') != -1) or (line.find('cert client.crt') != -1) or (line.find('key client.key') != -1):
        continue
    configLinesList.append(line)
    if line.find('remote') != -1:
        addr = line[line.find(' ')+1:line.rfind(' ')]
        if addr[0] in digitRange:
            ipAddr = addr
        else:
            ipAddr = socket.gethostbyname(addr)

configLinesList.append('<ca>\n')
for line in caFile:
    configLinesList.append(line)
configLinesList.append('</ca>\n')

configLinesList.append('<cert>\n')
for line in clientcrtFile:
    configLinesList.append(line)
configLinesList.append('</cert>\n')

configLinesList.append('<key>\n')
for line in clientkeyFile:
    configLinesList.append(line)
configLinesList.append('</key>\n')

configLinesList.append('block-outside-dns\n')
configLinesList.append('redirect-gateway def1\n')
configLinesList.append('tun-mtu 1500\n')
configLinesList.append('mssfix 1200\n   ')

outputFile = open(ipAddr + '.ovpn','w')
outputFile.writelines(configLinesList)
print()
print(configLinesList)
client2File.close()
clientkeyFile.close()
caFile.close()
clientcrtFile.close()
outputFile.close()
