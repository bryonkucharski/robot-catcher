'''
    Bryon Kucharski
    Wentorth Institute of Technology
    Spring 2018
    
    Modified gridworld - 2d goalie
'''
import numpy as np
import os, sys, inspect
import time
from matplotlib import pyplot
from random import randint

os.environ['SDL_VIDEO_WINDOW_POS'] = str(0) + "," + str(0)


#this is just to import stddraw from a different folder
princeton_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../princeton_lib")))
if princeton_subfolder not in sys.path:
    sys.path.insert(0, princeton_subfolder)

import stddraw

#this is just to import rl agent from a different folder
rl_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../rl")))
if rl_subfolder not in sys.path:
    sys.path.insert(0, rl_subfolder)

from qlearning_agent import rl_agent

#this is just to import stddraw from a different folder
vision_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../vision")))
if vision_subfolder not in sys.path:
    sys.path.insert(0, vision_subfolder)

import vision

def drawScene(goalie_pos, ball_x, ball_y):
    
    stddraw.clear()
    stddraw.setPenColor(stddraw.BLACK)
    
    #gridlines
    for i in range(1,GRID_NUM_HEIGHT):
        stddraw.filledRectangle(0,GRID_SIZE*i,WIDTH,0)

    for i in range(1,GRID_NUM_WIDTH):
        stddraw.filledRectangle(GRID_SIZE * i,0,0,HEIGHT)

    #goalie
    stddraw.setPenColor(stddraw.BLUE)
    stddraw.filledRectangle(goalie_pos*GRID_SIZE,0,GRID_SIZE,GRID_SIZE) #x,y,size_x,size_y
    
    #Ball
    stddraw.setPenColor(stddraw.GREEN)
    stddraw.filledCircle(((ball_x *GRID_SIZE) + (GRID_SIZE/2)) ,(HEIGHT - ((ball_y *GRID_SIZE) + (GRID_SIZE/2))), GRID_SIZE/2)
        
def check_valid_move(goalie_pos, action):
    if goalie_pos == 0 and action == 1:
        return False
    elif goalie_pos == GRID_NUM_WIDTH-1 and action == 2:
        return False
    return True

#Enviornment Constants
GRID_NUM_HEIGHT = 8
GRID_NUM_WIDTH = 5
GRID_SIZE = 75 # in pixels
WIDTH = GRID_SIZE*GRID_NUM_WIDTH
HEIGHT = GRID_SIZE*GRID_NUM_HEIGHT

#RL constants
EPSILON =       1    # greedy police
ALPHA =         0.5     # learning rate
GAMMA =         1       # discount 
ITERS =         1000     #iterations
UPDATE_FREQ =   60    #How often to update environment

stddraw.setXscale(0, WIDTH)
stddraw.setYscale(0, HEIGHT)
stddraw.setCanvasSize(WIDTH,HEIGHT)

agent = rl_agent(
                list(range(3)), #STAY,LEFT,RIGHT
                GAMMA,
                ALPHA,
                EPSILON
                )

agent.init_q_table()

goalie_pos = 3 #randint(0,GRID_NUM_WIDTH-1)
ball_x = randint(0, GRID_NUM_WIDTH-1)
ball_y = 0


episodes = 0
steps = 0
reset  = False 
all_steps = []
all_iters = []
start = time.time()
total_time = time.time()


while episodes <= ITERS:

    end = time.time()
    elapsed = end - start

    drawScene(goalie_pos,ball_x, ball_y)
    stddraw.show(0)
    
    if elapsed > 1/UPDATE_FREQ: #how fast the enviornment should move

        img = vision.get_screenshot(0,0, WIDTH, HEIGHT)
        x,y = vision.pixelToCell(img, GRID_SIZE,GRID_SIZE, debug = True)
        
        start = time.time()

        #get current state
        state = [goalie_pos, x, y]
        #state = [goalie_pos, ball_x, ball_y]
        
        #get action
        action = agent.get_action(str(state))

        #check if enviornment will allow the new state
        is_valid = check_valid_move(goalie_pos, action)

        if is_valid:
            if action == 0: #STAY
                goalie_pos = goalie_pos
            elif action == 1: #LEFT
                goalie_pos = goalie_pos - 1
            elif action == 2: #RIGHT
                goalie_pos = goalie_pos + 1
            
        #reward decision  -.04 every action, 1 for making it into the goal
        #reward = -.04
        if (ball_x == goalie_pos):
            reward = 1
        else:
           reward = -0.1 * (abs(goalie_pos - ball_x))
        
        #get next state
        img = vision.get_screenshot(0,0, WIDTH, HEIGHT)
        x_,y_ = vision.pixelToCell(img, GRID_SIZE,GRID_SIZE, debug = False)
        state_prime = [goalie_pos, x_, y_]
        

        #update based on experience {s,a,r,s'}
        
        agent.update(str(state),action,reward,str(state_prime))

        ball_y = ball_y + 1
        if(ball_y > GRID_NUM_HEIGHT-1):
            reset = True
        steps = steps + 1

        #os.system('cls')
        #print(agent.print_q_table())

        if reset:
            print('itr: ' + str(episodes) +' reward: ' + str(reward))
            ball_x = randint(0, GRID_NUM_WIDTH-1)
            ball_y = 0
            episodes = episodes + 1
            reset = False
            all_steps.append(steps)
            all_iters.append(episodes)
            steps = 0
        
