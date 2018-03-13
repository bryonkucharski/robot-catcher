# Usage: python discretize.py <filename> <debug flag>

import cv2
import numpy as np
from matplotlib import pyplot as plt
from math import ceil
import sys


# Enumerations to ease tuple access 
x = 0
y = 1


def discretize_ball_img(filename, debug):
	img1 = open_img(filename)

	img_dim = img1.shape[1], img1.shape[0]
	grid_dim = (5, 8)
	cell_dim = get_cell_dimensions(img_dim, grid_dim)

	circle_center, radius = get_circle(img1)

	cell = pixel_to_cell(circle_center, cell_dim)

	if (debug):
		print_all_coordinates(img_dim, grid_dim, cell_dim, circle_center, cell)
		img2 = build_img2(img1, img_dim, grid_dim, cell_dim, circle_center, radius)
		img3 = build_img3(img_dim, grid_dim, cell_dim, cell)
		show_subplots(img1, img2, img3, filename)
	else:
		print(circle_center)


def get_cell_dimensions(img_dim, grid_dim):
	return int(round(img_dim[x]/grid_dim[x])), int(round(img_dim[y]/grid_dim[y]))


# TODO Understand all HoughCircle parameters
def get_circle(img):
	grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	filter_size = 10

	# Keep calling HoughCircles() and adjusting filter size until only 1 or 0 circles are returned
	while (1):
		blur_img = cv2.blur(grey_img, (filter_size,filter_size))

		circles = cv2.HoughCircles(blur_img, cv2.HOUGH_GRADIENT, 1, 20, param1 = 50, param2 = 30, minRadius = 25, maxRadius = 175)
		circles = np.uint16(np.around(circles))

		num_circles = circles.shape[1]

		#print("Filter size: " + str(filter_size) + "x" + str(filter_size) + "\tNumber of circles: " + str(num_circles))

		if (num_circles == 1):
			break

		if (num_circles > 1):
			filter_size = filter_size + 1
		else:
			filter_size = filter_size - 1

		if (filter_size == 0):
			print("\nNo circles found")
			return (0,0), 0

	center = (circles[0,0,0], circles[0,0,1])
	radius = circles[0,0,2]

	return center, radius


def pixel_to_cell(circle_center, cell_dim):
	return int(circle_center[x]/cell_dim[x]), int(circle_center[y]/cell_dim[y])


def draw_gridlines(img, img_dim, grid_dim, cell_dim):
	# Draw vertical lines
	for i in range(1,grid_dim[x]):
		cv2.line(img, (cell_dim[x]*i,0), (cell_dim[x]*i,img_dim[y]), (0,0,255), 2)

	# Draw horizontal lines
	for i in range(1,grid_dim[y]):
		cv2.line(img, (0,cell_dim[y]*i), (img_dim[x],cell_dim[y]*i), (0,0,255), 2)


def draw_circle(img, center, radius):
	cv2.circle(img, center, radius, (0, 255, 0), 5)
	cv2.circle(img, center, 2, (0, 255, 0), 3)


def build_blank_img(img_dim):
	size = (img_dim[y], img_dim[x], 3)
	return np.ones(size, np.uint8) * 255


def fill_cell(img, cell_dim, cell):
	cv2.rectangle(img, (cell_dim[x]*(cell[x]-1),cell_dim[y]*(cell[y]-1)), (cell_dim[x]*cell[x],cell_dim[y]*cell[y]), (0,255,0), -1)


def show_subplots(img1, img2, img3, filename):
	plt.subplot(131),plt.imshow(cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)),plt.title('Original')
	plt.xticks([]), plt.yticks([])

	plt.subplot(132),plt.imshow(cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)),plt.title('Grid Overlay')
	plt.xticks([]), plt.yticks([])

	plt.subplot(133),plt.imshow(cv2.cvtColor(img3, cv2.COLOR_BGR2RGB)),plt.title('Discretized')
	plt.xticks([]), plt.yticks([])

	plt.savefig(filename[2:])
	plt.show()


def print_all_coordinates(img_dim, grid_dim, cell_dim, circle_center, cell):
	print("\nImage dimensions: " + str(img_dim))
	print("Grid dimensions: " + str(grid_dim))
	print("Cell dimensions: " + str(cell_dim))
	print("Circle center: " + str(circle_center))
	print("Cell: " + str(cell))


def build_img2(img1, img_dim, grid_dim, cell_dim, circle_center, radius):
	img2 = img1.copy()
	draw_gridlines(img2, img_dim, grid_dim, cell_dim)
	draw_circle(img2, circle_center, radius)
	return img2


def build_img3(img_dim, grid_dim, cell_dim, cell):
	img3 = build_blank_img(img_dim)
	fill_cell(img3, cell_dim, cell)
	draw_gridlines(img3, img_dim, grid_dim, cell_dim)
	return img3


def open_img(filename):
	img = cv2.imread(filename)

	# Poor doccumentation on how to error check for failed read
	# if (img1.empty()):
	# 	print("Could not find the supplied image")
	# 	sys.exit()

	return img


def main():
	if (len(sys.argv) != 3):
		print("\nUsage: pythonw " + sys.argv[0] + " <filename> <debug mode>")
		sys.exit()

	filename, debug = sys.argv[1], int(sys.argv[2])

	if (debug not in set([0, 1])):
		print("\nDebug bit must be set to 0 or 1. Forcing debug mode.")
		debug = 1

	discretize_ball_img(filename, debug)


if __name__== "__main__":
  main()
	
