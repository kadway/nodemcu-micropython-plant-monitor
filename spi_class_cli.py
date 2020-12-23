from struct import unpack
import json
import os

class Stm32SpiCli:
    def __init__(self):
        # define the existing commands for the communication with STM32
        # b'command name': [command byte to send, size in bytes of data structure in STM32, dictionary with data received/to send]
        self.commands = {
            b'get_general_config': [20, []],
            b'get_area_config': [48, []],
            b'get_adc_data': [38, []],
            b'get_act_data': [12, []],
            b'set_general_config': [20, []],
            b'set_area_config': [48, []]
        }

        self.c_recv = None
        self.byteArr = bytearray()
        self.tempArr = bytearray()
        self.numBytes = 0

    def save_data(self, bArr, command):
        self.c_recv = command
        self.byteArr = bArr
        filename = str(command)
        filename = "data/" + filename[2:-1] + ".json"
        if os.path.exists(filename):
            os.remove(filename)

        if command == b'get_general_config':
            self.unpack_general_conf()

        else:
            self.numBytes = self.commands[self.c_recv][0]
            self.numParts = int(len(self.byteArr)/self.numBytes)
            for i in range(self.numParts):
                self.tempArr = self.byteArr[i*self.numBytes:i*self.numBytes+self.numBytes]
                if command == b'get_area_config':
                    self.unpack_area_conf(i)
                else:
                    self.unpack_time_data(i)
                    if command == b'get_adc_data':
                        self.unpack_adc_data(i)
                    elif command == b'get_act_data':
                        self.unpack_act_data(i)

        with open(filename, 'w') as f:
            json.dump(self.commands[command][1], f)

        #empty the list after saving data
        if command == b'get_adc_data' or command == b'get_act_data' or command == b'get_area_config':
            self.commands[self.c_recv][1] = []

    def load_data(self, command):
        self.c_recv = command

        filename = str(command)
        filename = "data/" + filename[2:-1] + ".json"

        if os.path.exists(filename):
            with open(filename, 'r') as f:
                self.commands[self.c_recv][1] = json.load(f)
        else:
            print("Err: Path " + filename + " does not exist. Duplicate get_*_data.json and rename to set_*_data.json first!")

        if command == b'set_general_config':
            self.pack_general_conf()
            return self.byteArr

        elif command == b'set_area_config':
            if self.commands[b'get_general_config'][1]:
                self.pack_area_conf()
                print(str(self.commands[b'get_general_config'][1][0]['num_areas']) + " areas from file packed in bytearray")
                return self.byteArr
            else:
                print("Err: Must get general configuration before trying to send area conf.")
                return b'\x01'


    def unpack_general_conf(self):
        self.time_temp = unpack('<HH', self.byteArr[0:4])
        self.commands[b'get_general_config'][1] = []
        self.commands[b'get_general_config'][1].append({})
        self.commands[b'get_general_config'][1][0]['adc_interval'] = self.time_temp[0] | self.time_temp[1] << 16
        self.commands[b'get_general_config'][1][0]['init_code'] = unpack('<H', self.byteArr[4:6])[0]
        self.commands[b'get_general_config'][1][0]['page_adc'] = unpack('<H', self.byteArr[6:8])[0]
        self.commands[b'get_general_config'][1][0]['page_act'] = unpack('<H', self.byteArr[8:10])[0]
        self.commands[b'get_general_config'][1][0]['page_offset_adc'] = unpack('<H', self.byteArr[10:12])[0]
        self.commands[b'get_general_config'][1][0]['page_offset_act'] = unpack('<H', self.byteArr[12:14])[0]
        self.commands[b'get_general_config'][1][0]['num_areas'] = int(self.byteArr[14])
        self.commands[b'get_general_config'][1][0]['num_sensors'] = int(self.byteArr[15])
        self.commands[b'get_general_config'][1][0]['num_pumps'] = int(self.byteArr[16])
        self.commands[b'get_general_config'][1][0]['num_sovs'] = int(self.byteArr[17])
        # last 2 bytes are not relevant, exist because of padding in stm32 data structure

    def pack_general_conf(self):
        self.byteArr = self.commands[b'set_general_config'][1][0]['adc_interval'].to_bytes(4,'little')
        self.byteArr += self.commands[b'set_general_config'][1][0]['init_code'].to_bytes(2, 'little')
        self.byteArr += self.commands[b'set_general_config'][1][0]['page_adc'].to_bytes(2, 'little')
        self.byteArr += self.commands[b'set_general_config'][1][0]['page_act'].to_bytes(2, 'little')
        self.byteArr += self.commands[b'set_general_config'][1][0]['page_offset_adc'].to_bytes(2, 'little')
        self.byteArr += self.commands[b'set_general_config'][1][0]['page_offset_act'].to_bytes(2, 'little')
        self.byteArr += self.commands[b'set_general_config'][1][0]['num_areas'].to_bytes(2, 'little')
        self.byteArr = self.byteArr[:-1]
        self.byteArr += self.commands[b'set_general_config'][1][0]['num_sensors'].to_bytes(2, 'little')
        self.byteArr = self.byteArr[:-1]
        self.byteArr += self.commands[b'set_general_config'][1][0]['num_pumps'].to_bytes(2, 'little')
        self.byteArr = self.byteArr[:-1]
        self.byteArr += self.commands[b'set_general_config'][1][0]['num_sovs'].to_bytes(2, 'little')
        self.byteArr += b'\x00'
        #self.byteArr_txt = "".join("0x%02x " % i for i in self.byteArr)
        #print(self.byteArr_txt)

    def unpack_area_conf(self, idx):
        self.commands[b'get_area_config'][1].append({})
        self.commands[b'get_area_config'][1][idx]['associated_sensors'] = [0 for i in range(15)]
        for i in range(15):
            self.commands[b'get_area_config'][1][idx]['associated_sensors'][i] = int(self.tempArr[i])
        self.commands[b'get_area_config'][1][idx]['associated_solenoids'] = [0 for i in range(10)]
        for i in range(10):
            self.commands[b'get_area_config'][1][idx]['associated_solenoids'][i] = int(self.tempArr[15 + i])
        self.time_temp = unpack('<HH', self.tempArr[28:32])
        self.commands[b'get_area_config'][1][idx]['watering_duration'] = self.time_temp[0] | self.time_temp[1] << 16
        self.time_temp = unpack('<HH', self.tempArr[32:36])
        self.commands[b'get_area_config'][1][idx]['watering_interval'] = self.time_temp[0] | self.time_temp[1] << 16
        self.time_temp = unpack('<HH', self.tempArr[36:40])
        self.commands[b'get_area_config'][1][idx]['last_watering_time'] = self.time_temp[0] | self.time_temp[1] << 16
        self.commands[b'get_area_config'][1][idx]['threshold'] = unpack('<H', self.tempArr[40:42])[0]
        self.commands[b'get_area_config'][1][idx]['associated_pump'] = int(self.tempArr[42])
        self.commands[b'get_area_config'][1][idx]['open_loop'] = "yes" if int(self.tempArr[43]) == 1 else "no"
        self.commands[b'get_area_config'][1][idx]['area_ID'] = int(self.tempArr[44])

    def pack_area_conf(self):
        #clear byte array first
        self.byteArr = bytearray()

        for area_num in range(self.commands[b'get_general_config'][1][0]['num_areas']):
            for i in range(15):
                self.byteArr += self.commands[b'set_area_config'][1][area_num]['associated_sensors'][i].to_bytes(2, 'little')
                self.byteArr = self.byteArr[:-1]
            for i in range(10):
                self.byteArr += self.commands[b'set_area_config'][1][area_num]['associated_solenoids'][i].to_bytes(2, 'little')
                self.byteArr = self.byteArr[:-1]
            self.byteArr += b'\x00\x00\x00'
            self.byteArr += self.commands[b'set_area_config'][1][area_num]['watering_duration'].to_bytes(4, 'little')
            self.byteArr += self.commands[b'set_area_config'][1][area_num]['watering_interval'].to_bytes(4, 'little')
            self.byteArr += self.commands[b'set_area_config'][1][area_num]['last_watering_time'].to_bytes(4, 'little')
            self.byteArr += self.commands[b'set_area_config'][1][area_num]['threshold'].to_bytes(2, 'little')
            self.byteArr += self.commands[b'set_area_config'][1][area_num]['associated_pump'].to_bytes(2, 'little')
            self.byteArr = self.byteArr[:-1]
            self.byteArr += b'\x01' if (self.commands[b'set_area_config'][1][area_num]['open_loop'] == "yes") else b'\x00'
            self.byteArr += self.commands[b'set_area_config'][1][area_num]['area_ID'].to_bytes(2, 'little')
            self.byteArr += b'\x00\x00'

    def unpack_time_data(self, idx):
        self.commands[self.c_recv][1].append({})
        self.commands[self.c_recv][1][idx]['hours'] = int(self.tempArr[0])
        self.commands[self.c_recv][1][idx]['minutes'] = int(self.tempArr[1])
        self.commands[self.c_recv][1][idx]['seconds'] = int(self.tempArr[2])
        self.commands[self.c_recv][1][idx]['timeformat'] = int(self.tempArr[3])
        self.commands[self.c_recv][1][idx]['month'] = int(self.tempArr[4])
        self.commands[self.c_recv][1][idx]['day'] = int(self.tempArr[5])
        self.commands[self.c_recv][1][idx]['year'] = int(self.tempArr[6])

    def unpack_adc_data(self, idx):
        self.commands[self.c_recv][1][idx]['temperature'] = int(self.tempArr[7])
        self.commands[self.c_recv][1][idx]['measurements'] = [0 for i in range(15)] # 0 to max num of sensors
        for i in range(15):
            self.commands[self.c_recv][1][idx]['measurements'][i] = unpack('<H', self.tempArr[8 + i * 2:10 + i * 2])[0]

    def unpack_act_data(self, idx):
        self.commands[self.c_recv][1][idx]['area_id'] = int(self.tempArr[7])
        self.time_temp = unpack('<HH', self.tempArr[8:12])
        self.commands[self.c_recv][1][idx]['duration'] = self.time_temp[0] | self.time_temp[1] << 16