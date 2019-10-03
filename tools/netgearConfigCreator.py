#!/usr/bin/env python
########## python inteface to RSDB

import os

import re
import sys
import socket
digitRange = ['0','1','2','3','4','5','6','7','8','9']

#input("""
#        This script requeres 4(!!!) files to be in current working directory
#        client.conf
#        client.key
#        ca.crt
#        client.crt
#        and it will create an final config with IP address as a name and all keys and sertificates included
#        also it will include some windows specific directives
#        
#        Press any key to continue...""")

configLinesList = []
if os.path.exists('client.conf'):
    client2File = open('client.conf','r')
elif os.path.exists('client2.conf'):
    client2File = open('client2.conf','r')
elif os.path.exists('client3.ovpn'):
    client2File = open('client3.ovpn','r')    
elif os.path.exists('client.ovpn'):
    client2File = open('client.ovpn','r') 
elif os.path.exists('client_phone.ovpn'):    
    client2File = open('client_phone.ovpn','r')
else:
    print('File with config not found. Exiting...\n')
    sys.exit()   
caFile = open('ca.crt','r')
clientcrtFile = open('client.crt','r')
clientkeyFile = open('client.key','r')

configLinesList.append('###################################################################################################\n')
configLinesList.append('###########(///(###################################################################################\n')
configLinesList.append('########///////////################################################################################\n')
configLinesList.append('######(////#####(////#######////////##(//(///#(//////(#///##(/(#  /###  ##  ,,  *#   ### .(*/######\n')
configLinesList.append('######///(#(   (##///(#####///####(//#(/(##(/((//######////#(/(##  ##  /##  ###  #  . ## .#########\n')
configLinesList.append('######///##     (#///(#####//(#####//((/////(#(/////###//#//(/(##/  * .###      ##  #, * .#########\n')
configLinesList.append('######///(##* .###///######(//(###///#(/(#####(//######//##///(###*   ####  ######  ##*  .#########\n')
configLinesList.append('#######///##,  ##///#########(/////###(/(#####(//////(#//###(/(####. #####  ######  #### .#########\n')
configLinesList.append('#########/##   ##((################################################################################\n')
configLinesList.append('###################################################################################################\n')

for line in client2File:
    if (line.find('ca ca.crt') != -1) or (line.find('cert client.crt') != -1) or (line.find('key client.key') != -1):
        continue
    if line.find('remote') != -1:
        addr = line[line.find(' ')+1:line.rfind(' ')].strip()
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', addr) != None:
            ipAddr = addr
            configLinesList.append(line)
        else:
            print('addr:'+addr+'|')
            ipAddr = socket.gethostbyname(addr)
            configLinesList.append(line.replace(addr,ipAddr))
        continue
    configLinesList.append(line)

configLinesList.append('setenv opt block-outside-dns\n')
configLinesList.append('redirect-gateway def1\n')
configLinesList.append('tun-mtu 1500\n')
configLinesList.append('mssfix 1200\n')
configLinesList.append('sndbuf 0\n')
configLinesList.append('rcvbuf 0\n')
configLinesList.append('push "sndbuf 0"\n')
configLinesList.append('push "rcvbuf 0"\n')
configLinesList.append('ping-timer-rem\n')
configLinesList.append('verb 4\n')
configLinesList.append('#setenv opt tls-cipher "DEFAULT:@SECLEVEL=0"\n')
configLinesList.append('#dhcp-option DNS 1.1.1.1\n')

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

outputFile = open(ipAddr + '.ovpn','w')
outputFile.writelines(configLinesList)
print()
print(configLinesList)
client2File.close()
clientkeyFile.close()
caFile.close()
clientcrtFile.close()
outputFile.close()


if os.path.exists('client.conf'):
    os.remove('client.conf')
elif os.path.exists('client2.conf'):
    os.remove('client2.conf')
elif os.path.exists('client3.ovpn'):
    os.remove('client3.ovpn')    
elif os.path.exists('client.ovpn'):
    os.remove('client.ovpn') 
elif os.path.exists('client_phone.ovpn'):
    os.remove('client_phone.ovpn') 
os.remove('ca.crt')
os.remove('client.crt')
os.remove('client.key')
  