import cv2
import numpy as np
import collections
import sys
import time
sys.path.append("../../") #go back to vision folder
import discretize_vision as v


# Capture from webcam
#1 for usb webcam
#0 for integrated webcam
cap = cv2.VideoCapture(1)

scale_factor = 1
first_frame = True
grid_dim = (5, 8)

# Enumerations to ease tuple access 
x = 0
y = 1


while (True):
	start = time.time()
	cell = v.getCell(cap,scale_factor,first_frame,grid_dim, draw_frame=True)
	end = time.time()
	print(end-start)
	if cv2.waitKey(1) & 0xFF == ord('q'):
	    break

cap.release()
cv2.destroyAllWindows()


# # Convert to grayscale
# img2 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
# # Convert gray back to 3-channel BGR to maintain uniform dimensionality when plotting 
# img2 = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR)

