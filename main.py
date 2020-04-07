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
command = bytearray(b'\xBA')  # list command from master to slave
ackMaster = bytearray(b'\xE3')  # ack from master to slave
ackSlave = bytearray(b'\xCE')  # ack byte from slave
status = bytearray(b'\x00')  # initialize to zero
dummy = bytearray(b'\xAA')  # dummy byte
prev_command = bytearray(b'\x00') # initialize to zero

while True:
    conn, addr = s.accept()
    #print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    request = str(request)
    #print('Content = %s' % request)
    refresh = request.find('/?refresh=now')
    #if refresh == 6:
    #    print('refresh')

    # send command for slave to list data
    if prev_command != command:
        spi.write_readinto(command, status)
        prev_command = command
        print("Master sent list command: " + str(command))
        time.sleep_ms(500)  # sleep 500 msec

    if status[0] > 0:
        print("Slave data incoming: " + str(status))

        if status == ackSlave and prev_command == command: # got ackByte from slave
            print("Data is Ack. Master will send Ack and get data size")
            #time.sleep_ms(500)  # sleep 500 msec
            #  write master ack and receive data size
            spi.write_readinto(ackMaster, status)
            prev_command = ackMaster
            #time.sleep_ms(500)  # sleep 500 usec
        elif status != ackSlave and prev_command == ackMaster: #size of data is > 0 so prepare buffer sizes
                print("Slave data size: " + status[0])
                size = int(status[0])
                new_data_in = bytearray(b"\x00"*size)
                new_data_out = bytearray(b'\x00'*size)

                #send clock to get the data
                spi.write_readinto(new_data_out, new_data_in)

                #restart sequence
                prev_command = bytearray(b'\x00')

                if new_data_in[0] > 0:
                    print("Dummy out " + str(new_data_out))
                    print("Incoming data " + str(new_data_in))
                    data_out = new_data_out
                    data_in = new_data_in
                else:
                    print("Master sent clock but not data was received from slave")

        else:
            print("Ups lost in sequence.. Try to restart...")
            prev_command = bytearray(b'\x00')
    else:
        print("No data from slave!")
        prev_command = bytearray(b'\x00')

    time.sleep(1)  # sleep 1 sec


    response = web.web_page(data_out.decode("utf-8"), data_in.decode("utf-8"))
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()
