def test(spi, data_out):
    # import pin and hardware spi
    # from machine import Pin, SPI
    #import time
    #data_out = bytearray(print_out)
    data_in = data_out  # create a buffer

    spi.write_readinto(data_out, data_in)  # read into the given buffer (data_in) and output data_out on MOSI
    #spi.write_readinto(data_out, data_in)  # read into the given buffer (data_in) and output data_out on MOSI
    #time.sleep(1) #sleep 1 sec
    return data_in


# >>> buf = bytearray(b'012\x00\x01\x02ABC')
# >>> import ubinascii
# >>> print(ubinascii.hexlify(buf))
# b'303132000102414243'
# >>> print(ubinascii.hexlify(buf, ' '))
# b'30 31 32 00 01 02 41 42 43'
# >>> print(ubinascii.hexlify(buf, ' ').decode('ascii'))
# 30 31 32 00 01 02 41 42 43