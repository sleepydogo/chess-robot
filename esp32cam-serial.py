
## Todavia no esta implementado del todo

import serial
import time

ser = serial.Serial('/dev/ttyUSB0', 115200)

time.sleep(2)

ser.write('capture\n')

time.sleep(2)

image_data = ser.read(320 * 240 * 2)

ser.close()

with open('image.jpg', 'wb') as f:
    f.write(image_data)