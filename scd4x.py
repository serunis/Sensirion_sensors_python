#!/usr/bin/python

import time
#sudo pip3 install smbus2
from smbus2 import SMBus, i2c_msg




class scd4x():
    def __init__(self):
        self.i2c_bus = SMBus(1)
        self.i2cAddr = 0x62
        
        self.co2 = None
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
        
    def scd4x_startPeriodicMeasurement(self):
        #stop_periodic_measurement
        msg = i2c_msg.write(self.i2cAddr, [0x3f, 0x86])
        self.i2c_bus.i2c_rdwr(msg)
        time.sleep(0.5)
        
        #startPeriodicMeasurement
        msg = i2c_msg.write(self.i2cAddr, [0x21, 0xB1])
        self.i2c_bus.i2c_rdwr(msg)
        
        
    def scd4x_read(self):
        msg = i2c_msg.write(self.i2cAddr, [0xec, 0x05])
        self.i2c_bus.i2c_rdwr(msg)
        time.sleep(0.001)#1ms
        
        msg = i2c_msg.read(self.i2cAddr, 9)
        self.i2c_bus.i2c_rdwr(msg)
        value = list(msg)

        #CO2
        self.co2 = value[0]*256 + value[1]
        crc8_calc = self.sensirion_common_generate_crc(value[0:2])
        if crc8_calc != value[2]:
            self.invalid()
            return False
        
        #Temperature
        temp = value[3]*256 + value[4]
        crc8_calc = self.sensirion_common_generate_crc(value[3:5])
        if crc8_calc != value[5]:
            self.invalid()
            return False
            
        self.temperature = -45 + 175 * temp / 65536
        
        #Humidity
        temp = value[6]*256 + value[7]
        crc8_calc = self.sensirion_common_generate_crc(value[6:8])
        
        if crc8_calc != value[8]:
            self.invalid()
            return False
            
        self.humidity = 100 * temp / 65536
        return True

    def scd4x_perform_forced_recalibration(self, target_CO2):
    
        #pre-condition
        #Operate the SCD4x in the operation mode later used in normal sensor operation 
        #(periodic measurement, low power periodic measurement or single shot) 
        #for > 3 minutes in an environment with homogenous and constant CO2 concentration.
        
        #stop_periodic_measurement
        msg = i2c_msg.write(self.i2cAddr, [0x3f, 0x86])
        self.i2c_bus.i2c_rdwr(msg)
        time.sleep(0.5)
        
        word0 = target_CO2 >> 8
        word1 = target_CO2 & 0xFF
        word = [word0, word1]
        crc8_calc = self.sensirion_common_generate_crc(word)
        
        msg = i2c_msg.write(self.i2cAddr, [0x36, 0x2f, word0, word1, crc8_calc])
        self.i2c_bus.i2c_rdwr(msg)
        time.sleep(0.4)
        
        
        msg = i2c_msg.read(self.i2cAddr, 3)
        self.i2c_bus.i2c_rdwr(msg)
        value = list(msg)
        
        crc8_calc = self.sensirion_common_generate_crc(value[0:2])
        if crc8_calc != value[2]:
            self.invalid()
            return False
        
        print(value)
        
        if value[0] == 0xFF and value[1] == 0xFF:
            return False
        else:
            return True
    


"""
aa = scd4x()
aa.scd4x_startPeriodicMeasurement()
print('Signal update interval is 5 second')
time.sleep(5)

ret = aa.scd4x_read()
print('result', ret)
print('CO2', aa.co2)
print('%4.2f°C, %2dRH' % (aa.temperature, aa.humidity))

time.sleep(5)

ret = aa.scd4x_read()
print('result', ret)
print('CO2', aa.co2)
print('%4.2f°C, %2dRH' % (aa.temperature, aa.humidity))

"""