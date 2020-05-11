#!/usr/bin/env python3

import socket
import json

#command definitions
options = (
    b'get_general_config',
    b'get_area_conf',
    b'get_adc_data',
    b'get_act_data',
    b'set_general_config',
    b'set_area_conf')
#defaultCommands = {
#    b'get_general_config': bytearray(b'\xAA'),
#    b'get_area_conf': bytearray(b'\xBA'),
#    b'get_adc_data': bytearray(b'\xCA'),
#    b'get_act_data': bytearray(b'\xDA'),
#    b'set_general_config': bytearray(b'\xAB'),
#    b'set_area_conf': bytearray(b'\xBB')
#}

HOST = '192.168.1.12'  # The server's hostname or IP address
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
            try:
                while True:
                    data = s.recv(536)
                    if len(data) <= 0:
                        break
                    bytes += data

                data_loaded = json.loads(bytes.decode('utf-8'))  # data loaded
                print(data_loaded)

                with open(filename, 'w') as f:
                    json.dump(data_loaded, f, indent=4)

            except socket.error:
                print("Error receiving data: %s" % socket.error)
        else:
            with open(filename, 'r') as f:
                dict_data = json.load(f)
        #    try:
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
            #except:
            #    print("Some problem occurred when trying to send response")
        #except:

        #    print("except!")
        #    print(data)
        #    print("size is " + str(len(data)))
        #    print(bytes)
            #print(data_loaded)

    #print("Got data:")
    #print(data)