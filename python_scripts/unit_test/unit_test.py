import serial # (pip install pySerial)
import struct

serial_port = serial.Serial('COM7', 9600, timeout=0)

#for i in range(0,100):
while True:
    serial_port.write(b'1')
    x = serial_port.readline()
    print(x)