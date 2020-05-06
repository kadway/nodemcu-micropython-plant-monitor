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
    request = str(request)
    print(request)
    if request is not '':
        config = bytearray()
        config_txt = ''
        if request.find('/?spitest1=now') == 6:
            i += 1
            print('\nSpi test {} ...'.format(i))
            command_text = str(hex(c_getDataAct[0]))
            config, config_txt = spistm.spiStm32(spi, c_getDataAct,sleeptime)
            #response = web.web_page(command_text, config_txt, str(i))
        elif request.find('/?spitest2=now') == 6:
            print('\nSpi test {} ...'.format(i))
            i += 1
            command_text = str(hex(c_getConf[0]))
            config, config_txt = spistm.spiStm32(spi, c_getArea,sleeptime)
            #response = web.web_page(command_text, config_txt, str(i))
        elif request.find('/?spitest3=now') == 6:
            print('\nSpi test {} ...'.format(i))
            i += 1
            command_text = str(hex(c_getDataAdc[0]))
            config, config_txt = spistm.spiStm32(spi, c_getDataAdc, sleeptime)
        elif request.find('/?spitest4=now') == 6:
            print('\nSpi test {} ...'.format(i))
            i += 1
            command_text = str(hex(c_getDataAct[0]))
            config, config_txt = spistm.spiStm32(spi, c_getDataAct, sleeptime)
        else:
            response = web.web_page("fail...", "fail...", str(i))

        time.sleep_ms(sleeptime)  # sleep 1 sec
        response = web.web_page("fail...", "fail...", str(i))
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        try:
            conn.sendall(response)
        except:
            print("Some problem occurred when trying to send response")

        conn.close()
