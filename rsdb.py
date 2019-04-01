#!/usr/bin/env python
########## python inteface to RSDB

import csv
import os
import sys

import mysql.connector
from netaddr import *
import requests
import json
import datetime


########## vars ########

dbServerAddress = sys.argv[1]
dbDBName = sys.argv[2]
dbUserName = sys.argv[3]
dbPassword = sys.argv[4]
workDirecory = os.getcwd()

########################
def printALine():       # prints a divider 
    print('==================================================')
    return

def getIPQualityScoreAPIKey():        #   выбор АПИ ключа для поиска по сайту www.ipqualityscore.com
    ipQualityScoreAPIKey = 'BGvBnwvenMqX6BhMYuODspdBG5CncD1s'
    return ipQualityScoreAPIKey

def getIPtoGeplocationAPIKey():       #  выбор АПИ ключа для поиска по сайту ipToGeplocation
    ipToGeplocationAPIKey = 'f0acbe9b985966c64d1e0bfa0b4e2497'
    return ipToGeplocationAPIKey

def getIPQualityScore(ipAddr):     # получение risk score с сайта www.ipqualityscore.com
    checkerURL = 'https://www.ipqualityscore.com/api/json/ip/' + getIPQualityScoreAPIKey() + '/' + ipAddr
    r = json.loads(requests.get(checkerURL).text)
    if r["message"] == 'Success':
        ipqualityscore = r["fraud_score"]
        print("IPqualityScore for IP %s detected and equal to %s" % (ipAddr, ipqualityscore))
    else:
        ipqualityscore = -1
    return ipqualityscore

def getGetIpIntel(ipAddr):          # получение fraud score с сайта www.getipintel.net
    now = datetime.datetime.now()
    nowStr = str(now).replace(' ','').replace(':','').replace('-','').replace('.','')
    randomEmail = nowStr + '@mail.com'
    checkerURL = 'http://check.getipintel.net/check.php?ip=' + ipAddr + '&contact=' + randomEmail + '&format=json'
    print(checkerURL)
    r = json.loads(requests.get(checkerURL).text)
    print(r)
    if r["status"] == 'success':
        getipintel = r["result"][:6]
        print("GetIPintel Score for IP %s detected and equal to %s" % (ipAddr, getipintel))
    else:
        getipintel = '-1'
    return getipintel

def writeTheFile(data, filename):     #запись данных из блоб-поля в файл
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'w') as file:
        file.write(data)
        file.close()

def mainMenu():     # Главное меню скрипта
    printALine()
    print('==================== Main Menu ===================')
    printALine()
    print('0 : Exit script')
    print('1 : Check and add IP Ranges')
    print('2 : Work with Data from RouterScan') 
    print('3 : Work with VPN Routers Data')
    print('4 : Sells of VPN Routers')
    print('5 : (not ready yet)')
    print('9 : Different service Tools')
    printALine()
    return input()

def subMenu1():         # menu for work with ip ranges - Подменю 1 - работа с диапазонами IP адресов
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
    print('=============== Work with Data from RouterScan Submenu =============')
    printALine()
    print('0 : Go to Main Menu')
    print('1 : Add New Data from RouterScan to online database')
    print('2 : Select Routers Data from Database for Local Processing')
    print('3 : Submit Routers Data into Online Database')
    print('4 : ... < not ready yet >')
    printALine()
    return input()

def subMenu3():         # menu for Work with VPN Routers Data
    printALine()
    print('=============== Work with VPN Routers Data =============')
    printALine()
    print('0 : Go to Main Menu')
    print('1 : Get VPN Routers list for editing / selling')
    print('2 : Submit edited VPN Roters info into online Database')
    print('3 : ... < not ready yet >')
    print('4 : ... < not ready yet >')
    printALine()
    return input()

def subMenu4():         # menu for Work with VPN Routers Data
    printALine()
    print('=============== Sells of VPN Routers =============')
    printALine()
    print('0 : Go to Main Menu')
    print('1 : Get a list of VPNs for selling')
    print('2 : Submit list of Sells from file')
    print('3 : ... < not ready yet >')
    print('4 : ... < not ready yet >')
    printALine()
    return input()

def subMenu9():         # menu for Different service Tools
    printALine()
    print('=============== Different service Tools =============')
    printALine()
    print('0 : Go to Main Menu')
    print('1 : Check Database for ipquality & getipintel score')
    print('2 : ... < not ready yet >')
    print('3 : ... < not ready yet >')
    print('4 : ... < not ready yet >')
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
        if line.strip() == '': continue
        if line.find('-') < 0:
            ipNetsFromFile.add(line.strip())
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

def addNewDataFromRS():      # Импорт данных сканирования RouterScan в онлайн-базу
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

def optimizeIPRangesDB(): ### this function not finished yet....  Оптимизация списка диапазонов
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

def getVpnRoutersRawDataFromDB():          # Получение из базы списка роутеров для поиска в них ВПН
    selectSQL = "SELECT * FROM SCANRESS WHERE (TAKEN IS NULL OR TAKEN = 0) AND ("
    selectSQLadd = " AND (CountryCode = '"
    updateSQL = "UPDATE SCANRESS SET CountryCode = %s, Country = %s, Region = %s, RegionName = %s, City = %s, ISP = %s, ASCode = %s, ZIP = %s WHERE IP = %s AND PORT = %s"
    print('Reading the list of routers models that can potentially have a VPN Server function')
    isFirst = True
    tempStr = ''
    outputCSV = 'workList.csv'
    checkerURL = 'http://ip-to-geolocation.com/api/json/'
    apiKey = getIPtoGeplocationAPIKey()
    for line in open(workDirecory+'/lst/vpnrfls.lst','r'):
        if line.strip() == '': break
        if not isFirst: tempStr += ' OR '
        tempStr += "DEVICE LIKE '%" + line[:-1] + "%'"
        isFirst = False
    selectSQL += tempStr + ")"
    print(selectSQL)
    print('Connecting to online DataBase.... Please Wait....')
    dbRS = mysql.connector.connect(
        user = dbUserName,
        password = dbPassword,
        host = dbServerAddress,
        database = dbDBName)
    cursor = dbRS.cursor()
    cursor.execute(selectSQL)
    result = cursor.fetchall()
    for rowS in result:
        print('getting geolocation data of ip ' + str(rowS[0]) + ' country ' + str(rowS[18]))
        if str(rowS[18]) == '': 
            r = json.loads(requests.get(checkerURL+str(rowS[0])+'?key='+apiKey).text)
            if r["status"] == 'success':
                updateArgs = (r['countryCode'],r['country'],r['region'],r['regionName'],r['city'],r['isp'],r['as'],r['zip'],rowS[0],rowS[1])
                cursor.execute(updateSQL, updateArgs)
                dbRS.commit()
                print('Geolocation of IP %s submitted to DB' % rowS[0])
    printALine()
    print('Perform selection by country? Enter two letter country code (ex. US, if empty all countries will be selected):')
    countryCode = input()
    if len(countryCode) > 0:
        selectSQL += selectSQLadd + countryCode +"')"
        print(selectSQL)
    cursor.execute(selectSQL)
    result = cursor.fetchall()
    csvList = [['IP','Port','login:pass','Device','VPN Type','VPN login:pass','DDNS URL','DDNS RegData','Notes','isVPN','VPN error','NotAccessible','need Setup','AP/brige mode','Country']]
    for selectedRaw in result:
        if selectedRaw[30] == 'null': selectedRaw[30] = ''
        csvList.append(['="'+str(selectedRaw[0])+'"',selectedRaw[1],selectedRaw[2],selectedRaw[3],'','',selectedRaw[30],'','','','','','','',selectedRaw[18]])
    print('Outputting devices info into workList.csv file...')
    with open(outputCSV, "w", newline="") as file:
        writer = csv.writer(file, delimiter =';' )
        writer.writerows(csvList)
    cursor.close()
    dbRS.close()
    print('Done! Check data in the file workList.csv in current directory')
    return

def submitVpnRoutersDataToDB():           # запись в базу обработанных записей о роутерах 
                                            # - в основной таблице SCANRESS помечаются записи успешно обработанные
                                            # - в таблицу VPNROUTERS записываются исключительно рабочие роутеры для дальнейшей продажи
    csvFile = 'dataReady.csv'
    print("Input Data will be taken from 'dataReady.csv' file from current directory. You can get an error in case this file is not exist")
    updateSCANRESSQuery = "UPDATE SCANRESS SET TAKEN = 1, VPNTYPE = %s, VPNLOGPASS = %s, DDNSURL = %s, DDNSREGDATA = %s, NOTES = %s, ISVPN = %s, VPNERROR = %s, NOTACCESSIBLE = %s, NEEDSETUP = %s, APBRIDGE = %s WHERE IP = %s AND PORT = %s"
    selectSCANRESSQuery = "SELECT CountryCode, Country, Region, RegionName, City, ISP, ASCode, ZIP FROM SCANRESS WHERE IP = %s AND PORT = %s"
    selectVPNROUTERSQuery = "SELECT IPADDR FROM VPNROUTERS WHERE IPADDR = '%s'"
    inserVPNROUTERSQuery = "INSERT INTO VPNROUTERS (IPADDR, PORT, LOGPASS, DEVICE, VPNTYPE, VPNLOGPASS, DDNSURL, DDNSREGDATA, NOTES, CountryCode, Country, Region, RegionName, City, ISP, ASCode, ZIP, OVPNCONFIG, ipqualityscore, getipintel) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    updateVPNROUTERSQuery = "UPDATE VPNROUTERS SET PORT = %s, LOGPASS = %s, DEVICE = %s, VPNTYPE = %s, VPNLOGPASS = %s, DDNSURL = %s, DDNSREGDATA = %s, NOTES = %s, CountryCode = %s, Country = %s, Region = %s, RegionName = %s, City = %s, ISP = %s, ASCode = %s, ZIP = %s, OVPNCONFIG = %s, ipqualityscore = %s, getipintel = %s WHERE IPADDR = %s"
    setOfMissedConfigFiles = []
    print('Connecting to online DataBase.... Please Wait....')
    dbRS = mysql.connector.connect(
        user = dbUserName,
        password = dbPassword,
        host = dbServerAddress,
        database = dbDBName)
    cursor = dbRS.cursor()

    with open(csvFile, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';')
        for row in csv_reader:
            if ((row["VPN Type"] != '') or (row["VPN login:pass"] != '') or (row["DDNS URL"] != '') or (row["DDNS RegData"] != '') or (row["Notes"] != '') or (row["isVPN"] != '') or (row["VPN error"] != '') or (row["NotAccessible"] != '') or (row["need Setup"] != '') or (row["AP/brige mode"] != '')):
                updateArgs = (row["VPN Type"], row["VPN login:pass"], row["DDNS URL"], row["DDNS RegData"], row["Notes"], row["isVPN"], row["VPN error"], row["NotAccessible"], row["need Setup"], row["AP/brige mode"], row["IP"], row["Port"])
                print(updateSCANRESSQuery % updateArgs)
                cursor.execute(updateSCANRESSQuery, updateArgs)  # записываем в базу в основную таблицу данные по роутерам из csv файла
                dbRS.commit()
                if row["isVPN"] != '':
                    selectArgs = (row["IP"], row["Port"])
                    print(selectSCANRESSQuery % selectArgs)
                    cursor.execute(selectSCANRESSQuery, selectArgs)   # берем из базы запись с данными адреса для последующей записи ее в таблицу VPNROUTERS
                    result = cursor.fetchone()
                    print(result)
                    config_data_file = '' 
                    if row["VPN Type"] == "OpenVPN":
                        try:
                            print("reading config file /cfg/%s.ovpn" % row["IP"])
                            config_data_file = open(workDirecory+"/cfg/"+row["IP"]+".ovpn", 'rb').read() # читаем файл конфига 
                        except:
                            print("There happened an error reading file %s.ovpn" % row["IP"])
                            print("please prepare correct config file, put it in /cfg/ directory (in current dir) and import %s IP once more" % row["IP"])
                            setOfMissedConfigFiles.append(row["IP"])
                    selectArgs = (str(row["IP"]))
                    selectVPNROUTERSQuery1 = selectVPNROUTERSQuery % str(row["IP"])
                    print(selectVPNROUTERSQuery1)
                    cursor.execute(selectVPNROUTERSQuery1) # проверяем есть ли такой айпи 
                    if len(cursor.fetchall()) == 0:                     # если нет добавляем новую запись
                        insertArgs = (row["IP"], row["Port"], row["login:pass"], row["Device"], row["VPN Type"], row["VPN login:pass"], row["DDNS URL"], row["DDNS RegData"], row["Notes"], result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], config_data_file, getIPQualityScore(row["IP"]), getGetIpIntel(row["IP"]))
    #                   print(inserVPNROUTERSQuery % insertArgs)
                        cursor.execute(inserVPNROUTERSQuery, insertArgs)
                        print(row["IP"]+ " successfully inserted into table VPNROUTERS")
                    else:                                             # если есть обновояем данные в записи - так можно заменить пароль от роутера и любые другие данные кроме айпи, так же при этом запишутся свежие значения чекеров риск и фрауд скора
                        updateArgs = (row["Port"], row["login:pass"], row["Device"], row["VPN Type"], row["VPN login:pass"], row["DDNS URL"], row["DDNS RegData"], row["Notes"], result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], config_data_file, getIPQualityScore(row["IP"]), getGetIpIntel(row["IP"]), row["IP"])
    #                    print(updateVPNROUTERSQuery % updateArgs)
                        cursor.execute(updateVPNROUTERSQuery, updateArgs)
                        print(row["IP"]+ " successfully updated in table VPNROUTERS")
                    dbRS.commit()
    cursor.close()
    dbRS.close()
    print("All data added to database")
    if len(setOfMissedConfigFiles) > 0:
        print("Some OpenVPN configuration files was not found in directory /cfg/ in current dir")
        print("here the list of them:", setOfMissedConfigFiles)
        print("Add those files to /cfg/ folder in current dir and resubmit data of those IP's once more")
    return

def getVPNRoutersListForEdit():         # получение из базы списка VPN для редактирования
    
    selectSQL = "SELECT * FROM VPNROUTERS WHERE "
    outputVPNsFile = workDirecory + '/workListEdit.csv'

    print()
    printALine()
    while True:
        print()
        print('Choice by IP or Geolocation')
        print('Enter 1 if you want to choose VPNs by IPs or 2 if by some other criteria (country, state) or 3 for all VPNs in database')
        ii = input()
        if ii == '1':
            print('Enter the filename with list of IPs (name only in case file in current working directory, otherwise input full path)')
            try:
                ipsFileList=open(input(),'r')
            except:
                print('error when opening metioned file. Start again ')
                continue
            i = 0
            for line in ipsFileList:
                if line.strip() != '': 
                    if i == 0:
                        selectSQL += "(IPADDR = '" + line.strip() + "' OR OLDIP = '" + line.strip() + "'"
                    else: 
                        selectSQL += " OR IPADDR = '" + line.strip() + "' OR OLDIP = '" + line.strip() + "'"
                i += 1 
            selectSQL += ")"
            break
        if ii == '2':
            while True:
                print('Enter two-letter country code')
                cc = input()
                if len(cc) > 2:
                    print('Input error. You have to enter two letters only')
                    continue
                selectSQL += "(CountryCode = '" + cc + "'"
                break                
            while True:
                print("Enter two-letter state code. In case you don't want select state just press Enter and all states will be selected")
                rn = input()
                if len(rn) == 0:
                    break
                if len(cc) > 2:
                    print('Input error. You have to enter two letters only')
                    continue
                selectSQL += " AND Region = '" + rn + "'"
                break    
            selectSQL += ")"            
            break
        if ii == '3':
            break
        print('Input 1 or 2 or 3 only')
    while True:
        print()
        print('Choice by Sold or not:')
        print('Input 1 if you want to get unsold VPNs or input 2 if you want to het sold VPNs, or input 3 in case you want to get all VPNs')
        ii = input()
        if ii == '1':
            if selectSQL[-1] == ' ':
                selectSQL += "SOLD = 0"
            else:
                selectSQL += " AND SOLD = 0"
            break
        if ii == '2':
            if selectSQL[-1] == ' ':
                selectSQL += "SOLD = 1"
            else:
                selectSQL += " AND SOLD = 1"
            break
        if ii == '3':
            break    
        print('Input 1 or 2 or 3 only')
    if selectSQL[-1] == ' ':
        selectSQL = selectSQL[:-7]
    print(selectSQL)
    print('Connecting to online DataBase.... Please Wait....')
    dbRS = mysql.connector.connect(
        user = dbUserName,
        password = dbPassword,
        host = dbServerAddress,
        database = dbDBName)
    cursor = dbRS.cursor()
    cursor.execute(selectSQL)
    result = cursor.fetchall()
    csvList = [['IP','Port','login:pass','Device','VPN Type','VPN login:pass','DDNS URL','DDNS RegData','Notes','CountryCode','Country','Region','RegionName','City','ISP','ASCode','ZIP','ipquality_score','getipintel_score','Sold','Byer','SellLink','SellDate','OldIP','IsVPNDead','isWebLoginDead','RawID']]
    for sRaw in result:
        # sRaw[17] - blob with config, sRaw[23] - sells num
        csvList.append(['="'+str(sRaw[0])+'"',sRaw[1],sRaw[2],sRaw[3],sRaw[4],sRaw[5],sRaw[6],sRaw[7],sRaw[8],sRaw[9],sRaw[10],sRaw[11],sRaw[12],sRaw[13],sRaw[14],sRaw[15],sRaw[16],sRaw[18],sRaw[19],sRaw[20],sRaw[21],sRaw[22],sRaw[23],sRaw[25],sRaw[26],sRaw[27],sRaw[28]])
        if sRaw[4] == 'OpenVPN':
            if len(sRaw[17]) == 0:
                print('OpenVPN IP ' + sRaw[0] + ' do not have a proper config in database')
            else:
                writeTheFile(str(sRaw[17]), workDirecory + '/cfg/' + sRaw[0] + '.ovpn')
    print('Outputting devices info into workListEdit.csv file...')
    with open(outputVPNsFile, "w", newline="") as file:
        writer = csv.writer(file, delimiter =';' )
        writer.writerows(csvList)
    cursor.close()
    dbRS.close()
    print('Done! Check data in the file workListEdit.csv in current directory')
    return

def createList4Sells():                  # выборка с базы данных для формирования списка продаж
    print('Connecting to online DataBase.... Please Wait....')
    dbRS = mysql.connector.connect(
        user = dbUserName,
        password = dbPassword,
        host = dbServerAddress,
        database = dbDBName)
    cursor = dbRS.cursor()

    print()

    print('Here we go...')
    print("Let's choose what you need today...")
    print("Start with country choose - input 2-letter country code or 'All' for all countries")
    countryCode = input()
    if (len(countryCode) < 2) or ((len(countryCode)) < 2 and (countryCode != 'All')):
        print('Wrong Input, dude... going back to menu...')
        return
    if countryCode == 'All':
        countryCode = ''
    if countryCode != '':
        print()
        print("Now let's choose a state/region - input 2-letter state/region code or 'All' for all regions/states")
        regionCode = input()
        if (len(regionCode) < 2) or ((len(regionCode)) < 2 and (regionCode != 'All')):
            print('Wrong Input, dude... going back to menu...')
            return
        if regionCode == 'All':
            regionCode = ''
    else:
        regionCode = ''
    print()
    print("Greate job, dude!...")
    print("Now lt's choose type of VPN")
    typeOfVpn = input('Input "PPTP" or "OpenVPN" or "Both" only: ')
    if typeOfVpn not in ("PPTP","OpenVPN","Both"):
        print('Wrong Input, dude... have to input "PPTP" or "OpenVPN" or "Both" only - going back to menu...')
        return
    if typeOfVpn == 'Both':
        typeOfVpn = ''
    print()
    print("Wow, you're input monster, mate... go ahead...")
    print("Now let's choose if you need a VPN that never been sold, or never been sold to exact customer")
    print("Input 1 if you want a list of VPNs that been never sold before")
    print("or")
    print("Input 2 if you want a list of VPNs that been never sold to particular customer")
    soldOrNot = input("1 or 2 only: ")
    if soldOrNot not in ('1','2'):
        print("You are unlucky today. Read more carefully and nex time may be you'll reach your goal.")
        print('Now going back to menu...')
        return
    if soldOrNot == '2':
        customerForChoice = input('Input customer telegram ID (or "SHOP" for shop sells), and you will get alist of VPN that never been sold to him.: ')
            # тут можно поставить проверку на существование такого кастомера в базе
        selectCUSTOMERSQuery = "SELECT TelegramID from CUSTOMERS WHERE TelegramID = '" + customerForChoice + "'"
        cursor.execute(selectCUSTOMERSQuery)
        if cursor.fetchone() == None:
            print("There is no customer with telegramID %s in database" % customerForChoice)
            print('So going back to menu...')
            return
    print()
    print("Yeah, mister champion... next level...")
    print("And finally input the requered getipintel score")
    print("Keep in mind that some records in our database can still contain '-1' as score value, what means it been not tested yet")
    print("So input the maximum desired score value from 0 to 1 (ex. 0.25) or -1 for any value including those that still been not tested")
    getipintelScore = float(input())
    if (int(getipintelScore*100) > 100) or ((int(getipintelScore*100) < 0) and (int(getipintelScore) != -1)):
        print("Wrong input... getipintel score value can't be more than 1 and less than 0")
        print('So going back to menu...')
        return
    # теперь давайте сделаем запрос с выборкой по указаным параметрам
    selectVPNROUTERSQuery = "SELECT * FROM VPNROUTERS WHERE ISVPNDEAD = 0"
    selectQueryParamsList = []
    if countryCode != '':
        selectQueryParamsList.append("CountryCode = '" + countryCode + "'")
    if regionCode != '':
        selectQueryParamsList.append("Region = '" + regionCode + "'")
    if typeOfVpn != '':
        selectQueryParamsList.append("VPNTYPE = '" + typeOfVpn + "'")
    if soldOrNot == '1':
        selectQueryParamsList.append("SOLD = 0")
    elif soldOrNot == '2':
        selectQueryParamsList.append("BYER != '" + customerForChoice + "'")
    if int(getipintelScore) != -1:
        selectQueryParamsList.append("getipintel < '" + str(float(getipintelScore))[:4] + "'")
    for line in selectQueryParamsList:
        selectVPNROUTERSQuery += " AND " + line
    print(selectVPNROUTERSQuery)
    cursor.execute(selectVPNROUTERSQuery)
    result = cursor.fetchall()
    print('Checking deeper in seells...')
    newres = []
    if soldOrNot == '2':
        for selectedRow in result:
            selectSIDESELLSQUery = "SELECT * FROM SIDESELLS INNER JOIN CUSTOMERS ON SIDESELLS.CUSTID = CUSTOMERS.ID WHERE VPNID = %s AND TelegramID = '%s'" % (selectedRow[28],customerForChoice)
            print(selectSIDESELLSQUery)
            cursor.execute(selectSIDESELLSQUery)
            if cursor.fetchone() == None:
                newres.append(selectedRow)
    else:
        newres = result

    outputCSV = 'list4Sell.csv'

    print()
    print("Prining results : ")
    csvList = [['IP','Port','login:pass','Device','VPN Type','VPN login:pass','DDNS URL','DDNS RegData','Notes','Country','State','City','ipqualityscore','getipintel']]
    for selectedRaw in newres:
        csvList.append(['="'+str(selectedRaw[0])+'"',selectedRaw[1],selectedRaw[2],selectedRaw[3],selectedRaw[4],selectedRaw[5],selectedRaw[6],selectedRaw[7],selectedRaw[8],selectedRaw[9],selectedRaw[11],selectedRaw[13],selectedRaw[18],str(selectedRaw[19])])
    print('Outputting devices info into workList.csv file...')
    with open(outputCSV, "w", newline="") as file:
        writer = csv.writer(file, delimiter =';' )
        writer.writerows(csvList)
    cursor.close()
    dbRS.close()
    print('Done! Check data in the file list4Sell.csv in current directory')

    print()
    return

def submitVpnRoutersEdited():      # загрузка в базу списка отредактированных VPN
    csvFile = 'dataEditReady.csv'
    print("Input Data will be taken from 'dataEditReady.csv' file from current directory. You can get an error in case this file is not exist")
    print("Press Enter key to continue")
    input()
    
    updateVPNROUTERSQuery = "UPDATE VPNROUTERS SET IPADDR = %s, PORT = %s, LOGPASS = %s, DEVICE = %s, VPNTYPE = %s, VPNLOGPASS = %s, DDNSURL = %s, DDNSREGDATA = %s, NOTES = %s, CountryCode = %s, Country = %s, Region = %s, RegionName = %s, City = %s, ISP = %s, ASCode = %s, ZIP = %s, OVPNCONFIG = %s, ipqualityscore = %s, getipintel = %s, SOLD = %s, BYER = %s, SELLLINK = %s, SELLDATE = %s, OLDIP = %s, ISVPNDEAD = %s, ISWEBLOGINDEAD = %s WHERE ROWID = %s"
    setOfMissedConfigFiles = []

    print('Connecting to online DataBase.... Please Wait....')
    dbRS = mysql.connector.connect(
        user = dbUserName,
        password = dbPassword,
        host = dbServerAddress,
        database = dbDBName)
    cursor = dbRS.cursor()

    with open(csvFile, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';')
        for row in csv_reader:

            config_data_file = '' 
            if row["VPN Type"] == "OpenVPN":
                try:
                    print("reading config file /cfg/%s.ovpn" % row["IP"])
                    config_data_file = open(workDirecory+"/cfg/"+row["IP"]+".ovpn", 'rb').read() # читаем файл конфига 
                except:
                    print("There happened an error reading file %s.ovpn" % row["IP"])
                    print("please prepare correct config file, put it in /cfg/ directory (in current dir) and import %s IP once more" % row["IP"])
                    setOfMissedConfigFiles.append(row["IP"])

            updateArgs = (row["IP"], row["Port"], row["login:pass"], row["Device"], row["VPN Type"], row["VPN login:pass"], row["DDNS URL"], row["DDNS RegData"], row["Notes"], row["CountryCode"], row["Country"], row["Region"], row["RegionName"], row["City"], row["ISP"], row["ASCode"], row["ZIP"], config_data_file, row["ipquality_score"], row["getipintel_score"], row["Sold"], row["Byer"], row["SellLink"], row["SellDate"], row["OldIP"], row["IsVPNDead"], row["isWebLoginDead"], row["RawID"])
            cursor.execute(updateVPNROUTERSQuery, updateArgs)
            print(row["IP"]+ " successfully updated in table VPNROUTERS")

    if len(setOfMissedConfigFiles) > 0:
        print("Some OpenVPN configuration files was not found in directory /cfg/ in current dir")
        print("here the list of them:", setOfMissedConfigFiles)
        print("Add those files to /cfg/ folder in current dir and resubmit data of those IP's once more")
        print()
    return

def submitSellsFromFile():         # запись в базу только продаж sells.csv (IP;BYER_TG_ID;DATE)
    printALine()
    print()
    print('Submit list of last sells from localfile sells.csv (IP;BYER_TG_ID;DATE)')
    print('in case of sell to vpnshop in the field BYER_TG_ID should be "SHOP" in all other cases telegram ID if customer')
    print('date in field DATE should be in "YY.MM.DD" format')
    print()
    sellsFile = 'sells.csv'
    errorIPs = []
    doubleSellsList = []

    #прочитать содержимое .csv в список
    sellsList = []
    with open(sellsFile, encoding="ISO-8859-1") as csvfile:
        readCSV = csv.reader(csvfile, delimiter=';')
        for row in readCSV:
            if (row[0] == 'IP') or (row[0] == ''): continue
            sellsList.append(row)
    csvfile.close()
    customersList = []
    
    print('Connecting to online DataBase.... Please Wait....')
    dbRS = mysql.connector.connect(
        user = dbUserName,
        password = dbPassword,
        host = dbServerAddress,
        database = dbDBName)
    cursor = dbRS.cursor()

    selectCUSTOMERSQueryTemplate = 'SELECT * FROM CUSTOMERS WHERE TelegramID = '
    inserCUSTOMERSQueryTemplate = 'INSERT INTO CUSTOMERS (TelegramID) VALUES ('
    selectVPNROUTERSQueryTemplate = "SELECT IPADDR, ROWID, SOLD, BYER, SELLDATE, SELLSNUM FROM VPNROUTERS WHERE IPADDR = '%s'"
    # проверяем наличие покупателей в списке в базе
    print('проверяем наличие покупателей в списке в базе...')
    for sell in sellsList:
        if sell[1] not in customersList:
            customersList.append(sell[1])
    for customer in customersList:
        selectCUSTOMERSQuery = selectCUSTOMERSQueryTemplate + '"' + customer + '"'
        print(selectCUSTOMERSQuery)
        cursor.execute(selectCUSTOMERSQuery)
        if len(cursor.fetchall()) == 0:
            print(customer + ' - такой клиент в базе данных не найден')
            print('добавляем в базу клиента ' + customer)
            inserCUSTOMERSQuery = inserCUSTOMERSQueryTemplate + '"' + customer + '")'
            print(inserCUSTOMERSQuery)
            cursor.execute(inserCUSTOMERSQuery)
            dbRS.commit()
    # добавляем продажи по одной
    print('начинаем добавлять в базу продажи по одной...')
    for sell in sellsList:
        print(sell)
        selectCUSTOMERSQuery = selectCUSTOMERSQueryTemplate + '"' + sell[1] + '"'
        print(selectCUSTOMERSQuery)
        cursor.execute(selectCUSTOMERSQuery)
        result = cursor.fetchone()
        print(result)
        customerID = result[0] # получили ID клиента

        selectVPNROUTERSQuery = selectVPNROUTERSQueryTemplate % str(sell[0])
        print(selectVPNROUTERSQuery)
        cursor.execute(selectVPNROUTERSQuery)
        result = cursor.fetchone()
        if result == None:
            print('IP %s не найдет в базе VPN' % sell[0])
            errorIPs.append(sell[0])
            continue
        print(result)
        vpnID = result[1] # Получили ID впн с указанным IP

        if result[2] == 0: # если никогда не был продан этот IP пишем в основную таблицу
            updateVPNROUTERSQuery = "UPDATE VPNROUTERS SET SOLD = %s, BYER = %s, SELLDATE = %s, SELLSNUM = %s WHERE ROWID = %s" 
            updateVPNROUTERSargs = ('1',sell[1],sell[2],'1',vpnID)
            print(updateVPNROUTERSQuery % updateVPNROUTERSargs)
            cursor.execute(updateVPNROUTERSQuery, updateVPNROUTERSargs)
        else:           # если уже продавался то пишем в отдельную табличку а в VPNROUTERS прибавляем 1 к продажам / 
                        # тут же сначала мы проверим факт того что этот айпи не продавался этому же самому клиенту customerID , sell[1]
            if sell[1] == result[3]:
                printALine()
                print()
                print("!!!!!ATTENSION -> AHTUNG -> SOS -> PAMAGITE!!!!")
                print("VPN with IP " + sell[0] + " been ALREDY SOLD to " + result[3] + " at " +  str(result[4]))
                print("so we cant sell it him again...")
                print()
                doubleSellsList.append(sell[0])
                continue
            cursor.execute('SELECT * FROM SIDESELLS WHERE VPNID = ' + str(vpnID) + ' AND CUSTID = ' + str(customerID))
            if cursor.fetchone() != None:
                printALine()
                print()
                print("!!!!!ATTENSION -> AHTUNG -> SOS -> PAMAGITE!!!!")
                print("VPN with IP " + sell[0] + " been ALREDY SOLD to " + sell[1] + " somedays ago")
                print("so we cant sell it him again...")
                print()
                doubleSellsList.append(sell[0])
                continue
            insertSIDESELLSQuery = 'INSERT INTO SIDESELLS (VPNID, CUSTID, DATE) VALUES (%s, %s, %s)'
            insertSIDESELLSargs = (vpnID, customerID, sell[2])
            print(insertSIDESELLSQuery % insertSIDESELLSargs)
            cursor.execute(insertSIDESELLSQuery, insertSIDESELLSargs)
            updateVPNROUTERSQuery = "UPDATE VPNROUTERS SET SELLSNUM = %s WHERE ROWID = %s" % (result[5]+1, vpnID)
            print('updating SELLSNUM field in VPNROUTERS table')
            print(updateVPNROUTERSQuery)
            cursor.execute(updateVPNROUTERSQuery)
        dbRS.commit()
    
    if len(errorIPs) > 0:
        printALine()
        print()
        print("Приведенные ниже айпи не найдены в базе в таблице VPNROUTERS, а следовательно не могут быть проданы")
        print(errorIPs)
    if len(doubleSellsList) > 0:
        printALine()
        print()
        print("Приведенные ниже айпи были уже ранее проданы тем же самым клиентам - продажа одному клиенту одного и того же айпи дважды невозможна")
        print(doubleSellsList)
    printALine()
    print()
    return

def toolsMenuCheckScores():        # проверка скора по getipintel и ipqualityscore - из за ограничений getipintel проверяются только 6 адресов с одного IP дальше бан навечно и надо ставить новый впн или прокси
    print()
    print('here we will check the Database if there any VPN without score (getipintel and ipqualityscore')
    print('Connecting to online DataBase.... Please Wait....')
    dbRS = mysql.connector.connect(
        user = dbUserName,
        password = dbPassword,
        host = dbServerAddress,
        database = dbDBName)
    cursor = dbRS.cursor()
    selectQuery = "SELECT ROWID, getipintel, ipqualityscore, IPADDR FROM VPNROUTERS WHERE getipintel = '-1' or ipqualityscore = '-1'"
    updateQuery = "UPDATE VPNROUTERS SET ipqualityscore = %s, getipintel = %s WHERE ROWID = %s"
    cursor.execute(selectQuery)
    result = cursor.fetchall()
    for sRaw in result:
        gIPis = sRaw[1]
        iPqs = sRaw[2]
        if sRaw[1] == '-1':
            gIPis = getGetIpIntel(sRaw[3])
            if gIPis == '-1':
                print()
                print("your IP been banned by getipintel.net website. to continue you have to change thi IP. Exiting...")
                break
        if sRaw[2] == '-1':
            iPqs = getIPQualityScore(sRaw[3])
        updateArgs = (iPqs, gIPis, sRaw[0])
        print(updateQuery % updateArgs)
        cursor.execute(updateQuery, updateArgs)
    cursor.close()
    dbRS.close()
    print()
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
        sm2res = subMenu2()
        if sm2res == '0':
            break
        elif sm2res == '1':
            addNewDataFromRS()
        elif sm2res == '2':
            getVpnRoutersRawDataFromDB()
        elif sm2res == '3':
            submitVpnRoutersDataToDB()
        elif sm2res == '4':
            print('Here will be some more functions later...')
    return 

def subMenu3execution():
    while True:
        sm3res = subMenu3()
        if sm3res == '0':
            break
        elif sm3res == '1':
            getVPNRoutersListForEdit()
        elif sm3res == '2':
            submitVpnRoutersEdited()
        elif sm3res == '3':
            print('Here will be some more functions later...')
        elif sm3res == '4':
            print('Here will be some more functions later...')
    return 

def subMenu4execution():
    while True:
        sm4res = subMenu4()
        if sm4res == '0':
            break
        elif sm4res == '1':
            createList4Sells()
        elif sm4res == '2':
            submitSellsFromFile()
        elif sm4res == '3':
            print('Here will be some more functions later...')
        elif sm4res == '4':
            print('Here will be some more functions later...')
    return 

def subMenu9execution():
    while True:
        sm9res = subMenu9()
        if sm9res == '0':
            break
        elif sm9res == '1':
            toolsMenuCheckScores()
        elif sm9res == '2':
            print('Here will be some more functions later...')
        elif sm9res == '3':
            print('Here will be some more functions later...')
        elif sm9res == '4':
            print('Here will be some more functions later...')
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
        subMenu3execution()
    elif mmres == '4':
        subMenu4execution()
    elif mmres == '9':
        subMenu9execution()
    else:
        print('Wrong input')


print('Bye bye, Neo')
printALine()

