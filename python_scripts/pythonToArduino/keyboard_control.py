import keyboard #pip install keyboard
import serial #pip install pySerial

serial_port = serial.Serial('/dev/cu.usbmodem1411', 9600)

def continous_keypress(e):
	if(e.event_type == "down"):
		msg = keyboard._pressed_events #returns a dict
		print(list(msg)[0]) #convert key to int
		serial_port.write(str(msg).encode())

keyboard.hook(continous_keypress)
keyboard.wait()