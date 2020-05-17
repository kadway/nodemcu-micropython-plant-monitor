from machine import Pin, SPI
import time
from struct import unpack

class Stm32Spi:
    def __init__(self):
        # init dictionaries that hold the configuration and log data
        #self.general_config = {}
        #self.area_config = {}
        #self.adc_data = {}
        #self.act_data = {}

        # define the existing commands for the communication with STM32
        # b'command name': [command byte to send, size in bytes of data structure in STM32, dictionary with data received/to send]
        self.default_commands = {
            b'get_general_config': [bytearray(b'\xAA'), 20, []],
            b'get_area_config': [bytearray(b'\xBA'), 48, []],
            b'get_adc_data': [bytearray(b'\xCA'), 36, []],
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

        # configure HW spi
        self.spi = SPI(1, baudrate=40000000, polarity=0, phase=0)
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
        self.idx = 0

    def send_command(self, command):

        self.c_recv = command
        #send the command
        self.CSN.off()
        self.spi.write_readinto(self.default_commands[command][0], self.status)
        self.CSN.on()
        time.sleep_ms(100)  # sleep 100 msec

        #for debug
        #print("Master: " + str(hex(command[0][0])))
        #print("Slave: " + str(hex(self.status[0])))

        if self.status == self.ackSlave:

            if self.c_recv == b'get_general_config':
                self.nElements = 1

            elif self.c_recv == b'get_area_config' or self.c_recv == b'get_adc_data' or self.c_recv == b'get_act_data':
                self.CSN.off()
                self.spi.write_readinto(self.ackMaster, self.nElementsByte)  # get number of elements
                self.CSN.on()
                time.sleep_ms(10)  # sleep  msec
                self.nElementsTuple = unpack('<HH', self.nElementsByte)
                self.nElements = self.nElementsTuple[0] | self.nElementsTuple[1] << 16

                # debug
                print("".join("0x%02x " % i for i in self.nElementsByte))
        else:
            print("Slave did not ack. STM32 will be reset....")
            # restart stm32
            self.reset.on()
            self.reset.off()
            time.sleep_ms(2000)

    def get_data(self, max_elements=10):

        # empty the list before adding more data to avoid memory problems
        self.default_commands[self.c_recv][2] = []
        self.idx = 0

        if self.nElements > 0:  # data size is not zero -> continue
            for i in range(min(self.nElements, max_elements)):
                self.get_spi_bytes()

                if self.c_recv == b'get_general_config':
                    #print("Get general configuration")
                    self.unpack_general_conf()

                elif self.c_recv == b'get_area_config':
                    #print("Get area configuration")
                    self.unpack_area_conf(self.gen_idx()-1)
                    #print(self.default_commands[b'get_area_config'][2])

                elif self.c_recv == b'get_adc_data':
                    #print("Get ADC data")
                    self.unpack_adc_data(self.gen_idx()-1)
                    #print(self.default_commands[b'get_adc_data'][2])

                elif self.c_recv == b'get_act_data':
                    print("Get actuation data")

                self.nElements -= 1

        else:
            print("Error: Num of elements is {} !".format(self.nElements))

    def get_spi_bytes(self):

        self.byteArr = bytearray(b'\x00' * self.default_commands[self.c_recv][1])  # initialize to zero
        self.dummyByteArr = bytearray(b'\x21' * self.default_commands[self.c_recv][1])  # dummy bytes

        self.CSN.off()
        self.spi.write_readinto(self.dummyByteArr, self.byteArr)
        self.CSN.on()

        time.sleep_ms(1)  # sleep msec
        self.byteArr_txt = "".join("0x%02x " % i for i in self.byteArr)

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

    def unpack_adc_data(self, idx):
        self.default_commands[b'get_adc_data'][2].append({})
        self.time_temp = unpack('<HH', self.byteArr[0:4])
        self.default_commands[b'get_adc_data'][2][idx]['time'] = self.time_temp[0] | self.time_temp[1] << 16
        self.default_commands[b'get_adc_data'][2][idx]['temperature'] = unpack('<H', self.byteArr[4:6])[0]
        self.default_commands[b'get_adc_data'][2][idx]['measurements'] = [0 for i in range(15)] # 0 to max num of sensors
        for i in range(15):
            self.default_commands[b'get_adc_data'][2][idx]['measurements'][i] = unpack('<H', self.byteArr[6+i*2:8+i*2])[0]

    def gen_idx(self):
        self.idx += 1
        return self.idx