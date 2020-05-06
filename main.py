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
#spi = SPI(-1, baudrate=200000, polarity=0, phase=0, bits=8, firstbit=SPI.MSB, sck=Pin(0), mosi=Pin(2), miso=Pin(4))
#spi.init(baudrate=200000)  # set the baudrate

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
    #data_loaded = json.loads(request)
    #print("Got command: " + request)
    #if request is not '':
    config = bytearray()
    config_txt = ''
    if request == get_general_conf:
        dict = {}
        config, config_txt = spistm.spiStm32(spi, c_getConf, sleeptime, dict)
        print(dict)
    elif request == get_area_conf:
        dict = {}
        config, config_txt = spistm.spiStm32(spi, c_getArea, sleeptime, dict)
        print(dict)
    #try:
        data_string = json.dumps(dict)  # data serialized
        #print("data_string")
        #print(data_string)
        size = len(data_string)
        print("size " + str(size))
        parts = len(data_string)/536
        print("parts " + str(parts))
        if parts > 1:
            for i in range(int(parts)): #send parts of size 536
                bytes_sent = conn.send(data_string[i*536:(i+1)*536])
                print(str(i) + "\n" + data_string[i*536:(i+1)*536])
                size -= 536
            if(size > 0): #send the rest
                print("size " + str(size) + "idx: " + str(int(parts)*536) + "length: " + str(len(data_string)))
                bytes_sent = conn.send(b'The end')#data_string[int(parts)*536:])
                #print("\nsize>0" + data_string[int(parts)*536:])
            print("sent " + str(bytes_sent) + " bytes")
        elif size <= 536: #send everything at once
            bytes_sent = conn.send(data_string)
            print("\nsize<536\n" + data_string)
        else:
            print("something is wrong!")
            #print("sent " + str(bytes_sent) + " bytes")
        conn.close()

    #except:
        print("Some problem occurred when trying to send response")
        #print("sent " + str(bytes_sent) + " bytes")


