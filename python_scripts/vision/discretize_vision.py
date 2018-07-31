import cv2
import numpy as np
import collections # For deque

# Enumerations to ease tuple access 
x = 0
y = 1

def get_cell_2(cap, scale_factor, first_frame, grid_dim, draw_frame = False):
    # Capture frame
	ret, img1 = cap.read()
	#cv2.imshow('image', img1)
	#print(img1)
	#img1 = img1[179:179, 179:170]
	# Resize to ease processing time, save screen space for plotting multiple frames
	img1 = cv2.resize(img1, (0,0), fx=scale_factor, fy=scale_factor)
	
	# Hard coded crop - should figure out better method
	img1 = img1[:, int(round(192*scale_factor)):int(round(383*scale_factor))]
	#img1 = img1[:,206:380]
	#img1 = img1[y0:y1, x0:x1] 


	if (first_frame):
		img_dim = img1.shape[1], img1.shape[0]
		cell_dim = get_cell_dimensions(img_dim, grid_dim)
		#print(img_dim)
		first_frame = False


	binary_img = bgr_img_to_binary(img1, 250)
	circle_center, radius = get_circle_2(binary_img)
	cell = pixel_to_cell(circle_center, cell_dim)

	if(draw_frame):
		# Reconvert back to BGR
		binary_img = cv2.cvtColor(binary_img, cv2.COLOR_GRAY2RGB)
		img2 = build_img2(binary_img, img_dim, grid_dim, cell_dim, circle_center, radius)

		# Change to vstack() for veritical plotting
		total = np.hstack((img1, img2))
		cv2.imshow('image', total)

	return cell
	
def bgr_img_to_binary(img, threshold_level):
	grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	filter_size = 2 # TODO: Make filter size adaptive?
	blur_img = cv2.blur(grey_img, (filter_size,filter_size))
	ret, binary_img = cv2.threshold(blur_img, threshold_level, 255, cv2.THRESH_BINARY)

	return binary_img

def get_circle_2(img, debug = False):
	columns = np.sum(img,axis=0)
	sum = np.sum(columns)

	if sum == 0:
    		return (), 0
	else:
		return (np.argmax(columns),0),10
	
	#for i in range(0, img.shape[x]):
	#	for j in range(0, img.shape[y]):
	#		if pixel_is_white(img[i, j]):
	#			# print(i,j)
	#			return (j, i), 10
	#return (), 0
	#return (2,3), 0
	

def pixel_is_white(value):
	if value == 255:
		return True
	return False






def getCell(cap, scale_factor, first_frame, grid_dim, draw_frame = False):
    # Capture frame
	ret, img1 = cap.read()

	# Resize to ease processing time, save screen space for plotting multiple frames
	img1 = cv2.resize(img1, (0,0), fx=scale_factor, fy=scale_factor)

	# Hard coded crop - should figure out better method
	img1 = img1[0:265, 240:351]

	if (first_frame):
		img_dim = img1.shape[1], img1.shape[0]
		cell_dim = get_cell_dimensions(img_dim, grid_dim)
		#print(img_dim)
		first_frame = False

	circle_center, radius = get_circle(img1)
	cell = pixel_to_cell(circle_center, cell_dim)

	if(draw_frame):
		img2 = build_img2(img1, img_dim, grid_dim, cell_dim, circle_center, radius)
		#img3 = build_img3(img_dim, grid_dim, cell_dim, cell)

		# Change to vstack() for veritical plotting
		total = np.hstack((img1, img2))
		cv2.imshow('image', total)

	return cell


def get_cell_dimensions(img_dim, grid_dim):
	return int(round(img_dim[x]/grid_dim[x])), int(round(img_dim[y]/grid_dim[y]))


# TODO Understand all HoughCircle parameters, account for no circles etc
def get_circle(img, debug = False):
	grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	# TODO: Make filter size adaptive?
	filter_size = 4

	# Keep calling HoughCircles() and adjusting filter size until only 1 or 0 circles are returned
	while (1):
		blur_img = cv2.blur(grey_img, (filter_size,filter_size))
		circles = cv2.HoughCircles(blur_img, cv2.HOUGH_GRADIENT, 1, 20, param1 = 50, param2 = 30, minRadius = 1, maxRadius = 50)

		# if circles is None:
		# 	print(filter_size)
		# 	filter_size = filter_size - 1
		# 	print(filter_size)

		# 	if filter_size == 0:
		# 		print("\nNo circles found")
		# 		return (0,0), 0

		# 	continue

		if circles is None:
			return (), 0

		circles = np.uint16(np.around(circles))
		num_circles = circles.shape[1]

		if debug:
			print("Filter size: " + str(filter_size) + "x" + str(filter_size) + "\tNumber of circles: " + str(num_circles))

		if (num_circles > 1):
			filter_size = filter_size + 1
		elif (num_circles == 1):
			if debug:
				print(filter_size)
			break

	center = (circles[0,0,0], circles[0,0,1])
	radius = circles[0,0,2]
	#print(str(num_circles) + ' ' + str(radius) + ' ' + str(center))
	#center, radius = temporal_filter(center, radius)

	# THIS IS A QUICK FIX...FIND ROOT CAUSE
	if radius == 0:
		return (), 0

	return center, radius

# More elegent way to declare?
center_buffer = collections.deque([], 2)
radius_buffer = collections.deque([], 2)

def temporal_filter(center, radius):
	tau = 0.1

	center_buffer.append(center)
	radius_buffer.append(radius)
	
	if len(center_buffer) == 2:
		filtered_center_x = weighted_average(center_buffer[1][x], center_buffer[0][x], tau)
		filtered_center_y = weighted_average(center_buffer[1][y], center_buffer[0][y], tau)
		filtered_radius = weighted_average(radius_buffer[1], radius_buffer[0], tau)
		return (filtered_center_x, filtered_center_y), filtered_radius
	else:
		return center, radius
		

def weighted_average(t0, t1, tau):
	return int(round(t0*(1-tau) + t1*tau))


def pixel_to_cell(circle_center, cell_dim):
	if circle_center:
		return int(circle_center[x]/cell_dim[x]) + 1, int(circle_center[y]/cell_dim[y]) + 1
	else:
		return ()


def draw_gridlines(img, img_dim, grid_dim, cell_dim):
	# Draw vertical lines
	for i in range(1,grid_dim[x]):
		cv2.line(img, (cell_dim[x]*i,0), (cell_dim[x]*i,img_dim[y]), (0,0,255), 2)

	# Draw horizontal lines
	for i in range(1,grid_dim[y]):
		cv2.line(img, (0,cell_dim[y]*i), (img_dim[x],cell_dim[y]*i), (0,0,255), 2)


def draw_circle(img, center, radius):
	if radius:
		cv2.circle(img, center, radius, (0, 255, 0), 5)
		cv2.circle(img, center, 2, (0, 255, 0), 3)


def build_blank_img(img_dim):
	size = (img_dim[y], img_dim[x], 3)
	return np.ones(size, np.uint8) * 255


def fill_cell(img, cell_dim, cell):
	cv2.rectangle(img, (cell_dim[x]*cell[x],cell_dim[y]*cell[y]), (cell_dim[x]*(cell[x]+1),cell_dim[y]*(cell[y]+1)), (0,255,0), -1)


def build_img2(img1, img_dim, grid_dim, cell_dim, circle_center, radius):
	img2 = img1.copy()
	draw_gridlines(img2, img_dim, grid_dim, cell_dim)
	draw_circle(img2, circle_center, radius)
	return img2


def build_img3(img_dim, grid_dim, cell_dim, cell):
	img3 = build_blank_img(img_dim)
	if cell:
		fill_cell(img3, cell_dim, cell)
	draw_gridlines(img3, img_dim, grid_dim, cell_dim)
	return img3
