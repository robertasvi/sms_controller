#sudo python reset_usb.py pl2303
#lsmod | grep usbserial

import os
import sys
from subprocess import Popen, PIPE
import fcntl
driver = "pl2303" #sys.argv[-1]
print ("resetting driver:", driver)
USBDEVFS_RESET= 21780

try:
    lsusb_out = Popen("lsusb | grep -i %s"%driver, shell=True, bufsize=64, stdin=PIPE, stdout=PIPE, close_fds=True).stdout.read().strip().split()
    bus = lsusb_out[1]
    device = lsusb_out[3][:-1]
    f = open("/dev/bus/usb/%s/%s"%(bus, device), 'w', os.O_WRONLY)
    fcntl.ioctl(f, USBDEVFS_RESET, 0)
except Exception as msg:
    print ("failed to reset device:", msg)