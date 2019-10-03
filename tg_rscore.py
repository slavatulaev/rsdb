
from telethon import TelegramClient, sync, events
import time

def initTgClient():
    api_id = 571789
    api_hash =  '6f0688b138b3fdf4ee4589b5f19fb3f4'
    phone = '+17072784095'
    username = 'bonniedella'
    password = ''
    session_file = 'bonniedella.session'
    client = TelegramClient(username, api_id, api_hash)
    client.start()
    return client

def getScore(client, ip):
#    print(client.get_me().username)
    myLastMsg = client.send_message('ipscorebot', '/check')
#    print(myLastMsg)
    while(True):
        time.sleep(1)
        messageLast = client.get_messages('ipscorebot')
        if (messageLast[0].id > myLastMsg.id):
#            print('1:', messageLast)
            myLastMsg = client.send_message('ipscorebot', ip)
            break
    while(True):
        time.sleep(1)
        messageLast = client.get_messages('ipscorebot', limit=4)
        if (messageLast[2].text.find('**IP Score:**') != -1):
            print('"' + ip + '"' + ';"' + messageLast[2].text[17:messageLast[2].text.find(' |')] + '"\n')
            score = messageLast[2].text[17:messageLast[2].text.find(' |')]
            break
        if (messageLast[3].text.find('**IP Score:**') != -1):
            print('"' + ip + '"' + ';"' + messageLast[3].text[17:messageLast[3].text.find(' |')] + '"\n')
            score = messageLast[3].text[17:messageLast[3].text.find(' |')]
            break
    return score