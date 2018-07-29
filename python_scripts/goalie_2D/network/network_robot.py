'''
Bryon Kucharski
Summer 2018

Real Robot and a neural network with a 2D robot

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
from DQNAgent import DQNAgent
import numpy as np

# Replace with specific port name & baud rate#
photogate_serial = serial.Serial('COM11', 9600, timeout=0)
robot_serial = serial.Serial('COM7', 9600, timeout=5)


def move_robot(x, y):
	# Serial write section
	msg = str(x) + "," + str(y)
	robot_serial.write(str.encode(msg))

def readFromPhotogate():
    val = photogate_serial.read(1)
    if val != b'':
        return ord(val) + 1
    else:
        return -1

def update_current_position(action,x,y):
    new_x = x
    new_y = y

    if action == 1: #Left
        if x != 1:
            new_x = x - 1
            new_y = y
    elif action == 2: #Right
        if x != 5:
            new_x = x + 1
            new_y = y
    elif action == 3: #Up
        if y != 3:
            new_x = x 
            new_y = y + 1
    elif action == 4: #Down
        if y != 1:
            new_x = x
            new_y = y - 1
    
    return new_x, new_y
    


agent = DQNAgent(#state_size =num_grid_y*num_grid_x,
                state_size =4, 
                action_size = 5,
                gamma = 0.95,
                epsilon = 0.01,
                epsilon_min = 0.01,
                epsilon_decay = 0.995,
                learning_rate = 0.001, 
                model_type = 'DeepModel'
                )

agent.load("models/10000_goalie_network_5x3.h5")


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
scale_factor = 0.5
first_frame = True
grid_dim = (5, 8)

robot_x = 3
robot_y = 2
moveHomeFlag = True
start = 0

while(True):
    end = time.time()

    thrust = readFromPhotogate()

    ball_x = v.get_cell_2(cap,scale_factor,first_frame,grid_dim, draw_frame=True)
 
    #print(robot_x,robot_y,ball_x)
    if moveHomeFlag and (end-start) > 2:
        print("Homing")
        #robot.goToPosition(3,2)
        robot_x = 3
        robot_y = 2
        #robot.drawRobot()
        moveHomeFlag = False
        continue
    

    #IF PHOTOGATE IS DETECTED, PREDICT ALL
    if moveHomeFlag == False and thrust != -1 and len(ball_x) > 0:
        print(thrust)
        #KEEP MAKING PREDICITONS FOR ONE SECOND???
        state = [robot_x,ball_x[0],robot_y, thrust]
        print(state)

        action = agent.predict(np.array([state]))

        #agent was flipped when training 
        if action == 3:
            action = 4
        elif action == 4:
            action = 3

        print("CURRENT ROBOT POSITION: " + str(robot_x) + ", " + str(robot_y))
        print("HARDCODED ROBOT STATE POSITION: " + str(ball_x[0])  + "," + str(thrust))
        print("PREDICTION FOR STATE: "+ str(action) )
    
        #robot.update_position(action)
        robot_x, robot_y = update_current_position(action,robot_x,robot_y)
        print("NEW ROBOT STATE: " + str(robot_x) + ", " + str(robot_y))
 
        move_robot(robot_x,robot_y)
        start = time.time()
        #robot.drawRobot()
        moveHomeFlag = True

        #robot.drawRobot()

    #IF JUST X IS DETECTED, TAKE PREDICTION WITH THRUST = 1 (will favor middle position)
    
    if(len(ball_x) > 0):
        print("updating x")
        state = [robot_x,ball_x[0],robot_y, 2]
        time3 = time.time()
        action = agent.predict(np.array([state]))
        end3 = time.time()
     
        if action == 3:
            action = 4
        elif action == 4:
            action = 3
        robot_x, robot_y = update_current_position(action,robot_x,robot_y)
        #print("HARDCODED POSITION: " + str(ball_x[0])  + "," + str(1))
        #print("PREDICTION FOR STATE: " + str(robot_x) + ", " + str(ball_x[0]) + ", " + str(robot_y) +", " + str(1) + " ACTION: " + str(action) )
        #print("NEW STATE: " + str(robot_x) + ", " + str(robot_y))
        #this will work in mixed robot but not real robot (since we need to wait for the robot to move, cant move every iteration)
        #robot.update_position(action)
        #robot.drawRobot()
    
     
    
    robot.drawRobot()