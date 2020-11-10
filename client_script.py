#!/usr/bin/env python3

import socket
import json
import os

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

    #file name for json data dump or load
    filename = str(options[int(user_input)])
    filename = "data/" + filename[2:-1] + ".json"


    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(options[int(user_input)])

        if int(user_input) < 4:
            bytes = b''
            data = bytes
            if os.path.exists(filename):
                os.remove(filename)

            try:
                while True:
                    data = s.recv(536)
                    if len(data) <= 0:
                        break
                    bytes += data
                    #print("----- DATA IN -----\n " + bytes.decode('utf-8') + "\n-----         -----\n")
                with open(filename, 'w') as f:
                    json.dump(bytes.decode('utf-8'), f, indent=4)
                print("\nCommand done!\n")
            except socket.error:
                print("Error receiving data: %s" % socket.error)
        else:
            with open(filename, 'r') as f:
                dict_data = json.load(f)

            dataToSend = json.dumps(dict_data)  # data serialized
            print(dataToSend.encode('utf-8'))
            nBytesToSend = len(dataToSend)
            nParts = nBytesToSend / 536
            if nParts > 1:
                for i in range(int(nParts)):  # segment max size is 536
                    s.send(dataToSend[i * 536:(i + 1) * 536])
                    nBytesToSend -= 536
                if nBytesToSend > 0:  # send the rest
                    s.send(dataToSend[int(nParts) * 536:])
            elif nBytesToSend <= 536:  # send everything at once
                s.sendall(dataToSend.encode('utf-8'))
