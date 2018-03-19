import cv2
import numpy as np
import collections
import sys
sys.path.append("../../") #go back to vision folder
import discretize_vision as v


# Capture from webcam
cap = cv2.VideoCapture(0)

scale_factor = 0.25
first_frame = True
grid_dim = (8, 5)

# Enumerations to ease tuple access 
x = 0
y = 1


while (True):

	# Capture frame
	ret, img1 = cap.read()

	# Resize to ease processing time, save screen space for plotting multiple frames
	img1 = cv2.resize(img1, (0,0), fx=scale_factor, fy=scale_factor)

	if (first_frame):
		img_dim = img1.shape[1], img1.shape[0]
		cell_dim = v.get_cell_dimensions(img_dim, grid_dim)
		print(img_dim)
		first_frame = False

	circle_center, radius = v.get_circle(img1)
	cell = v.pixel_to_cell(circle_center, cell_dim)

	img2 = v.build_img2(img1, img_dim, grid_dim, cell_dim, circle_center, radius)
	img3 = v.build_img3(img_dim, grid_dim, cell_dim, cell)

	# Change to hstack() for horizontal plotting
	total = np.vstack((img1, img2, img3))
		
	cv2.imshow('image', total)

	if cv2.waitKey(1) & 0xFF == ord('q'):
	    break

cap.release()
cv2.destroyAllWindows()


# # Convert to grayscale
# img2 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
# # Convert gray back to 3-channel BGR to maintain uniform dimensionality when plotting 
# img2 = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR)