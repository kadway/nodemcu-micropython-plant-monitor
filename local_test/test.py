#!/usr/bin/env python3

import socket
import json
from ftfy import fix_text

#command definitions for json socket requests
#command definitions for json socket requests
get_general_conf = b'get_general_config'
set_general_conf = b'set_general_config'
get_area_conf = b'get_area_conf'
set_area_conf = b'set_area_conf'
get_adc_data = b'get_adc_data'
get_act_data = b'get_act_data'

HOST = '192.168.1.12'  # The server's hostname or IP address
PORT = 80       # The port used by the server
while True:
    print("Options:\n1. get general conf\n2. set general conf\n3. get area conf\nType command number:")
    string = input()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #s.setsockopt(socket.IPPROTO_TCP, socket.TCP_MAXSEG, 536)
        s.connect((HOST, PORT))
        if string == "1":
            command = get_general_conf  # data serialized
            s.sendall(command)
        elif string == "3":
            command = get_area_conf  # data serialized
            s.sendall(command)
        bytes = b''
        data = bytes
        try:
            while True:
                data = s.recv(4096)
                if data <= 0:
                    break
                bytes.append(data)

            print(data)
            print("size is " + str(len(data)))
        #fix_data = fix_text(data)
        #for item in data_loaded:
        #    print(item)
        except:
            #data_loaded = json.loads(data)  # data loaded
            print("except!")
            print(data)
            print("size is " + str(len(data)))
            #print(data_loaded)

    #print("Got data:")
    #print(data)
