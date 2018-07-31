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
import sys


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


OBSERVE = 32#320
REPLAY_MEMORY = 50000
BATCH = 32


if(len(sys.argv) != 4):
    sys.exit("ERROR: Must input 3 arguments. \n network_simulation.py num_x num_y simulations")


num_x = int(sys.argv[1])
num_y = int(sys.argv[2])
SIMULATIONS =  int(sys.argv[3])

if num_x > BATCH:
    iter_per_roll = 2*num_x
else:
    iter_per_roll = 2*BATCH

plot_file_name = str(num_x) + "x" + str(num_y) + "x" + str(SIMULATIONS) + '_network_simulation.txt'
averages_plot_file_name = str(num_x) + "x" + str(num_y) + "x" + str(SIMULATIONS) + '_network_simulation_averages.txt'


agent = DQNAgent(#state_size =num_grid_y*num_grid_x,
                state_size = 4, #robot_x,ball_x,robot_y,thrust
                action_size = 5, #up,down,left,right
                gamma = 0.95,
                #gamma = 0,
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

    return state_prime,reward

def distance_reward(x1, x2, y1, y2):

    distance = -0.1 * (np.sqrt((x2-x1)**2 + (y2-y1)**2) ** 2 )
    if distance == 0:
        return 2
    elif (x1 == x2) or (y1 == y2):
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

catch_count = 0
total_catches = []
total_reward = 0
total_rewards = []
num_epochs = []
last_reward = 0
last_catch = 0
average_rewards = []
average_epochs = []
average_catches = []


open(plot_file_name, 'w').close() #resets the text file
open(averages_plot_file_name, 'w').close() #resets the text file

print("Running Simulation for size " + str(num_x) + " x " + str(num_y) + " for " + str(SIMULATIONS) + " simulations")

for r in range(SIMULATIONS+1):
   

    i = 0
    robot_y = random.randint(1,num_y)
    robot_x = random.randint(1,num_x)
    ball_x = random.randint(1,num_x)
    thrust = random.randint(1,num_y)
    state = [robot_x,ball_x,robot_y,thrust]

    while i < iter_per_roll: 

        action = agent.take_action(np.array([state]))
        state_prime, reward = step(action, state )

        if i == iter_per_roll - 1:
            done = False
        else:
            done = False

        if done and reward == 1:
            catch_count += 1
            print("CATCH")
            
        total_reward += reward
        print(state,state_prime,action,reward)
        agent.remember(np.array([state]), action, reward, np.array([state_prime]), done)
        state = state_prime
        i += 1
    
    if r % 10 == 0:
        total_catches.append(catch_count)
        total_rewards.append(total_reward)
        num_epochs.append(r)

        fh = open(plot_file_name, 'a') 
        fh.write(str(r) + "," + str(total_reward) + "," + str(catch_count) + "\n" ) 
        fh.close()

    if r % 100 == 0:
        
        rewards = total_reward - last_reward
        average_reward = rewards / 100.0

        catches = catch_count - last_catch
        average_catch = catches / 100.0 

        print("Total reward: " + str(rewards) + " Average Reward: " + str(average_reward) + "Total Catches: " + str(catch_count) + " Average Catches: "+ str(average_catch) )

        average_catches.append(average_catch)
        average_rewards.append(average_reward)
        average_epochs.append(r)

        last_reward = total_reward
        last_catch = catch_count

        ft = open(averages_plot_file_name, 'a') 
        ft.write(str(r) + "," + str(average_reward) + "," + str(average_catch) + "\n" ) 
        ft.close()
       
    
    history = agent.replay(BATCH)
    print("epoch: " + str(r) + " history: " +  str(history.history['loss']) + " reward_count: " + str(total_reward))

plt.figure(1)
plt.plot(num_epochs,total_rewards)
plt.title("Network: Cumulative Reward in 3D Simulation: " )
plt.ylabel("Cumulative Reward")
plt.xlabel("Number of Ball Rolls")
plt.show()

plt.figure(1)
plt.plot(average_epochs,average_rewards)
plt.title("Network: Average Reward in 3D Simulation: ")
plt.ylabel("Average Reward")
plt.xlabel("Number of Ball Rolls")
plt.show()

plt.figure(1)
plt.plot(num_epochs,total_catches)
plt.title("Network: Total Catches in 3D Simulation: ")
plt.ylabel("Catches")
plt.xlabel("Number of Ball Rolls")
plt.show()

plt.figure(1)
plt.plot(average_epochs,average_catches)
plt.title("Network: Average Catches in 3D Simulation: ")
plt.ylabel("Average Catches")
plt.xlabel("Number of Ball Rolls")
plt.show()



   

