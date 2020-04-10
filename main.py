try:
    import usocket as socket
except:
    import socket

import gc
gc.collect()

from machine import Pin, SPI
from spitest import test
# from web import web_page
import web
import ubinascii
import time
# configure spi
spi = SPI(-1, baudrate=200000, polarity=0, phase=0, bits=8, firstbit=SPI.MSB, sck=Pin(0), mosi=Pin(2), miso=Pin(4))
spi.init(baudrate=200000)  # set the baudrate

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

data_out = bytearray(b'\x00')    # initialize to zero
data_in = bytearray(b'\x00')    # initialize to zero
c_List = bytearray(b'\xBA')  # list command from master to slave
ackMaster = bytearray(b'\xE3')  # ack from master to slave
ackSlave = bytearray(b'\xCE')  # ack byte from slave
status = bytearray(b'\x00')  # initialize to zero
dummy = bytearray(b'\xAA')  # dummy byte
prev_command = bytearray(b'\x00') # initialize to zero
i = 0
while True:
    conn, addr = s.accept()
    #print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    request = str(request)
    print('Content = %s' % request)

    if request.find('/?spitest=now') == 6:
        i += 1
        print('\nSpi test {} ...'.format(i))
        spi.write_readinto(c_List, status)
        time.sleep_ms(100)  # sleep 10 msec
        command_text = str(hex(c_List[0]))
        status_text = str(hex(status[0]))
        print("Master: " + command_text)
        print("Slave: " + status_text)
        #send master ack and get data size
        if status == ackSlave:
            spi.write_readinto(ackMaster, status)
            time.sleep_ms(100)  # sleep 10 msec
            if status[0] > 0: #data size is not zero -> continue
                command_text = str(hex(ackMaster[0]))
                status_text = str(hex(status[0]))
                print("Master: " + command_text)
                print("Slave: " + status_text)
                size = int(status[0])
                #prepare buffers size
                new_data_in = bytearray(b"\x00"*size)
                new_data_out = bytearray(b'\x01'*size)

                #send clock to get the data
                spi.write_readinto(new_data_out, new_data_in)
                time.sleep_ms(100)  # sleep 10 msec
                response = web.web_page(str(command_text), str(new_data_in), str(i))
    else:
        response = web.web_page("fail...", "fail...", str(i))

    time.sleep_ms(200)  # sleep 1 sec

    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()
