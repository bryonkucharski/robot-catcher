import numpy as np
from PIL import ImageGrab
import cv2
import time


def get_screenshot(x_start,y_start,x_end,y_end):
    printscreen =  np.array(ImageGrab.grab(bbox=(x_start,y_start,x_end,y_end)))
    img = cv2.cvtColor(printscreen, cv2.COLOR_BGR2RGB)
    return img
    #cv2.imshow('window', img)
    #cv2.waitKey(0)

def pixelToCell(colorImage, cell_LengthX, cell_LengthY, debug=False):
    
    # A function to read an image. The first parameter is the image file. Should be in the same location as the script.
	# Second parameter is a flag to specify how the image should be read.
	# 0 is gray scale
	# 1 is unchanged

    img = cv2.cvtColor(colorImage,cv2.COLOR_RGB2GRAY)

	# define range of gray color in HSV
    lower_green = np.array([0,0,0])
    upper_green = np.array([0,255,0])

	#Call InRange for black and white image
	# Threshold the HSV image to get only green colors
    mask = cv2.inRange(colorImage, lower_green, upper_green)
	
	# Bitwise-AND mask and original image
    res = cv2.bitwise_and(colorImage,colorImage, mask = mask)
	
    gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    bw_img = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)[1]
	#Function to identify the shape of a circle.
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 20, param1 = 50, param2 = 30, minRadius = 0, maxRadius = 0)
	
    circles = np.uint16(np.around(circles))
	#the number of detected circles
	#print(len(circles))

	#cv2.imshow('the mask', gray)
	
    for i in circles[0,:]:
	    #draw the outer green circles on the image you specify.
	    center = (i[0], i[1])
	    cv2.circle(colorImage, center, i[2], (0, 0, 255), 2)
		
		#print(center)#prints the coordinate
		#75 is the width of a square
		
		#truncating the division.
		#dividing it by the cell_length, for example each cell composes of 75 pixels by 75 pixels
	    cellX = np.trunc(center[0]/cell_LengthX)
	    cellY = np.trunc(center[1]/cell_LengthY)
		
		#print(cellX, cellY)
		
		#draw the red dot at the center of the circle
	    cv2.circle(colorImage, (i[0], i[1]), 2, (0, 0, 255), 3)
	
		#Instantiate a small window labeled Detected Circles with the cimg on display.	
	    if debug:
		    cv2.imshow('Detected Circles', colorImage)
			#Wait until you press a key
		    cv2.waitKey(1)
		    #cv2.destroyAllWindows()

    return int(cellX), int(cellY)
