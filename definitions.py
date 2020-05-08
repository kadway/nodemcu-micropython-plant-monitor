
#Definition of control bytes for SPI communication with ESP8266

#define ESP_GET_CONF       0xAA //get general configuration data
#define ESP_SET_CONF       0xAB
#define ESP_GET_AREA 	   0xBA //get area configuration data
#define ESP_SET_AREA	   0xBB
#define ESP_GET_DATA_ADC   0xCA //get measurements data
#define ESP_CLEAR_DATA_ADC 0xCB
#define ESP_GET_DATA_ACT   0xDA //get actuation data
#define ESP_CLEAR_DATA_ACT 0xDB
#define ESP_CLEAR_LOG	   0xEA
#define ESP_CLEAR_CONF	   0xEB

#define ESP_STOP_CONTROL_TASK    0xFA //suspend control task
#define ESP_RESUME_CONTROL_TASK  0xFB //resume control task

#definitions for spistm.py
status = bytearray(b'\x00')    # initialize to zero
dummyByte = bytearray(b'\x00')
nElementsByte = bytearray(b'\x00\x00\x00\x00')  # initialize to zero
ackMaster = bytearray(b'\xE3\xE3\xE3\xE3')      # ack from master to slave
ackSlave = bytearray(b'\xCE')    # ack byte from slave
c_getConf = bytearray(b'\xAA')   # get general configuration command from master to slave
c_getArea = bytearray(b'\xBA')   # list command from master to slave
c_getDataAdc = bytearray(b'\xCA')  # get adc data
c_getDataAct = bytearray(b'\xDA')  # get actuation data
confSize = 20
areaSize = 48
adcDataSize = 36
actDataSize = 12

#command definitions for json socket requests
get_general_conf = b'get_general_config'
set_general_conf = b'set_general_config'
get_area_conf = b'get_area_conf'
set_area_conf = b'set_area_conf'
get_adc_data = b'get_adc_data'
get_act_data = b'get_act_data'

defaultCommands = {
    b'get_general_config': bytearray(b'\xAA'),
    b'get_area_conf': bytearray(b'\xBA'),
    b'get_adc_data': bytearray(b'\xCA'),
    b'get_act_data': bytearray(b'\xDA'),
    b'set_general_config': bytearray(b'\xAB'),
    b'set_area_conf': bytearray(b'\xBB')
}