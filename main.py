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

# configure spi
#spi = SPI(-1, baudrate=200000, polarity=0, phase=0, bits=8, firstbit=SPI.MSB, sck=Pin(0), mosi=Pin(2), miso=Pin(4))
#spi.init(baudrate=200000)  # set the baudrate
# configure HW spi
spi = SPI(1, baudrate=40000000, polarity=0, phase=0)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

data_out = bytearray(b'\x00')    # initialize to zero
data_in = bytearray(b'\x00')    # initialize to zero
c_getConf = bytearray(b'\xAA')  # list command from master to slave
c_getArea = bytearray(b'\xBA')  # list command from master to slave
ackMaster = bytearray(b'\xE3\xE3\xE3\xE3')  # ack from master to slave
ackSlave = bytearray(b'\xCE')  # ack byte from slave
status = bytearray(b'\x00')  # initialize to zero
dummy = bytearray(b'\xAA')  # dummy byte
prev_command = bytearray(b'\x00') # initialize to zero
sleeptime = 300
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
            command_text = str(hex(c_getConf[0]))
            config, config_txt = spistm.spiStm32(spi, c_getConf,sleeptime)
            #response = web.web_page(command_text, config_txt, str(i))
        elif request.find('/?spitest2=now') == 6:
            print('\nSpi test {} ...'.format(i))
            i += 1
            command_text = str(hex(c_getConf[0]))
            config, config_txt = spistm.spiStm32(spi, c_getArea,sleeptime)
            #response = web.web_page(command_text, config_txt, str(i))
        else:
            response = web.web_page("fail...", "fail...", str(i))

        time.sleep_ms(sleeptime)  # sleep 1 sec
        response = web.web_page("fail...", "fail...", str(i))
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()
