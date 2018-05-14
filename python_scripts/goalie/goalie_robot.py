import os, sys, inspect
import random
import time
from PIL import ImageGrab
import numpy as np
import cv2
import serial # (pip install pySerial)

# Replace with specific port name & baud rate
serial_port = serial.Serial('COM4', 9600)


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

#Robot Constants
robot_pos = 0


def get_reward_vision(ball_pos):
    if (robot_pos == ball_pos):
        return 1
    else:
        return -0.1 * (abs(robot_pos - ball_pos))
    
def resetRobot():
    sendToRobot(17)

def sendToRobot(msg):
    serial_port.write(str(msg).encode())

def checkValidMove(action):
    if (robot_pos == 0):
        if action == 1:
            return False
    if (robot_pos == 4):
        if action == 2:
            return False
    return True

def updateRobotPosition(action):
    if action == 1:
        robot_pos -= 1
    elif action == 2:
        robot_pos += 1

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
resetRobot()

i = 0
epochs = 10000
grid_dim = (5,8)

while(True):
#while(i < epochs):
    
    #get state
    cell = v.getCell(cap,scale_factor,first_frame,grid_dim, draw_frame=True)
    robot_pos = robot.get_pos()
    if(len(cell) < 1):
        continue
    state = (cell[0],robot_pos)

    #get action
    action = agent.get_action(str(state))

    if(checkValidMove(action)):
        sendToRobot(action)
        updateRobotPosition(action)
    #get reward
    reward = get_reward_vision(cell[0])

    #get state prime
    cell_prime = v.getCell(cap,scale_factor,first_frame,grid_dim)
    robot_pos_prime = robot_pos
    if(len(cell_prime) < 1):
        continue
    state_prime = (cell_prime[0] , robot_pos_prime)


    print(str(state) + ", " + str(action) + ", " + str(reward) + ", " + str(state_prime))

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