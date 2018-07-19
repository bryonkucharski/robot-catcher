'''
    Bryon Kucharski
    Wentorth Institute of Technology
    Summer 2018
    
    A Tablular method of Reinforement learning with a real world one dimensional robot

'''
import os, sys, inspect
import random
import time
from PIL import ImageGrab
import numpy as np
import cv2
import serial # (pip install pySerial)
import struct

# Replace with specific port name & baud rate
serial_port = serial.Serial('COM7', 9600, timeout=0)

#this is just to import rl agent from a different folder
rl_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../rl")))
if rl_subfolder not in sys.path:
    sys.path.insert(0, rl_subfolder)

from qlearning_agent import rl_agent

vision_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../vision")))
if vision_subfolder not in sys.path:
    sys.path.insert(0, vision_subfolder)

import discretize_vision as v

#VISION constants
cap = cv2.VideoCapture(1)
scale_factor = 0.6
first_frame = True
grid_dim = (5, 5)


def get_reward_vision(robot_pos, ball_pos):
    if (robot_pos == ball_pos):
        return 1
    else:
        return -0.1 * (abs(robot_pos - ball_pos))
    
def resetRobot():
    #sendToRobot(17)
    sendToRobot(17)

def sendToRobot(msg):
    #30 is right
    #32 is left
	serial_port.write(struct.pack('>B', int(msg)))


def actionToCommand(action):
    """
    Converts the  action of the robot to the interger number the arduino will understand

    Args:
        action: 0 stay, 1 left, 2 right
    
    Returns:
        The interger command to send through serial to the robot
    """

    if int(action) == 1:
        return 32
    elif int(action) == 2:
        return 30

def positionToCommand(new_robot_pos):
    
    """
    Converts the new position of the robot to the interger number the arduino will understand

    Args:
        new_robot_pos: the new robot position that the robot will be told to move to
    
    Returns:
        The interger command to send through serial to the robot
    """

    if new_robot_pos == 0:
        return 16
    elif new_robot_pos == 1:
        return 17
    elif new_robot_pos == 2:
        return 18
    elif new_robot_pos == 3:
        return 19
    elif new_robot_pos == 4:
        return 20
 

def checkValidMove(robot_pos, action):
    """
    Determines if requested move is within robot bounds

    Args:
        robot_pos: current position of the robot
        action: action that is being performed
    
    Returns:
        True If the action is allowed to be performed
        OR
        False If the action is not allowed to be performed
    """
    if (robot_pos == 0):
        if int(action) == 1:
            return False
    if (robot_pos == 4):
        if int(action) == 2:
            return False
    return True

def updateRobotPosition(robot_pos, action):
    """
    Updates the position of the robot in the software point of view
    Note - still need to send the action to the robot

    Args:
        robot_pos: current position of the robot
        action: action that is being performed
    
    Returns:
        The new robot position based on the action
    """
    if int(action) == 1:
        robot_pos = robot_pos - 1
    elif int(action) == 2:
        robot_pos = robot_pos + 1

    return robot_pos

#RL constants
EPSILON =       1    # greedy police
ALPHA =         0.5     # learning rate
GAMMA =         1       # discount 

agent = rl_agent(
                list(range(3)), #STAY,LEFT,RIGHT
                GAMMA,
                ALPHA,
                EPSILON
               )


agent.init_q_table()

#resetRobot()

i = 0
epochs = 10000
grid_dim = (5,8)
robot_pos = 0


while(True):
#while(i < epochs):
  
    ####Get the State From Vision####
    #this takes about 20 - 30 ms or .02 to .03 s
    cell = v.getCell(cap,scale_factor,first_frame,grid_dim, draw_frame=True)
    if(len(cell) < 1):
        continue
    state = (cell[0],robot_pos)


    ####Get the Action to Take From The Table####
    action = agent.get_action(str(state))

    #if acton is valid, perform the action by sending it to the robot via serial
    if checkValidMove(robot_pos, action): 

        #get the new position the robot should be in based on the action
        robot_pos = updateRobotPosition(robot_pos, action)
        
        #if we need the robot to actually move
        if action != 0:
            #convert the action to the integer command agreed upon with arduino code
            command = positionToCommand(robot_pos)
            #if the command isnt the same position that were already in - dont want to send the same command twice in a row, it will only slow down the serial port
            if command != robot_pos:
                #send the action to take
                sendToRobot(command)

     ####Get the Reward After the Action has been taken####
    reward = get_reward_vision(robot_pos, cell[0])

     ####Get the Next State After the Action has been taken####
    cell_prime = v.getCell(cap,scale_factor,first_frame,grid_dim)
    robot_pos_prime = robot_pos
    if(len(cell_prime) < 1):
        continue
    state_prime = (cell_prime[0] , robot_pos_prime)


    print(str(cell) + str(state) + ", " + str(action) + ", " + str(reward) + ", " + str(state_prime))

     ####Update the Table####
    agent.update(str(state),action,reward,str(state_prime))

    #if (i % 10 == 0):
        #os.system('cls')
        #agent.print_q_table()
  
   # i = i + 1
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
