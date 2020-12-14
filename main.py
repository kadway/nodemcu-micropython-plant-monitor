try:
    import usocket as socket
except:
    import socket

import gc

gc.collect()

import spi_class
import json
import time
import micropython

# instantiate the spi_class
spi_object = spi_class.Stm32Spi()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(('', 80))
s.listen(5)

while True:
    #micropython.mem_info()
    conn, addr = s.accept()
    request = conn.recv(1024)
    req = str(request)

    if request == b'set_general_config' or request == b'set_area_config':
        #try:
        bytes = b''
        data = bytes
        while True:
            data = conn.recv(536)
            if len(data) <= 0:
                break
            bytes += data
        print("".join("0x%02x " % i for i in bytes))
        #data_loaded = json.loads(bytes.decode('utf-8'))  # data loaded
        ##spi_object.send_command(request)
        #spi_object.send_data(data_loaded)

    else:
        #re-send command until a valid num of elements is received
        while 0 == spi_object.nElements or spi_object.nElements > 500000:
            spi_object.send_command(request)
            time.sleep_ms(100)  # sleep 100 msec

        while spi_object.nElements > 0:
            print("Elements left: " + str(spi_object.nElements))
            spi_object.get_data()
            try:
                dataToSend = json.dumps(spi_object.default_commands[request][2])  # data serialized
                conn.sendall(dataToSend.encode('utf-8'))

            except:
                print("Some problem occurred when trying to send data")
                spi_object.reset()
                break

    conn.close()
