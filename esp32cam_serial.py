import serial
import time

# Open the serial port to the ESP32-CAM
ser = serial.Serial('/dev/ttyUSB0', 115200)

# Wait for the ESP32-CAM to boot up
time.sleep(2)

# Send the command to take a picture
ser.write('capture\n')

# Wait for the picture to be taken
time.sleep(2)

# Read the image data from the ESP32-CAM
image_data = ser.read(320 * 240 * 2)

# Close the serial port
ser.close()

# Save the image data to a file
with open('image.jpg', 'wb') as f:
    f.write(image_data)