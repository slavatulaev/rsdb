#!/usr/bin/env python
########## python inteface to RSDB

import csv
import os
import sys

import mysql.connector
from netaddr import *

########## vars ########

dbServerAddress = sys.argv[1]
dbDBName = sys.argv[2]
dbUserName = sys.argv[3]
dbPassword = sys.argv[4]

########################
def printALine():       # prints a divider 
    print('==================================================')
    return

def dbTest():           # not used in code - delete afterwards
    dbRS = mysql.connector.connect(
        user = dbUserName,
        password = dbPassword,
        host = dbServerAddress,
        database = dbDBName)
    cursor = dbRS.cursor()
    query = ("SELECT * FROM IP_DIAPAZONS")
    cursor.execute(query)
    for (IPDIA, COUNTRY, STATE, CITY, PROVIDER, DATE) in cursor:
     print("{}, {}, {}, {}, {}, {}".format(IPDIA, COUNTRY, STATE, CITY, PROVIDER, DATE))
    cursor.close()
    dbRS.close()
    return

def mainMenu():
    printALine()
    print('==================== Main Menu ===================')
    printALine()
    print('0 : Exit script')
    print('1 : Check and add IP Ranges')
    print('2 : Add New Data from RouterScan') 
    print('3 : Working with routers info (not ready yet)')
    printALine()
    return input()

def subMenu1():         # menu for work with ip ranges
    printALine()
    print('=============== IP Ranges Submenu =============')
    printALine()
    print('0 : Go to Main Menu')
    print('1 : Check and add to DB IP Ranges')
    print('2 : IP Range Tools')
    printALine()
    return input()

def subMenu2():         # menu for Add New Data from RouterScan
    printALine()
    print('=============== Add New Data from RouterScan Submenu =============')
    printALine()
    print('0 : Go to Main Menu')
    print('1 : Add New Data from RouterScan')
    print('2 : ... < not ready yet >')
    printALine()
    return input()

def subSubMenu1():      # IP Range Tools subsubmenu
    printALine()
    print('=============== IP Tools Submenu =============')
    printALine()
    print('0 : Go to IP Ranges Submenu')
    print('1 : Check and optimize IP Ranges in DB (not ready yet)')
    print('2 : Devide big network into parts (not ready yet)')
    return input()

def checkIPRange():     # checking ip ranges by list and adding new to database
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
    print('...online DB connected...')
    cursor = dbRS.cursor()
    query = ("SELECT IPDIA FROM IP_DIAPAZONS")
    cursor.execute(query)
    print('...query %s executed...' % query)
    for IPDIA in cursor:
        ipNetsInDB.add(IPDIA[0])
    print('...reading cursor finished...')
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
            print("Wrong input. Choose 'y' or 'n'")
    cursor.close()
    dbRS.close()
    return        

def addNewDataFromRS():
    insertQuery = ("INSERT INTO SCANRESS "
                "(IP, PORT, LOGPASS, DEVICE, BSSID, ESSID, SECURITY, WKEY, WPSPIN, LANIP, LANMASK, WANIP, WANMASK, WANGATEWAY, DNS, COMMENTS) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

    selectQuery = "SELECT * FROM SCANRESS WHERE IP = %s AND PORT = %s"

    updateQuery = "UPDATE SCANRESS SET LOGPASS = %s, DEVICE = %s, BSSID = %s, ESSID = %s, SECURITY = %s, WKEY = %s, WPSPIN = %s, LANIP = %s, LANMASK = %s, WANIP = %s, WANMASK = %s, WANGATEWAY = %s, DNS = %s, COMMENTS = %s WHERE IP = %s AND PORT = %s"

    insCounter, updCounter = 0, 0

    print('Connecting to online DataBase.... Please Wait....')
    dbRS = mysql.connector.connect(
        user = dbUserName,
        password = dbPassword,
        host = dbServerAddress,
        database = dbDBName)
    cursor = dbRS.cursor()
    print("Input the path to directory with .csv files (for default location 'rs_csv/' in current directory - just press Enter)")
    dirPath = input()
    if  dirPath == '': dirPath = 'rs_csv/'
    filesList = filter(lambda x: x.endswith('.csv'), os.listdir(dirPath)) 
    for fileName in filesList:
        with open(dirPath+fileName, encoding="ISO-8859-1") as csvfile:
            readCSV = csv.reader(csvfile, delimiter=';')
            for row in readCSV:
                if (row[0] == 'IP Address') or (row[4] == ''): continue
                selectArgs = (row[0], row[1])
                print(selectQuery % selectArgs)
                cursor.execute(selectQuery, selectArgs)
                result = cursor.fetchall()
                if len(row[5]) > 255: 
                    row[5] = row[5][0:255]
                if len(row[8]) > 17: 
                    row[8] = row[8][0:17]
                if len(row[9]) > 45: 
                    row[9] = row[9][0:45]
                if len(row[10]) > 10: 
                    row[10] = row[10][0:10]
                if len(row[11]) > 45: 
                    row[11] = row[11][0:45]
                if len(row[12]) > 8: 
                    row[12] = row[12][0:8]
                if len(row[13]) > 15: 
                    row[13] = row[13][0:15]
                if len(row[14]) > 15: 
                    row[14] = row[14][0:15]
                if len(row[15]) > 15: 
                    row[15] = row[15][0:15]
                if len(row[16]) > 15: 
                    row[16] = row[16][0:15]
                if len(row[17]) > 15: 
                    row[17] = row[17][0:15]
                if len(result) == 0:
                    insertArgs = (row[0], row[1], row[4], row[5], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[21])
                    print(insertQuery % insertArgs)
                    cursor.execute(insertQuery, insertArgs)
                    dbRS.commit()
                    insCounter = insCounter + 1
                else:
                    print('such IP:PORT already in DB')
                    if (row[4] != result[0][2]) or (row[5] != result[0][3]) or (row[8] != result[0][4]) or (row[9] != result[0][5]) or (row[10] != result[0][6]) or (row[11] != result[0][7]) or (row[12] != result[0][8]) or (row[13] != result[0][9]) or (row[14] != result[0][10]) or (row[15] != result[0][11]) or (row[16] != result[0][12]) or (row[17] != result[0][13]) or (row[18] != result[0][14]) or (row[21] != result[0][15]):
                        if (row[4] != result[0][2]) or (row[5] != result[0][3]) or (row[8] != result[0][4]) or (row[9] != result[0][5]) or (row[10] != result[0][6]) or (row[11] != result[0][7]) or (row[12] != result[0][8]): print('diff in FIRST HALF')
                        if (row[13] != result[0][9]) or (row[14] != result[0][10]) or (row[15] != result[0][11]) or (row[16] != result[0][12]) or (row[17] != result[0][13]) or (row[18] != result[0][14]) or (row[21] != result[0][15]): print('diff in SECOND HALF')

                        updateArgs = (row[4], row[5], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[21], row[0], row[1])
                        print(updateQuery % updateArgs)
                        cursor.execute(updateQuery, updateArgs)
                        dbRS.commit()
                        updCounter = updCounter + 1
    cursor.close()
    dbRS.close()
    print('')
    print('=================================================================================')
    print('Totally inserted %i rows and updated %i rows' % (insCounter, updCounter))
    print('')
    print('')
    return

def optimizeIPRangesDB(): 
    ipNetsInDB = IPSet() 
    print('Connecting to online DataBase.... Please Wait....')
    dbRS = mysql.connector.connect(
        user = dbUserName,
        password = dbPassword,
        host = dbServerAddress,
        database = dbDBName)
    cursor = dbRS.cursor()
    query = ("SELECT IPDIA FROM IP_DIAPAZONS")
    cursor.execute(query)
    print('Reading all the IP Ranges from the Database.... Please Wait....')
    for IPDIA in cursor:
        ipNetsInDB.add(IPDIA[0])

    cursor.close()
    dbRS.close()
    return

def subSubMenu1execution():
    while True:
        sm1res = subSubMenu1()
        if sm1res == '0':
            break
        elif sm1res == '1':
            optimizeIPRangesDB()
        elif sm1res == '2':
            print('Here will be Devide big network into parts')
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

def subMenu2execution():
    while True:
        sm1res = subMenu1()
        if sm1res == '0':
            break
        elif sm1res == '1':
            addNewDataFromRS()
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
        subMenu2execution()
    elif mmres == '3':
        print('Working with routers info (not working yet)')
    else:
        print('Wrong input')


print('Bye bye, Neo')
printALine()

