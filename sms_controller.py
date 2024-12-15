#https://www.instructables.com/Remote-Control-of-Raspberry-Pi-Via-SMS-SMS-Shell/
#pip install pyserial --break-system-packages
#pip install usb_resetter --break-system-packages https://github.com/netinvent/usb_resetter
#python3 sms_shell.py
#brltty daemon causes the serial to shutdown; sudo apt-get remove brltty

import serial
import time
import re
import subprocess
import logging
import os

logging.basicConfig(
    filename="logging.log",
    encoding="utf-8",
    filemode="a",
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    level=logging.INFO,
)

my_phone_number = "+37061743092"
check_network_registration = "AT+CREG?\r\n".encode()
set_in_text_mode = "AT+CMGF=1\r\n".encode()
read_message_at_position =  "AT+CMGR="
delete_all_messages = "AT+CMGD=1,4"
send_message = "AT+CMGS=\"" + my_phone_number + "\"\n"
data = ''

try:
    ser = serial.Serial("/dev/ttyUSB0",115200)
    ser.write(check_network_registration)
    ser.flush()
    while True:
        try:
            while ser.inWaiting() > 0:
                data = ser.read(ser.inWaiting()).decode('utf-8')
                time.sleep(0.001)
        except Exception as e:
            logging.error('Exception reading input: %s', repr(e))

        if data != "":
            if "CREG: 0,1" in data: # If Second parameter is 1 means it is registered successfully
                print("Network is registered")
                logging.info("Network is registered")
                ser.flush()
                ser.write(set_in_text_mode)

            if "SM" in data: # Notification that new message is received
                message_index = items = re.findall("\"SM\",([0-9]*)", data)
                print("New Message Is Received in Index: " + message_index[0])
                ser.flush()
                ser.write((read_message_at_position + message_index[0] + "\r\n").encode())

            if "REC UNREAD" in data: # When receiving the new message and it is not read, looks like that: +CMTI: "SM",17
                message_parts = data.split(",") # Looks like that: ['\r\n+CMGR: "REC UNREAD"', '"+NUMBED"', '""', '"22/02/24', '17:14:23+08"\r\Hello world\r\n\r\nOK\r\n']
                print(message_parts)
                if message_parts[1].replace("\"", "") == my_phone_number: # Check if the message is from trusted number
                    print("Message is from my phone number")
                    message = str(message_parts[4]).split("\n")[1].replace('\r', '')
                else:
                    print("Message is not from my phone number")

            if "status" in data:
                logging.info("Command status")
                ser.flush()
                ser.write((send_message + "Status info"[:160] + "\x1A").encode()) # Limit the lenght of the answer to 160 characters and use \x1A instead of Ctrl+Z
                logging.info("Sent status info")
                ser.flush()
                ser.write((delete_all_messages + "\r\n").encode())
                logging.info("SMS deleted")
            if "heateron" in data:
                logging.info("Heater on")
                ser.flush()
                ser.write((send_message + "Heater on"[:160] + "\x1A").encode()) # Limit the lenght of the answer to 160 characters and use \x1A instead of Ctrl+Z
                logging.info("Sent heater on confirmation")
                ser.flush()
                ser.write((delete_all_messages + "\r\n").encode())
                logging.info("SMS deleted")
            if "heateroff" in data:
                logging.info("Heater off")
                ser.flush()
                ser.write((send_message + "Heater off"[:160] + "\x1A").encode()) # Limit the lenght of the answer to 160 characters and use \x1A instead of Ctrl+Z
                logging.info("Sent heater off confirmation")
                ser.flush()
                ser.write((delete_all_messages + "\r\n").encode())
                logging.info("SMS deleted")

            data = ""
except KeyboardInterrupt:
    if ser != None:
        ser.close()
except NameError as e:
    logging.error('Variable definition error: %s', repr(e))
except Exception as e:
    logging.error('Exception with serial communication: %s', repr(e))
    #exec(open("reset_usb.py").read())
    #os.system('reboot')