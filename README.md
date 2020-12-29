# Python repository for NodeMCU ESP8266 interfacing STM32F407 and a network client

This repository is to be used together with
the [freeRTOS plant monitor](https://github.com/kadway/stm32f4-freertos-plant-monitor) which is the repository for a plant watering and monitoring
project which uses the [STM32F407VET6 development board](https://stm32-base.org/boards/STM32F407VET6-STM32-F4VE-V2.0.html) and FreeRTOS.

In this repository the NodeMCU (with the esp8266) is used with [MicroPython](https://docs.micropython.org/en/latest/index.html) firmware.
Check the [MicroPython documentation](https://docs.micropython.org/en/latest/esp8266/tutorial/intro.html) for getting started and getting the firmware.

The NodeMCU handles the byte level data exchange between the STM32 micro-controller and a network connected client,
it accepts requests from a client, via socket over TCP/IP and communicates with the STM32 micro-controller through SPI.

Through the NodeMCU, the main micro-controller firmware (STM32) can be re-configured with a python script 
running in a client connected in the same home network as the NodeMCU.

The client script can read the actual configuration and send updated one to the STM32 micro-controller from a 
json file containing the respective data structures.

The script has additional commands for reading logged data of moisture measurements, time and duration of 
watering of the configured areas (plants or pots) as well as commands
for resetting the configurations to a good known state and cleaning the logged data saved locally in the external 
flash of the STM32F407VET6 development board.

How to start
--
To use this code you need to have set-up the [freeRTOS plant monitor](https://github.com/kadway/stm32f4-freertos-plant-monitor) code in your STM32 board and have your own NodeMCU or ESP8266 based dev-board connected to it.
You may need to adjust pin assignments for SPI in spi_class_esp.py in case you don't use the same ones.

Firstly flash the MicroPython firmware [Instructions here](https://docs.micropython.org/en/latest/esp8266/tutorial/intro.html)

After flashing the MicroPython firmware, configure the [WebREPL](https://docs.micropython.org/en/latest/esp8266/tutorial/repl.html)
and clone the [WebREPL client repository](https://github.com/micropython/webrepl), this will make it very easy to send
python files to the esp8266.

Lastly clone this repository and send the modified boot.py, the main.py and the spi_class_esp.py using your local clone of the [WebREPL](https://github.com/micropython/webrepl) to the esp8266.

### Files in this repository

#### boot.py
- you need only to set your wifi network and password and after reboot it should connect to your wifi

#### main.py
- handles socket requests and forwards them to STM32

#### spi_class_esp.py
- handles the specific communication protocol over SPI

##### spi_class_cli.py
- handles the packing and unpacking of bytes of data to meaningful data structures

#### client_script.py
- handles the user input, you need to manually set your esp8266 IP

Available commands:

0. get general configuration
1. get area configuration
2. get adc data
3. get actuation data
4. set general configuration
5. set area configuration
6. clear log
7. reset STM
8. clear conf (default init)

### Configurations
Please refer to [freeRTOS plant monitor](https://github.com/kadway/stm32f4-freertos-plant-monitor)
for detailed explanations about the configuration possibilities and any existing limitations. 

### JSON saved data / data to send
The data received from the STM32 is stored in a python dictionary and saved in a JSON file.
By default new received data overwrites existing any file with same name.
For sending new configurations the received data should be copied and renamed from "get" to "set" like:

get_general_conf.json->set_general_conf.json
get_area_conf.json->set_area_conf.json

The general configuration data structure must be maintained, only values may be modified.
For adding of removing areas configuration, the dictionary size can be adjusted, but keeping the data size and format of
the areas.

------

#### Contributing
If you find the project interesting and would like to contribute feel free to send a pull request.
I'm also open for suggestions if you have ideas for To-Do's.

#### To Do:
* Automatic / periodic read of data logged in the STM32 external flash and save it in a data base (postgresql?)
* Graphic visualization of data (moisture/temperature over time, watering time vs moisture, etc)
* Add webpage visualization of actual configuration and last logged data (when possible - memory constraints?)
* Generalize the connection to wifi for when connecting to a new network - https://github.com/anson-vandoren/esp8266-captive-portal seems like a way to do it
