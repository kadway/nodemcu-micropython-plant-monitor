#!/usr/bin/env python3

import socket
import json
import os
import spi_class_cli

#command definitions
options = (
    b'get_general_config',
    b'get_area_config',
    b'get_adc_data',
    b'get_act_data',
    b'set_general_config',
    b'set_area_config')

HOST = '192.168.1.81'  # The server's hostname or IP address
PORT = 80       # The port used by the server

mylist = []

spi_obj = spi_class_cli.Stm32SpiCli()

while True:

    print("Options:\n"
          "0. get general configuration\n"
          "1. get area configuration\n"
          "2. get adc data\n"
          "3. get actuation data\n"
          "4. set general configuration\n"
          "5. set area configuration\n"
          "Type command number:")
    user_input = input()
    while not (0 <= int(user_input) < 6):
        print(user_input + " is invalid")
        user_input = input()



    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(options[int(user_input)])
        print("Send command: " + str(options[int(user_input)]))
        if int(user_input) < 4:
            bytes = b''
            data = bytes

            try:
                while True:
                    data = s.recv(1024)
                    if len(data) <= 0:
                        break
                    #print("bytes:")
                    bytes += data
                    #print(bytes)
                    #print("----- DATA IN -----\n " + data.decode('utf-8') + "\n-----         -----\n")

                #spi_obj.byteArr = bytes
                #self.c_recv = options[int(user_input)]
                spi_obj.save_data(bytes, options[int(user_input)])

                #mystring=bytes.decode('utf-8').replace("][", ",")
                #mylist=json.loads(mystring)


                print("\nCommand done!\n")
            except socket.error:
                print("Error receiving data: %s" % socket.error)
        else:
            with open(filename, 'r') as f:
                saved_data = json.load(f)

            dataToSend = json.dumps(saved_data)  # data serialized
            print(dataToSend.encode('utf-8'))
            s.sendall(dataToSend.encode('utf-8'))
            #s.sendall(bytearray(b'\x39'*20))

