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

def readFromRobot():
    msg = -1
    while(msg != 1):
        msg = serial_port.read()
        if msg:
            print(msg)

def actionToCommand(action):
    if int(action) == 1:
        return 32
    elif int(action) == 2:
        return 30

def positionToCommand(new_robot_pos):
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
   # print(str(action) + ", " + str(robot_pos) )
    if (robot_pos == 0):
        if int(action) == 1:
            return False
    if (robot_pos == 4):
        if int(action) == 2:
            return False
    return True

def updateRobotPosition(robot_pos, action):
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
    #print(robot_pos)
    #get state
    #start = time.time()
    #this takes about 20 - 30 ms or .02 to .03 s
    cell = v.getCell(cap,scale_factor,first_frame,grid_dim, draw_frame=True)
    #end = time.time()
    #elapsed = end - start
    #print(elapsed*1000.0)
    if(len(cell) < 1):
        continue
    
    state = (cell[0],robot_pos)
    #print(state)

    #get action
    action = agent.get_action(str(state))

    #if(checkValidMove(robot_pos, action)):
        #robot_ready = readFromRobot()
    #if( cell[1] == 1 ):

    if checkValidMove(robot_pos, action): 
        robot_pos = updateRobotPosition(robot_pos, action)
        print(robot_pos)
        if action != 0:
            command = positionToCommand(robot_pos)
            print(command)
            if command != robot_pos:
                sendToRobot(command)

    #get reward
    reward = get_reward_vision(robot_pos, cell[0])

    #get state prime
    cell_prime = v.getCell(cap,scale_factor,first_frame,grid_dim)
    robot_pos_prime = robot_pos
    if(len(cell_prime) < 1):
        continue
    state_prime = (cell_prime[0] , robot_pos_prime)


    print(str(cell) + str(state) + ", " + str(action) + ", " + str(reward) + ", " + str(state_prime))

    #update q table
    agent.update(str(state),action,reward,str(state_prime))

    #if (i % 10 == 0):
        #os.system('cls')
        #agent.print_q_table()

  
   # i = i + 1
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
