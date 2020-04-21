import time
def spiStm32(spi, command, sleeptime):
    status = bytearray(b'\x00')  # initialize to zero
    ackMaster = bytearray(b'\xE3')  # ack from master to slave
    ackSlave = bytearray(b'\xCE')  # ack byte from slave
    c_getConf = bytearray(b'\xAA')  # list command from master to slave
    c_getArea = bytearray(b'\xBA')  # list command from master to slave
    spi.write_readinto(command, status)
    time.sleep_ms(sleeptime)  # sleep 10 msec
    command_text = str(hex(command[0]))
    status_text = str(hex(status[0]))
    #print("Master: " + command_text)
    #print("Slave: " + status_text)

    config = bytearray()
    config_txt = ''
    if status == ackSlave:
        if command == c_getConf:
            config, config_txt = spiGetBytes(spi, ackMaster, 16, 1, sleeptime)
        elif command == c_getArea:
            if status == ackSlave:
                spi.write_readinto(ackMaster, status) #get number of elements
                time.sleep_ms(sleeptime)  # sleep 10 msec
                if status[0] > 0: #data size is not zero -> continue
                    config, config_txt = spiGetBytes(spi, ackMaster, 22, status[0], sleeptime)
                else:
                   print("slave sent bad element number")
    else:
        print("slave did not ack!")
        config = bytearray(b'\x00')
        config_txt = 'fail'
    return config, config_txt

def spiGetBytes(spi, send, nBytes, nElements, delay):
    recv = bytearray(b'\x00')  # initialize to zero
    config = bytearray()
    config_txt = ''

    for j in range(nElements):
        for i in range(nBytes):
            # expecting 22 bytes of data
            spi.write_readinto(send, recv)
            time.sleep_ms(delay)  # sleep msec
            config += recv
            status_text = str(hex(recv[0]))
           # status_text = str(recv[0])
            config_txt += status_text + " "
            #print("Slave: " + status_text)
    return config, config_txt