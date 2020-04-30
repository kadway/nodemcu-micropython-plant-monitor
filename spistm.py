import time
from struct import unpack
generalConf = {}
areaConf = {}

def spiStm32(spi, command, sleeptime):
    status = bytearray(b'\x00')  # initialize to zero
    dummyByte = bytearray(b'\x00')
    nElementsByte = bytearray(b'\x00\x00\x00\x00') # initialize to zero
    ackMaster = bytearray(b'\xE3\xE3\xE3\xE3')  # ack from master to slave
    ackSlave = bytearray(b'\xCE')  # ack byte from slave
    c_getConf = bytearray(b'\xAA')  # list command from master to slave
    c_getArea = bytearray(b'\xBA')  # list command from master to slave
    confSize = 20
    areaSize = 48
    spi.write_readinto(command, status)
    time.sleep_ms(sleeptime)  # sleep 10 msec
    command_text = str(hex(command[0]))
    status_text = str(hex(status[0]))
    print("Master: " + command_text)
    print("Slave: " + status_text)

    config = bytearray()
    config_txt = ''
    if status == ackSlave:
        if command == c_getConf:
            print("Get conf")
            byteArr, config_txt = spiGetBytes(spi, confSize, sleeptime)
            # add items to general conf dictionary
            unpack_general_conf(byteArr)
            print(generalConf)
        elif command == c_getArea:
            if status == ackSlave:
                print("Get area")
                spi.write_readinto(ackMaster, nElementsByte) #get number of elements
                time.sleep_ms(sleeptime)  # sleep  msec
                print("".join("0x%02x " % i for i in nElementsByte))
                x = unpack('<HH', nElementsByte)
                nElements = x[0] | x[1] << 16
                if nElements > 0: #data size is not zero -> continue
                    print("area has " + str(nElements) + " elements")
                    for j in range(nElements):
                        byteArr, config_txt = spiGetBytes(spi, areaSize, sleeptime)
                        unpack_area_conf(byteArr, j)
                        #time.sleep_ms(500)  # sleep msec
                    print(areaConf)
                else:
                    print("slave sent bad element number")
    else:
        print("slave did not ack!")
        config = bytearray(b'\x00')
        config_txt = 'fail'
    return config, config_txt

def spiGetBytes(spi, nBytes, delay):
    recv = bytearray(b'\x00'*nBytes)  # initialize to zero
    dummySend = bytearray(b'\x21'*nBytes)  # dummy bytes
    #config = bytearray()
    # expecting nBytes bytes of data
    spi.write_readinto(dummySend, recv)
    time.sleep_ms(delay)  # sleep msec
    bytes_text = "".join("0x%02x " % i for i in recv)
    #print("".join("0x%02x " % i for i in nElements))
    #status_text = str(hex(recv))
    # status_text = str(recv[0])
    #config_txt += status_text + "\n"
    print("Slave: " + bytes_text)
    return recv, bytes_text

def unpack_general_conf(byteArr):
    x = unpack('<HH', byteArr[0:4])
    bytes = x[0] | x[1] << 16
    generalConf['adc_interval'] = bytes

    generalConf['init_code'] = unpack('<H', byteArr[4:6])[0]
    generalConf['page_adc'] = unpack('<H', byteArr[6:8])[0]
    generalConf['page_act'] = unpack('<H', byteArr[8:10])[0]
    generalConf['page_offset_adc'] = unpack('<H', byteArr[10:12])[0]
    generalConf['page_offset_act'] = unpack('<H', byteArr[12:14])[0]

    generalConf['num_areas'] = int(byteArr[14])
    generalConf['num_sensors'] = int(byteArr[15])
    generalConf['num_pumps'] = int(byteArr[16])
    generalConf['num_sovs'] = int(byteArr[17])
    #last 2 bytes are not relevant, exist because of padding in stm32 data structure

def unpack_area_conf(byteArr, idx):
    areaConf['area'+str(idx)] = {}
    areaConf['area'+str(idx)]['associated_sensors'] = [ 0 for i in range(15)]
    for i in range(15):
        areaConf['area'+str(idx)]['associated_sensors'][i] = int(byteArr[i])

    areaConf['area' + str(idx)]['associated_solenoids'] = [0 for i in range(10)]
    for i in range(10):
        areaConf['area' + str(idx)]['associated_solenoids'][i] = int(byteArr[15+i])

    x = unpack('<HH', byteArr[28:32])
    t = x[0] | x[1] << 16
    areaConf['area' + str(idx)]['watering_duration'] = t

    x = unpack('<HH', byteArr[32:36])
    t = x[0] | x[1] << 16
    areaConf['area' + str(idx)]['watering_interval'] = t

    x = unpack('<HH', byteArr[36:40])
    t = x[0] | x[1] << 16
    areaConf['area' + str(idx)]['last_watering_time'] = t

    areaConf['area' + str(idx)]['threshold'] = unpack('<H', byteArr[40:42])[0]

    areaConf['area' + str(idx)]['associated_pump'] = int(byteArr[42])

    areaConf['area' + str(idx)]['open_loop'] = "yes" if int(byteArr[43]) == 1 else "no"

    areaConf['area' + str(idx)]['area_ID'] = int(byteArr[44])
