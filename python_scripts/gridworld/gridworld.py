'''

    Bryon Kucharski
    Wentorth Institute of Technology
    Spring 2018
    
    My implementation of a gridworld enviornment
'''
import numpy as np
import os, sys, inspect
import time
from matplotlib import pyplot

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


GRID_NUM = 4
GRID_SIZE = 100 # in pixels
WIDTH = GRID_SIZE*GRID_NUM
HEIGHT = WIDTH
UPDATE_FREQ = 120#HZ

#RL constants
EPSILON = 0.9   # greedy police
ALPHA = 0.5     # learning rate
GAMMA = 1       # discount factor

def drawScene(black_hole_x, black_hole_y, ball_x, ball_y, goal_x, goal_y, neg_x, neg_y):
    '''
    handles the drawing of the ball, black box, goal box, and negative box
    '''
    stddraw.clear()
    stddraw.setPenColor(stddraw.BLACK)

    #gridlines
    for i in range(1,GRID_NUM):
        stddraw.filledRectangle(GRID_SIZE * i,0,0,HEIGHT)
        stddraw.filledRectangle(0,GRID_SIZE*i,WIDTH,0)
    
    #black rectangle
    stddraw.filledRectangle(black_hole_x * GRID_SIZE, black_hole_y * GRID_SIZE, GRID_SIZE,GRID_SIZE)
    
    #Ball
    stddraw.setPenColor(stddraw.GREEN)
    stddraw.filledCircle(((ball_x *GRID_SIZE) + (GRID_SIZE/2)) ,((ball_y *GRID_SIZE) + (GRID_SIZE/2)), GRID_SIZE/2)

    #Goal
    stddraw.setPenColor(stddraw.GREEN)
    stddraw.rectangle(goal_x * GRID_SIZE,goal_y * GRID_SIZE,GRID_SIZE, GRID_SIZE)

    #Negative box
    stddraw.setPenColor(stddraw.RED)
    stddraw.rectangle(neg_x * GRID_SIZE,neg_y * GRID_SIZE,GRID_SIZE, GRID_SIZE)

def check_valid_move(ball_x,ball_y, action):
    '''
    checks if the action about to be taken will result in the ball being off the screen or inside the black hole
    '''
    if action == 0: #wants to move up
        #check if next move will be inside black hole
        if (ball_y + 1 == black_hole_loc_y) and (ball_x == black_hole_loc_x):
            return False
        else:
            return (ball_y < (GRID_NUM-1))

    elif action == 1: # wants to move 
        #check if next move will be inside black hole
        if (ball_y - 1 == black_hole_loc_y) and (ball_x == black_hole_loc_x):
            return False
        else:
            return (ball_y > 0)
        
    elif action == 2: #wants to move right
        #check if next move will be inside black hole
        if (ball_x + 1 == black_hole_loc_x) and (ball_y == black_hole_loc_y):
            return False
        else: 
            return ball_x < (GRID_NUM - 1)

    elif action == 3:
        #check if next move will be inside black hole
        if (ball_x - 1 == black_hole_loc_x) and (ball_y == black_hole_loc_y):
            return False
        else:
            return ball_x > 0
   


#stddraw.setXscale(0, WIDTH)
#stddraw.setYscale(0, HEIGHT)
#stddraw.setCanvasSize(WIDTH,HEIGHT)

#initalize the black box, ball, goal location, and negative location
black_hole_loc_x = np.random.randint(1,GRID_NUM - 1)
black_hole_loc_y = np.random.randint(1,GRID_NUM - 1)
ball_x = 0
ball_y = 0

#goal will always be upper right
goal_x = GRID_NUM - 1
goal_y = GRID_NUM - 1

#this is just so the red box is never in the same location as the black box
while True:
    neg_x = np.random.randint(1,GRID_NUM - 1)
    neg_y = np.random.randint(1,GRID_NUM - 1)
    if ((neg_x is not black_hole_loc_y) and (neg_y is not black_hole_loc_y)):
        break



agent = rl_agent(
                list(range(4)), #UP,DOWN,LEFT,RIGHT
                GAMMA, #gamma
                ALPHA,
                EPSILON
                )

agent.init_q_table()

#drawScene(black_hole_loc_x, black_hole_loc_y,ball_x,ball_y,goal_x,goal_y, neg_x,neg_y)

start = time.time()
total_time = time.time()
episodes = 0
steps = 0
reset  = False
num_iters = 1000
all_steps = []
iters = []

while episodes <= num_iters:
    
    end = time.time()
    elapsed = end - start

    if elapsed > 1/UPDATE_FREQ: #how fast the ball should move
        start = time.time()

        #get current state
        state = [ball_x, ball_y]

        #get action
        action = agent.get_action(str(state))

        #check if enviornment will allow the new state
        is_valid = check_valid_move(ball_x, ball_y, action)

        if is_valid:
            if action == 0: #UP
                ball_y = ball_y + 1
            elif action == 1: #DOWN
                ball_y = ball_y - 1
            elif action == 2: #RIGHT
                ball_x = ball_x + 1
            elif action == 3: #LEFT
                ball_x = ball_x - 1

        steps = steps + 1
 
        #reward decision  -.04 every action, 1 for making it to the goal, -1 for entering red box
        reward = -.04
        if((ball_x == goal_x) and (ball_y == goal_y)):
            reward = 1
            reset = True
        elif((ball_x == neg_x) and (ball_y == neg_y)):
            reward = -1
        
        #get next state
        state_prime = [ball_x, ball_y]

        #update based on experience {s,a,r,s'}
        agent.update(str(state),action,reward,str(state_prime))


        #if ball is in goal reset back to 0,0
        if reset:
            print('itr: ' + str(episodes) + ' steps: ' + str(steps) + ' state: ' + str(state) +' reward: ' + str(reward))
            ball_x = 0
            ball_y = 0
            episodes = episodes + 1
            reset = False
            all_steps.append(steps)
            iters.append(episodes)
            steps = 0

        #agent.print_q_table()


    #drawScene(black_hole_loc_x, black_hole_loc_y,ball_x,ball_y,goal_x,goal_y, neg_x,neg_y)
    #stddraw.show(1)

pyplot.plot(iters,all_steps )
total_end = time.time()
total_elapsed = total_end - total_time
pyplot.title('Tabular - ' + 'time: ' + str(round(total_elapsed, 2)) + 's GRID_NUM: ' + str(GRID_NUM) + ' \nEPOCHS: ' + str(num_iters) + ' Avgs Step/Epoch: ' + str(round(np.sum(all_steps) / num_iters ,2)))
pyplot.savefig('gridworld_' + str(GRID_NUM) + '_' +str(num_iters) )
#pyplot.show()

