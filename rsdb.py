#!/usr/bin/env python
########## python inteface to RSDB

import sys
import mysql.connector
from netaddr import *
import pprint

########## vars ########

dbServerAddress = sys.argv[1]
dbDBName = sys.argv[2]
dbUserName = sys.argv[3]
dbPassword = sys.argv[4]

########################
def printALine():
    print('==================================================')
    return

def dbTest():
    dbRS = mysql.connector.connect(
        user = dbUserName,
        password = dbPassword,
        host = dbServerAddress,
        database = dbDBName)
    cursor = dbRS.cursor()
    query = ("SELECT * FROM IP_DIAPAZONS")
    cursor.execute(query)
    for (IPDIA, SCANNED, COUNTRY, STATE, CITY, PROVIDER, DATE) in cursor:
     print("{}, {}, {}, {}, {}, {}, {}".format(IPDIA, SCANNED, COUNTRY, STATE, CITY, PROVIDER, DATE))
    cursor.close()
    dbRS.close()
    return

def mainMenu():
    printALine()
    print('==================== Main Menu ===================')
    printALine()
    print('0 : Exit script')
    print('1 : Check and add IP Ranges')
    print('2 : Add New Data from RouterScan (not working yet)') 
    print('3 : Working with routers info (not working yet)')
    printALine()
    return input()

def subMenu1():
    printALine()
    print('=============== IP Diapazons Submenu =============')
    printALine()
    print('0 : Go to Main Menu')
    print('1 : Check and add to DB IP Ranges')
    print('2 : Here will be some more functions later')
    printALine()
    return input()

def checkIPRange():
    ipNetsInDB = IPSet()
    ipNetsFromFile = IPSet()
    printALine()
    print('Input the IP list file name (default iplist.txt in current directory)')
    ipListFileName = input()
    if ipListFileName == '': ipListFileName = 'iplist.txt'
    ipListFile = open(ipListFileName)
    for line in ipListFile:
        if line.strip() == '': break
        if line.find('-') < 0:
            ipNetsFromFile.add(line)
        else:
            ipNetsFromFile.add(IPRange(line[:line.find('-')],line[line.find('-')+1:]))
    print('Nets from File: ', ipNetsFromFile)
    print('Connecting to online DataBase.... Please Wait....')
    dbRS = mysql.connector.connect(
        user = dbUserName,
        password = dbPassword,
        host = dbServerAddress,
        database = dbDBName)
    cursor = dbRS.cursor()
    query = ("SELECT IPDIA FROM IP_DIAPAZONS")
    cursor.execute(query)
    for IPDIA in cursor:
        ipNetsInDB.add(IPDIA[0])
#    print('Nets from DB: ', ipNetsInDB)
    crossIPSet = ipNetsInDB & ipNetsFromFile
    diffIPSet = ipNetsFromFile & (ipNetsInDB ^ ipNetsFromFile)
    if len(crossIPSet) > 0:
        print('')
        print('Following networks are in database and already been scanned:')
        for ipNet in crossIPSet.iter_cidrs():
            print(ipNet)
        print('')
    printALine()
    print('Below see the list of networks never scanned before:')
    print('')
    for ipNet in diffIPSet.iter_cidrs():
        print(ipNet)
    print('')
    printALine()
    if len(diffIPSet) == 0:
        print("There's no new networks in your list, all of them already in database (means been scanned). So exiting to the Menu...")
        return
    print("Do you want to save to file ip_nets_result.txt? (y/n)")
    if input() == 'y':
        file = open('ip_nets_result.txt','w')
        for ipNet in diffIPSet.iter_cidrs():
            file.write(str(ipNet) + '\n')
        print('List of networks been saved to file ip_nets_result.txt')
        printALine()
    print('Should it be added to the Online Database right now? (y/n)')
    while True:
        i = input()
        print('input is: ', i)
        if i == 'y':
            print('Starting adding data to online Database, this can take a some time...')
            for ipNet in diffIPSet.iter_cidrs():
                query = ("INSERT INTO IP_DIAPAZONS (IPDIA) VALUES ('" + str(ipNet) + "')")
                print(query)
                cursor.execute(query)
            print('Addind networks DONE')
            break
        elif i == 'n':
            print('Ok, you choose not to add this data to online Database. \n Exiting to menu.')
            break
        else:
            print("Wrong input. Choose 'y' or 'y'")
    cursor.close()
    dbRS.close()
    return        
    

def subMenu1execution():
    while True:
        sm1res = subMenu1()
        if sm1res == '0':
            break
        elif sm1res == '1':
            checkIPRange()
        elif sm1res == '2':
            print('Here will be some more functions')
    return 

while True:
    mmres = mainMenu()
    if mmres == '0':
        break
    elif mmres == '1':
        subMenu1execution()
    elif mmres == '2':
        print('Add New Data from RouterScan (not working yet)')
    elif mmres == '3':
        print('Working with routers info (not working yet)')
    else:
        print('Wrong input')


print('Bye bye, Neo')
printALine()

