
def writeTheFile(data, filename):     #запись данных из блоб-поля в файл
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
    #    file.write(bytes(data))  # encoding="ISO-8859-1" , encoding='UTF-8'
    #    file.write(bytes(data, encoding='UTF-8'))   # вот так для Diego
        file.write(data)                             # а так для меня
        file.close()
    return