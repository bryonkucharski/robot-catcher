import cv2
import numpy as np
import collections
import sys
import sys
sys.path.append("../../") #go back to vision folder
import discretize_vision as v



filename = sys.argv[1]
cap = cv2.VideoCapture(filename) 

frame_counter = 0
scale_factor = 0.25
first_frame = True
grid_dim = (5, 8)

while(True):
    
    # Capture frame
	ret, img1 = cap.read()

	# Resize to ease processing time, save screen space for plotting multiple frames
	img1 = cv2.resize(img1, (0,0), fx=scale_factor, fy=scale_factor)

	if (first_frame):
		img_dim = img1.shape[1], img1.shape[0]
		cell_dim = v.get_cell_dimensions(img_dim, grid_dim)
		print(img_dim)
		first_frame = False

	frame_counter += 1

	# Reset the capture and the frame_counter when last frame is reached
	if frame_counter == cap.get(cv2.CAP_PROP_FRAME_COUNT):
	    frame_counter = 0 
	    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

	circle_center, radius = v.get_circle(img1)
	cell = v.pixel_to_cell(circle_center, cell_dim)
	if cell:
		print(cell)
	else:
		print()

	img2 = v.build_img2(img1, img_dim, grid_dim, cell_dim, circle_center, radius)
	img3 = v.build_img3(img_dim, grid_dim, cell_dim, cell)

	# Change to vstack() for vertical plotting
	total = np.hstack((img1, img2, img3))
		
	cv2.imshow('image', total)
    
    # The arg on waitKey() affects the playback speed but not sure what the unit is
	if cv2.waitKey(50) & 0xFF == ord('q'):
	    break
	if cv2.waitKey(20) & 0xFF == ord('p'):
	    while(1):
	    	if cv2.waitKey(20) & 0xFF == ord('p'):
	    		break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()