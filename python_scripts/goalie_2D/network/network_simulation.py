import numpy as np
import os, sys, inspect
import time
from random import randint
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import json
import random
import tensorflow as tf


flder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../../rl")))
if flder not in sys.path:
    sys.path.insert(0, flder)

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.Session(config=config)
from keras import backend as K
K.set_session(sess)


style.use('fivethirtyeight')

from DQNAgent import DQNAgent

SIMULATIONS = 10000
OBSERVE = 32#320
REPLAY_MEMORY = 50000
BATCH = 32

plot_file_name = '2000_network_simulation_5x3.txt'
averages_plot_file_name = '2000_network_simulation_averages.txt'

num_x = 5
num_y = 3
num_states = num_x*num_y
num_actions = 5

agent = DQNAgent(#state_size =num_grid_y*num_grid_x,
                state_size = 4, #robot_x,ball_x,robot_y,thrust
                action_size = 5, #up,down,left,right
                #gamma = 0.95,
                gamma = 0,
                epsilon = 1,
                epsilon_min = 0.01,
                epsilon_decay = 0.995,
                learning_rate = 0.001, 
                model_type = 'DeepModel'
                )


random.seed(10)

def step(action, state):
    
    x_ , y_ = update_current_position(action, state[0], state[2])
    reward = distance_reward(x_,state[1],y_,state[3])
    state_prime = [x_,state[1],y_,state[3]]

    return state_prime,reward,True

def distance_reward(x1, x2, y1, y2):

    distance = -0.1 * (np.sqrt((x2-x1)**2 + (y2-y1)**2) ** 2 )
    if distance == 0:
        return 1
    else:
        return distance


def manhanttan_reward():
    return None

def update_current_position(action,x,y):
    new_x = x
    new_y = y

    if action == 1: #Left
        if x != 1:
            new_x = x - 1
            new_y = y
    elif action == 2: #Right
        if x != num_x:
            new_x = x + 1
            new_y = y
    elif action == 3: #Up
        if y != num_y:
            new_x = x 
            new_y = y + 1
    elif action == 4: #Down
        if y != 1:
            new_x = x
            new_y = y - 1
    
    return new_x, new_y

total_reward = 0

for r in range(SIMULATIONS+1):
   

    i = 0
    while i < 32:
        
        ball_x = random.randint(1,num_x)
        thrust = random.randint(1,num_y)
        robot_x = random.randint(1,num_x)
        robot_y = random.randint(1,num_y)

        state = [robot_x,ball_x,robot_y,thrust]
        action = agent.take_action(np.array([state]))
        state_prime, reward, done = step(action, state )
        total_reward += reward
        print(state,state_prime,action,reward)
        agent.remember(np.array([state]), action, reward, np.array([state_prime]), done)
        i += 1
        
    
    history = agent.replay(BATCH)
    print("epoch: " + str(r) + " history: " +  str(history.history['loss']) + " reward_count: " + str(total_reward))
    #total_loss.append(history.history['loss'])   


   

