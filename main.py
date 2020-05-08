try:
    import usocket as socket
except:
    import socket

import gc

gc.collect()

from machine import Pin, SPI
# from web import web_page
import web
import ubinascii
import time
import spistm
from definitions import *
import json

# configure spi
# spi = SPI(-1, baudrate=200000, polarity=0, phase=0, bits=8, firstbit=SPI.MSB, sck=Pin(0), mosi=Pin(2), miso=Pin(4))
# spi.init(baudrate=200000)  # set the baudrate

# configure HW spi
spi = SPI(1, baudrate=40000000, polarity=0, phase=0)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(('', 80))
s.listen(5)

sleeptime = 1
i = 0

while True:
    conn, addr = s.accept()
    request = conn.recv(1024)
    req = str(request)
    print(req)
    # data_loaded = json.loads(request)
    # print("Got command: " + request)
    # if request is not '':
    config = bytearray()
    config_txt = ''

    dict_data = {}
    if request == b'set_general_config' or request == b'set_area_conf':
        #try:
        bytes = b''
        data = bytes
        while True:
            data = conn.recv(536)
            if len(data) <= 0:
                break
            bytes += data
        data_loaded = json.loads(bytes.decode('utf-8'))  # data loaded
        print(data_loaded)
        #except:
        #    print("Some problem occurred when trying to receive data")

    else:
        config, config_txt = spistm.spiStm32(spi, defaultCommands[request], sleeptime, dict_data)
        try:
            dataToSend = json.dumps(dict_data)  # data serialized
            nBytesToSend = len(dataToSend)
            nParts = nBytesToSend / 536
            if nParts > 1:
                for i in range(int(nParts)):  # segment max size is 536
                    conn.send(dataToSend[i * 536:(i + 1) * 536].encode('utf-8'))
                    nBytesToSend -= 536
                if nBytesToSend > 0:  # send the rest
                    conn.sendall(dataToSend[int(nParts) * 536:].encode('utf-8'))
            elif nBytesToSend <= 536:  # send everything at once
                conn.sendall(dataToSend.encode('utf-8'))
        except:
            print("Some problem occurred when trying to send data")

    conn.close()
