#!/usr/bin/python

from CLCD_Code import LCD


lcd = LCD(address=0x27, bus=1, width=16,rows=2, backlight=False)
lcd.text("Hello,", 1)
lcd.text("hello2", 2)
#lcd.backlight(False)
#lcd.backlight(True)
