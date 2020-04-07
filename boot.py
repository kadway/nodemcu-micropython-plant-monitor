import esp
esp.osdebug(None)
esp.osdebug(0)

def do_connect():
    import network
    import time
    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        ap_if.active(False)  # disable ap mode
        sta_if.active(True) #enable station mode
        sta_if.connect('Cuibusor de Nebunii', 'whatislove')
        time.sleep(1)  # sleep for 1 second
        while not sta_if.isconnected():
            print('still trying to connect to network...')
            ap_if.active(False)  # disable ap mode
            sta_if.active(True)  # enable station mode
            sta_if.connect('Cuibusor de Nebunii', 'whatislove')
            time.sleep(1)  # sleep for 1 second
    print('network config:', sta_if.ifconfig())
import webrepl
webrepl.start()