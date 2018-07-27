'''
Bryon Kucharski
Summer 2018

Uses mixed reality (real ramp and virtual robot) and a q table with a 2D robot

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
from virtual_robot import virtual_robot
from qlearning_agent import rl_agent
import random
import discretize_vision as v
import time

# Replace with specific port name & baud rate#
serial_port = serial.Serial('COM11', 9600, timeout=0)


def readFromPhotogate():
    val = serial_port.read(1)
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
    

def get_ball_x():
    '''VISON CODE HERE'''
    return -1

def get_reward(robot_x, robot_y, ball_x,thrust ):
    '''
    return DISTANCEFORMULA
    '''

    return -1


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

robot_spaces_x = 5 #grids
robot_spaces_y = 3 #grids
gantry_plate_size = 2.6771654 #inches
robot = virtual_robot(
                    WIDTH = 1680,#width of monitor
                    HEIGHT = 1050, #height of monitor
                    dpi = 99, #dpi of the monitor
                    roi_x = 12, #inches, this is how wide in x you want the robot range to be, the black part of the virtual robot inches
                    roi_y = 8, #inches
                    number_of_states_x = robot_spaces_x, #0,1,2,3,4
                    number_of_states_y = robot_spaces_y, #0,1,2
                    initial_x = 2, #middle x
                    initial_y = 1 #middle y
                )

#agent.init_q_table()

#VISION constants
cap = cv2.VideoCapture(1)
scale_factor = 1.0
first_frame = True
grid_dim = (5, 8)

while(True):
    space = readFromPhotogate()
    x = v.get_cell_2(cap,scale_factor,first_frame,grid_dim, draw_frame=True)
    
    if len(x) > 0:
        print(x)

    if space != -1:
        #print(x)
        robot.goToPosition(x[0],space)
        print(x[0],space)
        robot.drawRobot()
        time.sleep(2)
        robot.goToPosition(3,2)
    
    #else:
    #   robot.goToPosition(2,1)

    robot.drawRobot()
    '''
    #state = getState(robot)
    #if state[1] != -1:
    #    print(state)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    
    
    ####Get the State####
    state = getState(robot)
    if len(state[0]) < 0: //if no ball x detected
        continue

    ####Get the Action####
    action = agent.get_action(str(state))
    robot.update_position(action)
    
    #####Get the Reward####
    reward = get_reward(robot_x, robot_y, ball_x,thrust )

    ####Get the State Prime####
    state_prime = getState(robot)
    if len(state_prime[0]) < 0: //if no ball x detected
        continue

    print(str(state) + ", " + str(action) + ", " + str(reward) + ", " + str(state_prime))

    #update q table
    agent.update(str(state),action,reward,str(state_prime))
    '''
    




