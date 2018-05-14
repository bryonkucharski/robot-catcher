import keyboard #pip install keyboard
import serial #pip install pySerial

serial_port = serial.Serial('COM4', 9600, timeout=0)

def continous_keypress(e):
	if(e.event_type == "down"):
		msg = keyboard._pressed_events #returns a dict
		print(list(msg)[0]) #convert key to int
		serial_port.write(msg)
		print(serial.read())
		

keyboard.hook(continous_keypress)
keyboard.wait()

