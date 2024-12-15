import serial
import time
import re
import subprocess


ser = serial.Serial("/dev/ttyUSB0",115200)

my_phone_number = "+37061743092"

check_network_registration = "AT+CREG?\r\n".encode()

ser.write(check_network_registration)
ser.flush()
data = ''

try:
    while True:
        while ser.inWaiting() > 0:
            data = ser.read(ser.inWaiting()).decode('utf-8')
            time.sleep(0.001)
        if data != "":
            print("Data: " + data)
            
            #TODOS

            data = ""
except KeyboardInterrupt:
    if ser != None:
        ser.close()