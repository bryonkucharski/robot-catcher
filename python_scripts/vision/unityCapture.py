import cv2
import numpy as np
import collections
from PIL import ImageGrab
import time
import discretize_vision as v


start = time.time()#start the timer
first_frame = True
grid_dim = (5,10)

while (True):
	#start = time.time()#start the timer
	end = time.time() #end the timer
	total = end - start #get elapsed time
	
	if total > .07:
		start = time.time() #restart the timer
		'''
		#Lets take a selection of the screen and capture it. Set this to the dimensions of the unity environment.
		screenImage = ImageGrab.grab(bbox=(897, 116, 952, 679))#(X, Y) starting position ; (W, H) ending position
		#screenImage = ImageGrab.grab()
		screenImage_array = np.array(screenImage)#convert the image to a numpy array
		frame = cv2.cvtColor(screenImage_array, cv2.COLOR_BGR2GRAY)
		cv2.imshow("Unity Environment", frame) #Name the window and display it
		cv2.waitKey(0)
		cv2.destroyAllWindows();
		#Original Sphere Unity size was 0.0686
		'''
		
		# Capture frame
		#ret, img1 = cap.read()
		tack = 25;#Expand the screen capture area incase the ball spawns on the edge of the ramp
		screenImage = ImageGrab.grab(bbox=(305, 157, 580, 597))#(X, Y) starting position ; (W, H) ending position
		
		img1 = np.array(screenImage)#convert the image to a numpy array
		
		# Resize to ease processing time, save screen space for plotting multiple frames
		#img1 = cv2.resize(img1, (0,0), fx=scale_factor, fy=scale_factor)

		if (first_frame):
			img_dim = img1.shape[1], img1.shape[0]
			print(img1.shape)
			cell_dim = v.get_cell_dimensions(img_dim, grid_dim)
			first_frame = False

		circle_center, radius = v.get_circle(img1)
		cell = v.pixel_to_cell(circle_center, cell_dim)
		
		print("Cell Location: " + str(cell))
		
		img2 = v.build_img2(img1, img_dim, grid_dim, cell_dim, circle_center, radius)
		img3 = v.build_img3(img_dim, grid_dim, cell_dim, cell)

		# Change to hstack() for horizontal plotting
		# Change to vstack() for vertical plotting
		total = np.hstack((img1, img2, img3))
			
		cv2.imshow('image', total)

		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
		
	#end = time.time() #end the timer
	#total = end - start #get elapsed time
	#print(total)

#cap.release()
cv2.destroyAllWindows()


# # Convert to grayscale
# img2 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
# # Convert gray back to 3-channel BGR to maintain uniform dimensionality when plotting 
# img2 = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR)

