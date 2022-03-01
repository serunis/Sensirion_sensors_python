#!/usr/bin/python

import time
#sudo pip3 install smbus2
from smbus2 import SMBus, i2c_msg


class sht3x():
    def __init__(self):
        self.i2c_bus = SMBus(1)
        self.i2cAddr = 0x44
        self.temperature = None
        self.humidity = None

    def invalid(self):
        self.temperature = None
        self.humidity = None
        
    def sensirion_common_generate_crc(self, data_list):
        crc = 0xFF
        for a in data_list:
            crc ^= a
            for i in range(8):
                if crc & 0x80 != 0:
                    crc = (crc << 1)^0x31
                else:
                    crc = (crc << 1)
        return (crc & 0xFF)

    def sht3x_read(self):
    
        wr_msg = i2c_msg.write(self.i2cAddr, [0x2C, 0x06])
        rd_msg = i2c_msg.read(self.i2cAddr, 6)
        
        self.i2c_bus.i2c_rdwr(wr_msg, rd_msg)
        value = list(rd_msg)
        
        crc8_calc = self.sensirion_common_generate_crc(value[0:2])
        if crc8_calc != value[2]:
            self.invalid()
            return False
            
        crc8_calc = self.sensirion_common_generate_crc(value[3:5])
        if crc8_calc != value[5]:
            self.invalid()
            return False
        
        self.temperature = ((((value[0] * 256.0) + value[1]) * 175) / 65535.0) - 45
        self.humidity = 100 * (value[3] * 256 + value[4]) / 65535.0
        
        return True

"""
sht30 = sht3x()
print(sht30.sht3x_read())
print('Temperature: %8.2f°C humidity: %8.2frh' % (sht30.temperature, sht30.humidity))
"""
