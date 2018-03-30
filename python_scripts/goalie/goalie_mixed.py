import os, sys, inspect
import random
import time
from PIL import ImageGrab
import numpy as np


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



def get_reward_vision():
        #if robot position is the same as the ball position 
            #return 1
        else:
            #return math
    return 10

def get_state_vision(grid_dim, robot):
   
    # TODO: get screenshot from camera
    screenImage = v.screenshot()#(X, Y) starting position ; (W, H) ending position
    img = np.array(screenImage)#convert the image to a numpy array
    img_dim = img.shape[1], img.shape[0]
    cell_dim = v.get_cell_dimensions(img_dim, grid_dim)
    circle_center, radius = v.get_circle(img)
    cell = v.pixel_to_cell(circle_center, cell_dim)
    #print(cell)
    robot_x = robot.get_pos()
    

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
epochs = 10000
grid_dim = (5,8)

while(i < epochs):
    

    #state = get_state_vision(grid_dim, robot)

    #get action
    action = agent.get_action(str(state))
   
    robot.update_position(action)
    
    reward = get_reward_vision()

    state_prime = get_state_vision(grid_dim, rpbot)


    #print(str(state) + ", " + str(action) + ", " + str(reward) + ", " + str(state_prime))
    agent.update(str(state),action,reward,str(state_prime))

    if (i % 10 == 0):
        os.system('cls')
        agent.print_q_table()


    i = i + 1

    robot.drawRobot()
  