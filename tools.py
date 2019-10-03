#!/usr/bin/env python
import random
import string
import ftplib
import zipfile
import os
import re
import sys
import socket

def genRandomString(length):  # генерирует и возвращает строку случайных символов заданой длины в нижнем регистре
    rS = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return rS

def genRandomStringUp(length):  # генерирует и возвращает строку случайных символов заданой длины в верхнем регистре
    rS = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return rS

def genRandomStringMix(length):  # генерирует и возвращает строку случайных символов заданой длины
    rS = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=length))
    return rS

def ftpUploadFile(ftp, ftpPath, ftpLogin, ftpPassword, filePath): # загрузка файла на ftp
    ftpFilePath = ''
    fileName = filePath.split('/')[-1]
    i = 0
    while True:
        try:
            print('connecting ftp://' + ftp + ' - try ' + str(i))
            ftpObj = ftplib.FTP(ftp, ftpLogin, ftpPassword, timeout = 10 )
            print(ftpObj)
            print("ftp connected succesfully")
            break
        except:
            i += 1
            if i > 10 : 
                return ''
    print("changing directory...")
    ftpObj.cwd(ftpPath)
    print("directory changed succesfully")
    i = 0
    while True:
        try:
            print("opening file " + filePath)
            f = open(filePath, 'rb')
            print("sending file to ftp...")
            ftpObj.storbinary("STOR "+ filePath, f)
            print("closing ftp connection ...")
            ftpObj.quit()
            f.close()
            ftpFilePath = fileName
            break
        except:
            print("faled to upload %s to ftp" % filePath)
            i += 1
            f.close()
            if i > 10 : 
                return ''
            print("this is try nomber %s, will try again now..." % str(i))
    return ftpFilePath                                            # возвращает путь к файлу на ftp

def zipFiles(filesList = (), nameLen = 32):  # создает во временном каталоге архив с рандомным названием из nameLen-х символов
    zipFilePath = 'tmp/' + genRandomString(nameLen) + '.zip'
    try:
        os.mkdir('tmp')
    except:
        pass
    try: 
        zipFile = zipfile.ZipFile(zipFilePath, 'w', zipfile.ZIP_DEFLATED)
        for f in filesList:
            zipFile.write(f)
        zipFile.close()
    except:
        return ''
    return zipFilePath

# ftpUploadFile('files.000webhost.com','public_html','cryptocashback','qaz1XsW2','workList.csv')

def normalizeOVPNConfig(cfgData, deviceStr = ''):  # приводит конфиг к стандартизованному виду
    caData = []
    certData = []
    keyData = []
    caStart = False
    certStart = False
    keyStart = False
    cfgLines = []
    #print('cfgData is: ', cfgData)
    for line in cfgData:
        #print('current line', line)
        if line.strip() == '<ca>':
            caData.append(line)
            caStart = True
            continue
        if line.strip() == '<cert>':
            certData.append(line)
            certStart = True
            continue
        if line.strip() == '<key>':
            keyData.append(line)
            keyStart = True
            continue
        if line.strip() == '</ca>':
            caData.append(line)
            caStart = False
            continue
        if line.strip() == '</cert>':
            certData.append(line)
            certStart = False
            continue
        if line.strip() == '</key>':
            keyData.append(line)
            keyStart = False
            continue
        if caStart == True:
            caData.append(line)
            continue
        if certStart == True:
            certData.append(line)
            continue
        if keyStart == True:
            keyData.append(line)
            continue
        if ((line[0] == '#') and ((line.find('setenv opt tls-cipher') == -1) and (line.find('dhcp-option') == -1))):
            continue
        if (line.strip() == 'block-outside-dns'):
            continue
        if (line.find('verb') != -1):
            cfgLines.append('verb 4\n')
            continue
        if line.strip() == 'tls-cipher "DEFAULT:@SECLEVEL=0"':
            cfgLines.append('setenv opt tls-cipher "DEFAULT:@SECLEVEL=0"\n')
            continue
        if (line.find('tun-mtu') != -1):
            cfgLines.append('tun-mtu 1500\n')
            continue
        if (line.find('mssfix') != -1):
            if ((deviceStr.find('Belkin') != -1) or (deviceStr.find('ASUS') != -1)):
                cfgLines.append('mssfix 0\n')
            else:
                cfgLines.append('mssfix 1200\n')
            continue

        if line.find('remote ') != -1:
            addr = line[line.find(' ')+1:line.rfind(' ')].strip()
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', addr) != None:
                ipAddr = addr
                cfgLines.append(line)
            else:
                try:
                    ipAddr = socket.gethostbyname(addr)
                    cfgLines.append(line.replace(addr,ipAddr))
                except:
                    print('URL ', addr, 'could not be resolved. check it! ==============  Attencion ===========')
                    cfgLines.append(line)
            continue
            
        if (line.strip() != ''):
            cfgLines.append(line)
    if (deviceStr.find('Belkin') != -1):
        try:
            if (cfgLines.index('dhcp-option DNS 1.1.1.1\n') > -1):
        #        print('this Belkin router already have DNS info in config ---------------')
                pass
        except:
            cfgLines.append('dhcp-option DNS 1.1.1.1\n')
        #    print('here we add DNS info in config ++++++++++++++++')
    if (deviceStr.find('NETGEAR') != -1):
        try:
            if ((cfgLines.index('#setenv opt tls-cipher "DEFAULT:@SECLEVEL=0"\n') > -1) or (cfgLines.index('setenv opt tls-cipher "DEFAULT:@SECLEVEL=0"\n') > -1)):
                pass
        except:
            cfgLines.append('#setenv opt tls-cipher "DEFAULT:@SECLEVEL=0"\n')
    try:
        if (cfgLines.index('setenv opt block-outside-dns\n') > -1):
            pass
    except:
        cfgLines.append('setenv opt block-outside-dns\n')
    try:
        if (cfgLines.index('redirect-gateway def1\n') > -1):
            pass
    except:
        cfgLines.append('redirect-gateway def1\n')
    try:
        if (cfgLines.index('ping-timer-rem\n') > -1):
            pass
    except:
        cfgLines.append('ping-timer-rem\n')
    try:
        if (cfgLines.index('verb 4\n') > -1):
            pass
    except:
        cfgLines.append('verb 4\n')
    try:
        if (cfgLines.index('tun-mtu 1500\n') > -1):
            pass
    except:
        cfgLines.append('tun-mtu 1500\n')
    try:
        if (cfgLines.index('mssfix 1200\n') > -1) or (cfgLines.index('mssfix 0\n') > -1):
            pass
    except:
        cfgLines.append('mssfix 1200\n')
    cfgData = []
    for l in cfgLines: cfgData.append(l)
    for l in caData: cfgData.append(l)
    for l in certData: cfgData.append(l)
    for l in keyData: cfgData.append(l)
    return cfgData