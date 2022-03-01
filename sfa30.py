#!/usr/bin/python

import time
#sudo pip3 install smbus2
from smbus2 import SMBus, i2c_msg




class sfa30():
    def __init__(self):
        self.i2c_bus = SMBus(1)
        self.i2cAddr = 0x5D
        
        self.hcho = None
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
        
    def invalid(self):
        self.temperature = None
        self.humidity = None
        self.co2 = None
        
    def sfa30_startPeriodicMeasurement(self):
        #Stop Continuous Measurement
        msg = i2c_msg.write(self.i2cAddr, [0x01, 0x04])
        self.i2c_bus.i2c_rdwr(msg)
        time.sleep(0.01)#10ms
        
        #Start continuous measurement
        msg = i2c_msg.write(self.i2cAddr, [0x00, 0x06])
        self.i2c_bus.i2c_rdwr(msg)
        time.sleep(0.01)#10ms
        
    def sfa30_read(self):
        msg = i2c_msg.write(self.i2cAddr, [0x03, 0x27])
        self.i2c_bus.i2c_rdwr(msg)
        time.sleep(0.1)#100ms
        
        msg = i2c_msg.read(self.i2cAddr, 9)
        self.i2c_bus.i2c_rdwr(msg)
        value = list(msg)


        #hcho
        self.hcho = value[0]*256 + value[1]
        crc8_calc = self.sensirion_common_generate_crc(value[0:2])
        if crc8_calc != value[2]:
            self.invalid()
            return False

        #Humidity
        temp = value[3]*256 + value[4]
        crc8_calc = self.sensirion_common_generate_crc(value[3:5])
        if crc8_calc != value[5]:
            self.invalid()
            return False
        
        self.humidity = temp / 100
        
        
        
        #Temperature
        temp = value[6]*256 + value[7]
        crc8_calc = self.sensirion_common_generate_crc(value[6:8])
        
        if crc8_calc != value[8]:
            self.invalid()
            return False
            
        self.temperature = temp / 200

        return True
    

"""
#should be power-on sfa30 10s before calling sfa30_startPeriodicMeasurement
aa = sfa30()
aa.sfa30_startPeriodicMeasurement()
time.sleep(0.5)

for trial in range(2):
    ret = aa.sfa30_read()
    print('trial:', trial,'result', ret)
    print('HCHO', aa.hcho)
    print('%4.2f°C, %2dRH' % (aa.temperature, aa.humidity))

    time.sleep(1)
"""