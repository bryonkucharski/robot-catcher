import cv2
import numpy as np
import collections


def discretize_ball_img(filename, debug):
	img1 = open_img(filename)

	img_dim = img1.shape[1], img1.shape[0]
	grid_dim = (8, 5)
	cell_dim = get_cell_dimensions(img_dim, grid_dim)

	circle_center, radius = get_circle(img1)

	cell = pixel_to_cell(circle_center, cell_dim)

	if (debug):
		print_all_coordinates(img_dim, grid_dim, cell_dim, circle_center, cell)
		img2 = build_img2(img1, img_dim, grid_dim, cell_dim, circle_center, radius)
		img3 = build_img3(img_dim, grid_dim, cell_dim, cell)
		show_subplots(img1, img2, img3)
	else:
		print(circle_center)


def get_cell_dimensions(img_dim, grid_dim):
	return int(round(img_dim[x]/grid_dim[x])), int(round(img_dim[y]/grid_dim[y]))


# TODO Understand all HoughCircle parameters, account for no circles etc
def get_circle(img):
	grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	filter_size = 4

	# Keep calling HoughCircles() and adjusting filter size until only 1 or 0 circles are returned
	while (1):
		#print("While")
		blur_img = cv2.blur(grey_img, (filter_size,filter_size))
		circles = cv2.HoughCircles(blur_img, cv2.HOUGH_GRADIENT, 1, 20, param1 = 50, param2 = 30, minRadius = 25, maxRadius = 100)

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

		#print("Filter size: " + str(filter_size) + "x" + str(filter_size) + "\tNumber of circles: " + str(num_circles))

		if (num_circles > 1):
			filter_size = filter_size + 1
		elif (num_circles == 1):
			print(filter_size)
			break

	center = (circles[0,0,0], circles[0,0,1])
	radius = circles[0,0,2]
	center, radius = temporal_filter(center, radius)

	return center, radius

center_buffer = collections.deque([], 2)
radius_buffer = collections.deque([], 2)

def temporal_filter(center, radius):
	tau = 0.1

	center_buffer.append(center)
	radius_buffer.append(radius)
	
	if len(center_buffer) == 2:
		filtered_center_x = int(round(center_buffer[1][x]*(1-tau) + center_buffer[0][x]*tau))
		filtered_center_y = int(round(center_buffer[1][y]*(1-tau) + center_buffer[0][y]*tau))
		filtered_radius = int(round(radius_buffer[1]*(1-tau) + radius_buffer[0]*tau))
		return (filtered_center_x, filtered_center_y), filtered_radius
	else:
		return center, radius
		

def pixel_to_cell(circle_center, cell_dim):
	if circle_center:
		return int(circle_center[x]/cell_dim[x]), int(circle_center[y]/cell_dim[y])
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
		cell_dim = get_cell_dimensions(img_dim, grid_dim)
		print(img_dim)
		first_frame = False

	circle_center, radius = get_circle(img1)
	cell = pixel_to_cell(circle_center, cell_dim)

	img2 = build_img2(img1, img_dim, grid_dim, cell_dim, circle_center, radius)
	img3 = build_img3(img_dim, grid_dim, cell_dim, cell)

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