try:
    import usocket as socket
except:
    import socket

import gc

gc.collect()

import spi_class
import json

# instantiate the spi_class
spi_object = spi_class.Stm32Spi()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(('', 80))
s.listen(5)

while True:
    conn, addr = s.accept()
    request = conn.recv(1024)
    req = str(request)
    print(req)
    # data_loaded = json.loads(request)
    # print("Got command: " + request)
    # if request is not '':

    if request == b'set_general_config' or request == b'set_area_config':
        #try:
        bytes = b''
        data = bytes
        while True:
            data = conn.recv(536)
            if len(data) <= 0:
                break
            bytes += data
        data_loaded = json.loads(bytes.decode('utf-8'))  # data loaded
        print(data_loaded)
        #except:
        #    print("Some problem occurred when trying to receive data")

    else:
        #config, config_txt = spistm.spiStm32(spi, defaultCommands[request], sleeptime, dict_data)
        spi_object.send_command(request)
        while spi_object.nElements > 0:
            spi_object.get_data(10)
            try:
                dataToSend = json.dumps(spi_object.default_commands[request][2])  # data serialized
                nBytesToSend = len(dataToSend)
                nParts = nBytesToSend / 536
                if nParts > 1:
                    for i in range(int(nParts)):  # segment max size is 536
                        conn.send(dataToSend[i * 536:(i + 1) * 536].encode('utf-8'))
                        nBytesToSend -= 536
                    if nBytesToSend > 0:  # send the rest
                        conn.sendall(dataToSend[int(nParts) * 536:].encode('utf-8'))
                elif nBytesToSend <= 536:  # send everything at once
                    conn.sendall(dataToSend.encode('utf-8'))
            except:
                print("Some problem occurred when trying to send data")

    conn.close()
