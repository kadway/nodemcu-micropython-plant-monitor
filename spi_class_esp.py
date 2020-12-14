from machine import Pin, SPI
import time
from struct import unpack

class Stm32Spi:
    def __init__(self):
        # define the existing commands for the communication with STM32
        # b'command name': [command byte to send, size in bytes of data structure in STM32, dictionary with data received/to send]
        self.default_commands = {
            b'get_general_config': [bytearray(b'\xAA'), 20],
            b'get_area_config': [bytearray(b'\xBA'), 48],
            b'get_adc_data': [bytearray(b'\xCA'), 38],
            b'get_act_data': [bytearray(b'\xDA'), 12],
            b'set_general_config': [bytearray(b'\xAB'), 20],
            b'set_area_config': [bytearray(b'\xBB'), 48]
        }

        self.c_recv = None
        self.status = bytearray(b'\x00')  # initialize to zero
        self.dummyByteArr = bytearray(b'\x00')                  # initialize to zero
        self.nElements = 0
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

    def send_command(self, command):
        self.c_recv = command
        self.CSN.off()
        self.spi.write_readinto(self.default_commands[command][0], self.status)
        time.sleep_ms(5)

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

    def get_data(self):
        self.CSN.off()
        if self.nElements > 0:  # data size is not zero -> continue
            self.get_spi_bytes()
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
