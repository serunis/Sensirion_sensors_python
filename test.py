#!/usr/bin/python

from sfa30 import sfa30
from scd4x import scd4x
from CLCD_Code import LCD

from DFRobot_SGP40 import DFRobot_SGP40
from sht3x import sht3x

import time




lcd = LCD(address=0x27, bus=1, width=16,rows=2, backlight=False)
lcd.text("Please", 1)
lcd.text("wait 15 seconds", 2)


sfa = sfa30()
sfa.sfa30_startPeriodicMeasurement()
time.sleep(0.5)

scd41 = scd4x()
scd41.scd4x_startPeriodicMeasurement()
#time.sleep(5)

sgp40=DFRobot_SGP40(bus = 1, relative_humidity = 50, temperature_c = 25)
sht31=sht3x()
#set Warm-up time
print('Please wait 10 seconds')
sgp40.begin(10)

cnt = 1
while True:
    sht31.sht3x_read()
    sgp40.set_envparams(sht31.humidity, sht31.temperature)
    print('Voc index: %-3d Temperature: %4.1f°C humidity: %2drh' % (sgp40.get_voc_index(), sht31.temperature, sht31.humidity))

    if cnt == 5:
        cnt = 0
        sfa.sfa30_read()
        scd41.scd4x_read()
        print('HCHO:', sfa.hcho)
        print('CO2:', scd41.co2)
        print('')
        lcd_str = "V:%-3d   %4.1f %2d P:%.3f C:%-4d" % (sgp40.get_voc_index(), sht31.temperature, sht31.humidity, sfa.hcho/1000, scd41.co2)
        lcd.text(lcd_str, 1)
    
    cnt += 1
    time.sleep(1)

