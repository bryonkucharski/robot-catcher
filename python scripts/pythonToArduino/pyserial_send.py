import serial # (pip install pySerial)

# Replace with specific port name & baud rate
serial_port = serial.Serial('/dev/cu.usbmodem1411', 9600)

while(1):
	msg = input('Enter msg: ')
	# Message must be cast to byte format
	serial_port.write(str(msg).encode())