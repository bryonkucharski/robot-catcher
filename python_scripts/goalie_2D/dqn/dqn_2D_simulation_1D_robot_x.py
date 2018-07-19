'''
    Bryon Kucharski
    Wentorth Institute of Technology
    Summer 2018
    
    Applying a DQN to a 2D simulation of a 1D robot
    Similiar to http://edersantana.github.io/articles/keras_rl/

    The environment is a stddraw enviornment with a topdown view (see simulated_1D_robot_topdown.py)
    
    It is used to learn the X direction of the robot
    it uses a matrix of 0s and 1s (taken from stddraw enviornment) to calculate the state      

'''

import numpy as np
import os, sys, inspect
import time
from random import randint
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import tensorflow as tf


style.use('fivethirtyeight')


    

#this is just to import rl agent from a different folder
rl_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../rl")))
if rl_subfolder not in sys.path:
    sys.path.insert(0, rl_subfolder)

from DQNAgent import DQNAgent

robot_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../robot")))
if robot_subfolder not in sys.path:
    sys.path.insert(0, robot_subfolder)

from simulated_1D_robot import simulated_1D_robot


config = tf.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.Session(config=config)
from keras import backend as K
K.set_session(sess)


num_grid_x = 5
num_grid_y = 100

save_model = True
load_model = False
update_model = True
model_name = 'RewardFunction2_2000.h5'
draw_scene = True

if (load_model):
    esp = 0.01
else:
    esp = 1

robot = simulated_1D_robot(
                goalie_pos_start = 3, 
                GRID_NUM_HEIGHT = num_grid_y, 
                GRID_NUM_WIDTH = num_grid_x, 
                GRID_SIZE = 10,
                draw_scene = draw_scene,
                gridworld = True
                )

agent = DQNAgent(#state_size =num_grid_y*num_grid_x,
                state_size =2, 
                action_size = 3,
                gamma = 0.95,
                epsilon = esp,
                epsilon_min = 0.01,
                epsilon_decay = 0.995,
                learning_rate = 0.001, 
                model_type = 'DeepModel'
                )

EPOCHS = 5000
if not draw_scene:
    UPDATE_FREQ = 1000000
else:
    UPDATE_FREQ = 1000000

batch_size = 32

start = time.time()
done = False
reward_count = 0
total_reward = 0
total_rewards = []
num_epochs = []
total_loss = []

axes = plt.gca()
#axes.set_xlim(0, 100)
#axes.set_ylim(-50, +50)
line, = axes.plot(num_epochs, total_rewards, 'r-')

if load_model: 
    agent.load(model_name)



for r in range(EPOCHS):
    #state = robot.get_state_matrix()
    state = robot.get_state_array()
    state = np.array([state])
    #print(state)
    robot.reset()
    
    i = 0

    while not done:
        end = time.time()
        elapsed = end - start
       
        if elapsed > 1/UPDATE_FREQ:
            
            if draw_scene:
                robot.drawGridScene()

            start = time.time()
            action = agent.take_action(state)
            state_prime, reward, done = robot.step(action, stateType = 'array')
            state_prime = np.array([state_prime])

            total_reward += reward
            
            if update_model:
                agent.remember(state, action, reward, state_prime, done)

            #print("\nState: \n" + str(state.reshape(num_grid_y,num_grid_x)) + " \naction: " + str(action) + " Reward: " + str(reward) + "\nState Prime: \n" + str(state_prime.reshape(num_grid_y,num_grid_x)))
            state = state_prime
            if done:
        
                done = False
                
                #check for a catch
                if reward == 1:
                    reward_count += 1
                    print("CATCH!!!")

                #exit this epoch    
                break
            i = i + 1
    
    if(agent.memory_length() > batch_size) and (update_model):
        #start = time.time()
        history = agent.replay(batch_size)
        print("epoch: " + str(r) + " history: " +  str(history.history['loss']) + " reward_count: " + str(reward_count))
        #end = time.time()
        #print(end - start)
        total_loss.append(history.history['loss'])
        

    if r % 10 == 0:
        total_rewards.append(total_reward)
        num_epochs.append(r)
 


if save_model:
    agent.save(model_name)


plt.figure(1)
plt.plot(num_epochs,total_rewards)
plt.title("Cumulative Reward in Deep Learning 2D Simulation: Vector State")
plt.ylabel("Cumulative Reward")
plt.xlabel("Number of Updates")
plt.show()


