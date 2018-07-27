'''
Bryon Kucharski
Summer 2018

Real Robot and a q table with a 2D robot

'''
import os, sys, inspect
parent_dir_name = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
fldr = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../../robot")))
if fldr not in sys.path:
    sys.path.insert(0, fldr)
fldr = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../../socket")))
if fldr not in sys.path:
    sys.path.insert(0, fldr)
fldr = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../../rl")))
if fldr not in sys.path:
    sys.path.insert(0, fldr)
fldr = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../../vision")))
if fldr not in sys.path:
    sys.path.insert(0, fldr)    

import cv2
import serial # (pip install pySerial)
from qlearning_agent import rl_agent
import random
import discretize_vision as v
import time
from virtual_robot import virtual_robot

# Replace with specific port name & baud rate#
photogate_serial = serial.Serial('COM11', 9600, timeout=0)
robot_serial = serial.Serial('COM7', 9600, timeout=5)


def move_robot(x, y):
	# Serial write section
	msg = str(x) + "," + str(y)
	print ("\nPython value sent: \t" + msg)
	robot_serial.write(str.encode(msg))

def readFromPhotogate():
    val = photogate_serial.read(1)
    if val != b'':
        return ord(val) + 1
    else:
        return -1

def getState(robot):
    
    photogate = readFromPhotogate()
    if photogate >= 0:
        ball_y = photogate
    else:
        ball_y = 1

    ball_x = get_ball_x()

    robot_pos = robot.get_goalie_pos()

    return ball_x,photogate,robot_pos[0],robot_pos[1]
    


#RL constants
EPSILON =       1    # greedy police
ALPHA =         0.5     # learning rate
GAMMA =         1       # discount 

agent = rl_agent(
                list(range(5)), #STAY,LEFT,RIGHT, UP, DOWN
                GAMMA,
                ALPHA,
                EPSILON
               )

agent.init_q_table()

robot = virtual_robot(
                    WIDTH = 1680,#width of monitor
                    HEIGHT = 1050, #height of monitor
                    dpi = 99, #dpi of the monitor
                    roi_x = 12, #inches, this is how wide in x you want the robot range to be, the black part of the virtual robot inches
                    roi_y = 8, #inches
                    number_of_states_x = 5, #0,1,2,3,4
                    number_of_states_y = 3, #0,1,2
                    initial_x = 2, #middle x
                    initial_y = 1 #middle y
                )


#VISION constants
cap = cv2.VideoCapture(1)
scale_factor = 1.0
first_frame = True
grid_dim = (5, 8)

start = 0
moveHomeFlag = False
while(True):
    end = time.time()

    space = readFromPhotogate()
    x = v.get_cell_2(cap,scale_factor,first_frame,grid_dim, draw_frame=True)
    print(space,x)

    if moveHomeFlag and (end-start) > 2:
        move_robot(3,2-1)
        moveHomeFlag = False
        continue
    
    if space != -1:
        #print(x)
        start = time.time()
        moveHomeFlag = True
        print(x[0],space)
        move_robot(x[0],space-1)
        print(x[0],space)
        robot.goToPosition(x[0],space)

        #time.sleep(2)
        #move_robot(3,2)
    
    robot.drawRobot()


    
    
