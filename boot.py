import esp
esp.osdebug(None)
esp.osdebug(0)

def do_connect():
    import network
    import time
    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)
    if not sta_if.isconnected():
        print('Connecting to network...')
        ap_if.active(False)  # disable ap mode
        sta_if.active(True) #enable station mode
        sta_if.connect('my_network', 'my_password')
        time.sleep(1)  # sleep for 1 second
        while not sta_if.isconnected():
            print('Still trying to connect to network...')
            ap_if.active(False)  # disable ap mode
            sta_if.active(True)  # enable station mode
            sta_if.connect('my_network', 'my_password')
            time.sleep(5)  # sleep for 5 seconds
    print('Network config:', sta_if.ifconfig())

import webrepl
webrepl.start()