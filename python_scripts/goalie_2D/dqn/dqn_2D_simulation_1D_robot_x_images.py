'''
    Bryon Kucharski
    Wentorth Institute of Technology
    Summer 2018
    
    Applying a DQN to a 2D simulation of a 1D robot
    Similiar to http://edersantana.github.io/articles/keras_rl/

    The environment is a stddraw enviornment with a topdown view (see simulated_1D_robot_topdown.py)
    
    It is used to learn the X direction of the robot
    it uses binary images to calculate the state      

'''

import numpy as np
import os, sys, inspect
import time
from random import randint
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import json
import tensorflow as tf


config = tf.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.Session(config=config)
from keras import backend as K
K.set_session(sess)


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



t = 0
EPOCHS = 1000000
OBSERVE = 320
REPLAY_MEMORY = 50000
BATCH = 32
LEARNING_RATE = 1e-4
FRAME_PER_ACTION = 1
update_model = True
load_model = False
draw_scene = True
esp = 1
reward_count = 0
total_reward = 0
total_loss = []
total_rewards = []
num_epochs = []

if (load_model):
    esp = 0.01
else:
    esp = 1

robot = simulated_1D_robot(
                goalie_pos_start = 2, 
                GRID_NUM_WIDTH = 5, 
                GRID_SIZE = 75,
                draw_scene = draw_scene,
                gridworld = False
                )

agent = DQNAgent(state_size = 80*80, 
                action_size = 3,
                gamma = 0.99,
                epsilon = esp,
                epsilon_min = 0.01,
                epsilon_decay = 0.995,
                learning_rate = LEARNING_RATE, 
                model_type = 'DeepModel'
                )

if load_model:
    agent.load('image_model.h5')


for r in range(EPOCHS):
    if total_reward > 1000:
        break

    #plt.ion()
    #plt.show()
    #robot.reset()
    #state = robot.get_state_stacked(initalState=True)
    state = robot.get_state_binary(resize_shape = (80,80))


    done = False
    while not done:
        robot.drawNoGridScene() 

        if t % FRAME_PER_ACTION == 0: #this is so you can delay how often you want to take an action (in frames)

            action = agent.take_action(state)
            
            #state_prime, reward, done = robot.step(action, stateType = 'stacked', previous_state = state)
            state_prime, reward, done = robot.step(action, stateType = 'binary', reshape_shape = (80,80))
            

            if t > OBSERVE:
                total_reward += reward

            if update_model:
                agent.remember(state, action, reward, state_prime, done)
            
            if t > OBSERVE and update_model:
                
                history = agent.replay(BATCH)
                print("epoch: " + str(r) + " iteration: " + str(t) +  " loss: " +  str(history.history['loss']) + " total reward: " + str(total_reward))
                total_loss.append(history.history['loss'])
        #print("action: " + str(action) + " Reward: " + str(reward) )
            
        state = state_prime   
        t=t+1
        if r % 10 == 0:
            total_rewards.append(total_reward)
            num_epochs.append(r)
           
            


        if (t % 1000 == 0) and update_model:
           agent.save("image_model.h5")

plt.figure(1)       
plt.plot(num_epochs,total_rewards)
plt.title("Cumulative Reward in DQN 2D Simulation. Iterations: " + str(t))
plt.ylabel("Cumulative Reward")
plt.xlabel("Number of Updates")

plt.figure(2) 
plt.plot(np.arange(0,len(total_loss)),total_loss)
plt.title("Cumulative Loss in DQN 2D Simulation")
plt.ylabel("Loss")
plt.xlabel("Number of Updates")

plt.show()