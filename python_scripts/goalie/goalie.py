'''
    Bryon Kucharski
    Wentorth Institute of Technology
    Spring 2018
    
    Simulated One Dimensional Robot using stddraw grahpics library and a tabular Reinforcement Learning agent 
'''


import numpy as np
import os, sys, inspect
import time
from matplotlib import pyplot
from random import randint


#uncomment to set stddraw window to top left of screen
#os.environ['SDL_VIDEO_WINDOW_POS'] = str(0) + "," + str(0)

#this is just to import rl agent from a different folder
rl_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../rl")))
if rl_subfolder not in sys.path:
    sys.path.insert(0, rl_subfolder)

from qlearning_agent import rl_agent

#this is just to import vision from a different folder
vision_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../vision")))
if vision_subfolder not in sys.path:
    sys.path.insert(0, vision_subfolder)

import discretize_vision

robot_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../robot")))
if robot_subfolder not in sys.path:
    sys.path.insert(0, robot_subfolder)

from simulated_1D_robot import simulated_1D_robot



#RL constants
EPSILON =       1    # greedy police
ALPHA =         0.5     # learning rate
GAMMA =         1       # discount 



#declare agent with 3 actions, 0 for stay, 1 for left, 2 for right
agent = rl_agent(
                list(range(3)), #STAY,LEFT,RIGHT
                GAMMA,
                ALPHA,
                EPSILON
                )

#created the robot using tthe stddraw graphics library 
robot = simulated_1D_robot(
                goalie_pos_start = 3, 
                GRID_NUM_HEIGHT = 8, 
                GRID_NUM_WIDTH = 5, 
                GRID_SIZE = 75 #pixels
                )

#create the q table stored in the agent
agent.init_q_table()
#agent.init_stddraw(800)


#Main Loop constants 
ITERS =         1000    #How many episodes to run in total
UPDATE_FREQ =   60      #How often to update environment, in hz
episodes = 0            #One episode is start to end of ramp
steps = 0               #One step is one iteration of state-action-reward-state_prime-update
reset  = False          
all_steps = []          #used to plot
all_iters = []          #used to plot

start = time.time()     
total_time = time.time()

is_done = False

#Main Loop
'''
    Follows the Basic RL Flow
    While !terminated:
        Get State
        Get Action
        Take Action
        Get Reward
        Get State Prime
        Update Agent
        State = State Prime
'''
while episodes <= ITERS:

    end = time.time()
    elapsed = end - start

    # draw the robot every frame
    robot.drawScene()
    
    #this is what controls how quickly each iteration runs, if it updates too quick the robot will move 
    # too quick to see the updates. If you are not drawing the scene, you dont need to use this
    if elapsed > 1/UPDATE_FREQ: #how fast the enviornment should move

        #uncomment this to use vision to get the state of the enviornment
        #img = vision.get_screenshot(0,0, WIDTH, HEIGHT)
        #x,y = vision.pixelToCell(img, GRID_SIZE,GRID_SIZE, debug = True)
      
        start = time.time()

        ####Get the State####
        state = robot.get_state_array()

        #####Get the Action####
        action = agent.get_action(str(state))
 
        #####Perform the Action in the Environment####
        #####Gets the State Prime and Reward####
        state_prime, reward, is_done = robot.step(action, stateType='array')
    
        #uncomment this to use vision to get the state of the enviornment
        #get next state
        #img = vision.get_screenshot(0,0, WIDTH, HEIGHT)
        #x_,y_ = vision.pixelToCell(img, GRID_SIZE,GRID_SIZE, debug = False)
        
        ####Update Based On Experience {s,a,r,s'}####
        agent.update(str(state),action,reward,str(state_prime))


        #agent.visualize_q_table(800)
        steps = steps + 1

        #uncomment this to print q table to console
        #os.system('cls')
        #print(agent.print_q_table())
        print('itr: ' + str(episodes) +' reward: ' + str(reward) + " x: " + str(state[0]) + "  x_: " + str(state_prime[0]) + " goalie_pos: ")

        #If the robot is at the bottom of the ramp, update stpes/iterations/episodes
        if is_done:
            is_done = False
            episodes = episodes + 1
            all_steps.append(steps)
            all_iters.append(episodes)
            steps = 0
        
