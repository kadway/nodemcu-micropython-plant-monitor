#!/usr/bin/env python3

import socket
import time
import spi_class_cli

#command definitions
options = (
    b'get_general_config',
    b'get_area_config',
    b'get_adc_data',
    b'get_act_data',
    b'set_general_config',
    b'set_area_config',
    b'clear_log',
    b'reset')

HOST = '192.168.1.81'  # The server's hostname or IP address
PORT = 80       # The port used by the server

spi_obj = spi_class_cli.Stm32SpiCli()

while True:

    print("Options:\n"
          "0. get general configuration\n"
          "1. get area configuration\n"
          "2. get adc data\n"
          "3. get actuation data\n"
          "4. set general configuration\n"
          "5. set area configuration\n"
          "6. clear log\n"
          "7. reset STM\n"
          "Type command number:")
    user_input = input()
    while not (0 <= int(user_input) < 8):
        print(user_input + " is invalid")
        user_input = input()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(options[int(user_input)])
        # In the first socket send, want only to send the command bytes, add a delay to prevent additional data being sent together
        time.sleep(1)
        print("\nCommand selected: " + str(options[int(user_input)]))

        # Option for receiving data from MCU
        if int(user_input) < 4:
            bytes = b''
            data = bytes
            try:
                while True:
                    data = s.recv(1024)
                    if len(data) <= 0:
                        break
                    bytes += data

                if len(bytes)>0:
                    spi_obj.save_data(bytes, options[int(user_input)])
                    print("\nCommand done!\n")
                else:
                    print("Error: no data received from ESP\n")
            except socket.error:
                print("Error receiving data: %s" % socket.error)

        # Option for sending data to MCU
        elif int(user_input) < 6:
            bytes_to_send = spi_obj.load_data(options[int(user_input)])
            if bytes_to_send != b'\x01':
                s.sendall(bytes_to_send)
                print("\nCommand done!\n")
            else:
                print("The command " + options[int(user_input)].decode() + " failed!\n ")
        else:
            print("\nCommand done!\n")
        s.close()