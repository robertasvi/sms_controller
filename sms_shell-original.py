#https://www.instructables.com/Remote-Control-of-Raspberry-Pi-Via-SMS-SMS-Shell/
#pip install pyserial --break-system-packages
#python3 sms_shell.py
#brltty daemon causes the serial to shutdown; sudo apt-get remove brltty

import serial
import time
import re
import subprocess


ser = serial.Serial("/dev/ttyUSB0",115200)

my_phone_number = "+37061743092"

check_network_registration = "AT+CREG?\r\n".encode()
set_in_text_mode = "AT+CMGF=1\r\n".encode()
read_message_at_position =  "AT+CMGR="
send_message = "AT+CMGS=\"" + my_phone_number + "\"\n"

ser.write(check_network_registration)
ser.flushInput()
data = ''

try:
    while True:
        while ser.inWaiting() > 0:
            data = ser.read(ser.inWaiting()).decode('utf-8')
            time.sleep(0.0001)
        if data != "":
            print(data)
            if "CREG: 0,1" in data: # If Second parameter is 1 means it is registered successfully
                print("Network Is Registered")
                ser.write(set_in_text_mode)

            if "SM" in data: # Notification that new message is received
                message_index = items = re.findall("\"SM\",([0-9]*)", data)
                print("New Message Is Received in Index: " + message_index[0])
                ser.write((read_message_at_position + message_index[0] + "\r\n").encode())

            if "REC UNREAD" in data: # When receiving the new message and it is not read, looks like that: +CMTI: "SM",17
                message_parts = data.split(",") # Looks like that: ['\r\n+CMGR: "REC UNREAD"', '"+NUMBED"', '""', '"22/02/24', '17:14:23+08"\r\Hello world\r\n\r\nOK\r\n']
                print(message_parts)
                if message_parts[1].replace("\"", "") == my_phone_number: # Check if the message is from trusted number
                    print("Message is from my phone number")
                    message = str(message_parts[4]).split("\n")[1].replace('\r', '')

                    print("Command received: " + str(message))
                    shell_command_result = subprocess.check_output(str(message), shell=True) # Send the command to the shell

                    print("Result: " + shell_command_result.decode('utf-8'))
                    ser.write((send_message + shell_command_result.decode('utf-8')[:160] + "\x1A").encode()) # Limit the lenght of the answer to 160 characters and use \x1A instead of Ctrl+Z
                else:
                    print("Message is not from my phone number")

            data = ""
except KeyboardInterrupt:
    if ser != None:
        ser.close()