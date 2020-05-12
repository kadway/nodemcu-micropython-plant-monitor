# plant-monitor-nodemcu-wifi-bridge

This is part of the plant watering and monitoring project with STM32 mcu: https://github.com/kadway/stm32f4-freertos-plant-monitor  
The nodemcu with esp8266 is used with micropython firmware to serve as a wifi gateway allowing to read the saved moisture measurements data and actuation log from the external flash in the stm32 development board and to modify the system configurations.

#### To do:
* Improve README
* Check why json keeps crashing when trying to load larger amounts of data (client_script.py)
* Extend the spi_class to unpack the actuation data (incoming bytes from stm32)
* Send configuration data to stm32
* Add webpage visualization of actual configuration and last logged data
* Generalize the connection to wifi - https://github.com/anson-vandoren/esp8266-captive-portal seems like a way to do it
