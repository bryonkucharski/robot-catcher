import os, sys, inspect
import random
import time
from PIL import ImageGrab
import numpy as np
import cv2

#this is just to import rl agent from a different folder
rl_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../rl")))
if rl_subfolder not in sys.path:
    sys.path.insert(0, rl_subfolder)

from qlearning_agent import rl_agent

vision_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../vision")))
if vision_subfolder not in sys.path:
    sys.path.insert(0, vision_subfolder)

import discretize_vision as v

robot_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../robot")))
if robot_subfolder not in sys.path:
    sys.path.insert(0, robot_subfolder)

from virtual_robot import virtual_robot


def get_reward_vision(robot_pos, ball_pos):
    if (robot_pos == ball_pos):
        return 1
    else:
        return -0.1 * (abs(robot_pos - ball_pos))
    


    
#Vision Variables
cap = cv2.VideoCapture(1)
scale_factor = 0.6
first_frame = True
grid_dim = (5, 5)

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

robot = virtual_robot(
                    WIDTH = 1680,
                    HEIGHT = 1050,
                    
                    dpi = 99,
                    ramp_length = 12.7953, #inches
                    number_of_states = 5
                )

agent.init_q_table()

i = 0
grid_dim = (5,8)        #
ITERS =         1000    #How many episodes to run in total
UPDATE_FREQ =   60      #How often to update environment, in hz
episodes = 0            #One episode is start to end of ramp

while episodes <= ITERS:
    
    ####Get the State####
    cell = v.getCell(cap,scale_factor,first_frame,grid_dim, draw_frame=True)
    robot_pos = robot.get_goalie_pos()

    if(len(cell) < 1):
        continue
    state = (cell[0],robot_pos)

    ####Get the Action####
    action = agent.get_action(str(state))
    
    robot.update_position(action)
    
    #get reward
    reward = get_reward_vision(robot_pos,cell[0])

    #get state prime
    cell_prime = v.getCell(cap,scale_factor,first_frame,grid_dim)
    robot_pos_prime = robot.get_pos()
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

    robot.drawRobot()
    if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()