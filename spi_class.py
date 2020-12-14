from machine import Pin, SPI
import time
from struct import unpack

class Stm32Spi:
    def __init__(self):
        # define the existing commands for the communication with STM32
        # b'command name': [command byte to send, size in bytes of data structure in STM32, dictionary with data received/to send]
        self.default_commands = {
            b'get_general_config': [bytearray(b'\xAA'), 20, []],
            b'get_area_config': [bytearray(b'\xBA'), 48, []],
            b'get_adc_data': [bytearray(b'\xCA'), 38, []],
            b'get_act_data': [bytearray(b'\xDA'), 12, []],
            b'set_general_config': [bytearray(b'\xAB'), 20, []],
            b'set_area_config': [bytearray(b'\xBB'), 48, []]
        }

        self.c_recv = None
        self.status = bytearray(b'\x00')  # initialize to zero

        self.dummyByteArr = bytearray(b'\x00')                  # initialize to zero
        self.nElements = 0
        self.nElementsLeft = 0
        self.nElementsByte = bytearray(b'\x00\x00\x00\x00')  # initialize to zero
        self.nElementsTuple = ()

        # configure HW spi max baudrate=40000000
        self.spi = SPI(1, baudrate=1000000, polarity=0, phase=0)
        self.reset = Pin(5, Pin.OUT)  # Pin 5 or D1 on node mcu
        self.reset.on()
        self.reset.off()
        self.CSN = Pin(15, Pin.OUT)
        self.CSN.on()

        # auxiliary variables
        self.ackMaster = bytearray(b'\xE3\xE3\xE3\xE3')      # ack from master to slave
        self.ackSlave = bytearray(b'\xCE')                   # ack byte from slave

        # variables for spi get data method
        self.byteArr = bytearray()
        self.byteArr_txt = ''  # for debugging

    def reset(self):
        #self.__init__()
        self.nElements = 0
        self.nElementsLeft = 0

    def send_command(self, command):
        self.c_recv = command
        self.CSN.off()
        self.spi.write_readinto(self.default_commands[command][0], self.status)
        time.sleep_ms(5)

        #for debug
        #print("Master: " + str(hex(command[0][0])))
        #print("Slave: " + str(hex(self.status[0])))

        if self.status == self.ackSlave:
            if self.c_recv == b'get_general_config':
                self.nElements = 1

            elif self.c_recv == b'get_area_config' or self.c_recv == b'get_adc_data' or self.c_recv == b'get_act_data':
                self.spi.write_readinto(self.ackMaster, self.nElementsByte)  # get number of elements
                time.sleep_ms(5)
                self.nElementsTuple = unpack('<HH', self.nElementsByte)
                self.nElements = self.nElementsTuple[0] | self.nElementsTuple[1] << 16

                # debug
                #print("".join("0x%02x " % i for i in self.nElementsByte))
        else:
            print("Slave did not ack. STM32 spi will be reset....")
            # restart stm32 spi
            self.reset.on()
            self.reset.off()
            time.sleep_ms(2000)

    #def send_data(self, data):
        #if self.c_recv == b'set_general_config':
            #self.pack_general_conf(data)
            #self.send_spi_bytes()

       #elif self.c_recv == b'set_area_config':
       #    pack_area_conf(data)


    def get_data(self):
        # empty the list before adding more data to avoid memory problems
        self.default_commands[self.c_recv][2] = []
        self.CSN.off()
        if self.nElements > 0:  # data size is not zero -> continue
            self.get_spi_bytes()
            if self.c_recv == b'get_general_config':
                self.unpack_general_conf()
            elif self.c_recv == b'get_area_config':
                self.unpack_area_conf(0)
            elif self.c_recv == b'get_adc_data':
                self.unpack_time_data(0)
                self.unpack_adc_data(0)
            elif self.c_recv == b'get_act_data':
                self.unpack_time_data(0)
                self.unpack_act_data(0)
            self.nElements -= 1
        else:
            print("Error: Num of elements is {} !".format(self.nElements))
        self.CSN.on()

    def send_spi_bytes(self):
        self.dummyByteArr = bytearray(b'\x21' * self.default_commands[self.c_recv][1])  # dummy bytes
        self.spi.write_readinto(self.byteArr, self.dummyByteArr)
        time.sleep_ms(1)  # sleep msec


    def get_spi_bytes(self):
        self.byteArr = bytearray(b'\x00' * self.default_commands[self.c_recv][1])  # initialize to zero
        self.dummyByteArr = bytearray(b'\x21' * self.default_commands[self.c_recv][1])  # dummy bytes
        self.spi.write_readinto(self.dummyByteArr, self.byteArr)
        time.sleep_ms(1)  # sleep msec

    def unpack_general_conf(self):
        self.time_temp = unpack('<HH', self.byteArr[0:4])
        self.default_commands[b'get_general_config'][2].append({})
        self.default_commands[b'get_general_config'][2][0]['adc_interval'] = self.time_temp[0] | self.time_temp[1] << 16
        self.default_commands[b'get_general_config'][2][0]['init_code'] = unpack('<H', self.byteArr[4:6])[0]
        self.default_commands[b'get_general_config'][2][0]['page_adc'] = unpack('<H', self.byteArr[6:8])[0]
        self.default_commands[b'get_general_config'][2][0]['page_act'] = unpack('<H', self.byteArr[8:10])[0]
        self.default_commands[b'get_general_config'][2][0]['page_offset_adc'] = unpack('<H', self.byteArr[10:12])[0]
        self.default_commands[b'get_general_config'][2][0]['page_offset_act'] = unpack('<H', self.byteArr[12:14])[0]
        self.default_commands[b'get_general_config'][2][0]['num_areas'] = int(self.byteArr[14])
        self.default_commands[b'get_general_config'][2][0]['num_sensors'] = int(self.byteArr[15])
        self.default_commands[b'get_general_config'][2][0]['num_pumps'] = int(self.byteArr[16])
        self.default_commands[b'get_general_config'][2][0]['num_sovs'] = int(self.byteArr[17])
        # last 2 bytes are not relevant, exist because of padding in stm32 data structure

    #def pack_general_conf(self, data):
        #self.byteArr = data[0]['adc_interval'].to_bytes(4,'little')
        #self.byteArr += data[0]['init_code'].to_bytes(2, 'little')
        #self.byteArr += data[0]['page_adc'].to_bytes(2, 'little')
        #self.byteArr += data[0]['page_act'].to_bytes(2, 'little')
        #self.byteArr += data[0]['page_offset_adc'].to_bytes(2, 'little')
        #self.byteArr += data[0]['page_offset_act'].to_bytes(2, 'little')
        #self.byteArr += data[0]['num_areas'].to_bytes(2, 'little')
        #self.byteArr = self.byteArr[0:len(self.byteArr) - 1]
        #self.byteArr += data[0]['num_sensors'].to_bytes(2, 'little')
        #self.byteArr = self.byteArr[0:len(self.byteArr) - 1]
        #self.byteArr += data[0]['num_pumps'].to_bytes(2, 'little')
        #self.byteArr = self.byteArr[0:len(self.byteArr) - 1]
        #self.byteArr += data[0]['num_sovs'].to_bytes(2, 'little')
        #self.byteArr += b'\x00'
        #self.byteArr_txt = "".join("0x%02x " % i for i in self.byteArr)
        #print(self.byteArr_txt)

    def unpack_area_conf(self, idx):
        self.default_commands[b'get_area_config'][2].append({})
        self.default_commands[b'get_area_config'][2][idx]['associated_sensors'] = [0 for i in range(15)]
        for i in range(15):
            self.default_commands[b'get_area_config'][2][idx]['associated_sensors'][i] = int(self.byteArr[i])
        self.default_commands[b'get_area_config'][2][idx]['associated_solenoids'] = [0 for i in range(10)]
        for i in range(10):
            self.default_commands[b'get_area_config'][2][idx]['associated_solenoids'][i] = int(self.byteArr[15 + i])
        self.time_temp = unpack('<HH', self.byteArr[28:32])
        self.default_commands[b'get_area_config'][2][idx]['watering_duration'] = self.time_temp[0] | self.time_temp[1] << 16
        self.time_temp = unpack('<HH', self.byteArr[32:36])
        self.default_commands[b'get_area_config'][2][idx]['watering_interval'] = self.time_temp[0] | self.time_temp[1] << 16
        self.time_temp = unpack('<HH', self.byteArr[36:40])
        self.default_commands[b'get_area_config'][2][idx]['last_watering_time'] = self.time_temp[0] | self.time_temp[1] << 16
        self.default_commands[b'get_area_config'][2][idx]['threshold'] = unpack('<H', self.byteArr[40:42])[0]
        self.default_commands[b'get_area_config'][2][idx]['associated_pump'] = int(self.byteArr[42])
        self.default_commands[b'get_area_config'][2][idx]['open_loop'] = "yes" if int(self.byteArr[43]) == 1 else "no"
        self.default_commands[b'get_area_config'][2][idx]['area_ID'] = int(self.byteArr[44])

    def unpack_time_data(self, idx):
        self.default_commands[self.c_recv][2].append({})
        self.default_commands[self.c_recv][2][idx]['hours'] = int(self.byteArr[0])
        self.default_commands[self.c_recv][2][idx]['minutes'] = int(self.byteArr[1])
        self.default_commands[self.c_recv][2][idx]['seconds'] = int(self.byteArr[2])
        self.default_commands[self.c_recv][2][idx]['timeformat'] = int(self.byteArr[3])
        self.default_commands[self.c_recv][2][idx]['month'] = int(self.byteArr[4])
        self.default_commands[self.c_recv][2][idx]['day'] = int(self.byteArr[5])
        self.default_commands[self.c_recv][2][idx]['year'] = int(self.byteArr[6])

    def unpack_adc_data(self, idx):
        self.default_commands[self.c_recv][2][idx]['temperature'] = int(self.byteArr[7])
        self.default_commands[self.c_recv][2][idx]['measurements'] = [0 for i in range(15)] # 0 to max num of sensors
        for i in range(15):
            self.default_commands[self.c_recv][2][idx]['measurements'][i] = unpack('<H', self.byteArr[8+i*2:10+i*2])[0]

    def unpack_act_data(self, idx):
        self.default_commands[self.c_recv][2][idx]['area_id'] = int(self.byteArr[7])
        self.time_temp = unpack('<HH', self.byteArr[8:12])
        self.default_commands[self.c_recv][2][idx]['duration'] = self.time_temp[0] | self.time_temp[1] << 16