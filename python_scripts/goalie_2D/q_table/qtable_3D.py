'''
Summer 2018

Uses 3D simulation in unity and a q table with a 2D robot

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
import pdb

flder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../../socket")))
if flder not in sys.path:
    sys.path.insert(0, flder)
flder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../../rl")))
if flder not in sys.path:
    sys.path.insert(0, flder)
flder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../utils")))
if flder not in sys.path:
    sys.path.insert(0, flder)
from tcp_server import tcp_socket

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.Session(config=config)
from keras import backend as K
K.set_session(sess)


style.use('fivethirtyeight')

from DQNAgent import DQNAgent
from qlearning_agent import rl_agent


from unityUtils import UnityInterface


t = 0
EPOCHS = 2000
OBSERVE = 32#320
REPLAY_MEMORY = 50000
BATCH = 32
LEARNING_RATE = 1e-4

TYPE = "2D" # "x" for 1D robot in x direction. "y" for 1D robot in y direction. "2D" for 2D robot

plot_file_name =          'poster_data_2000_q_table_5x3_' + str(TYPE) + '_robot.txt'
averages_plot_file_name = 'poster_data_2000_q_table_5X3_' + str(TYPE) + '_robot_averages.txt'
save_model = True
load_model = False
update_model = True


server = tcp_socket(
                    host = '',
                    port = 50000, 
                    backlog = 5, #amount of requests to queue at one time
                    size = 1024 
                    )

unity = UnityInterface(server)



if TYPE == "x" or TYPE == "y":
    num_actions = 3
    num_states = 2
else:
    num_actions = 5
    num_states = 4

#RL constants
EPSILON =       1    # greedy police
ALPHA =         0.5     # learning rate
GAMMA =         1       # discount 

agent = rl_agent(
                list(range(num_actions)), #STAY,LEFT,RIGHT
                GAMMA,
                ALPHA,
                EPSILON
                )

agent.init_q_table()


catch_count = 0
total_reward = 0
last_catch = 0
last_reward = 0
total_rewards = []
num_epochs = []
average_epochs = []
total_loss = []
total_catches = []
average_catches = []
average_rewards = []

unity.wait_for_phrase("start")


open(plot_file_name, 'w').close() #resets the text file
open(averages_plot_file_name, 'w').close() #resets the text file

for r in range(EPOCHS + 1):
    ### Main Loop ###
    done = False
    state = unity.get_state_unity(type = TYPE)
    while not done:
        
        action = agent.get_action(str(state))
        unity.send_action(action, TYPE)
        
        state_prime, reward, done = unity.step(type = TYPE)
        total_reward += reward  

        #print(str(r) + ": State: " + str(state) + " action: " + str(action) + " Reward: " + str(reward) + " State Prime: " + str(state_prime) + " " + str(total_reward) + " " + str(done))
        
        if update_model:
            agent.update(str(state),action,reward,str(state_prime))
        
        state = state_prime

        #########

        #check for a catch
        if done and reward == 1:
            catch_count += 1
            print("CATCH!!!")

    if r % 10 == 0:
        total_rewards.append(total_reward)
        total_catches.append(catch_count)
        num_epochs.append(r)
        print("Epoch: " + str(r) + " Total Reward: " + str(total_reward) + " Total Catches: " + str(catch_count))
        fh = open(plot_file_name, 'a') 
        fh.write(str(r) + "," + str(total_reward) + "," + str(catch_count) + "\n" ) 
        fh.close()

    if r % 100 == 0:
        
        catches = catch_count - last_catch
        rewards = total_reward - last_reward
        average_catch = catches / 100.0
        average_reward = rewards / 100.0

        print(" Total catches this 50: " + str(catches) + " Average: " + str(average_catch) + " Total reward this 50: " + str(rewards) + " Average: " + str(average_reward))
        average_catches.append(average_catch)
        average_rewards.append(average_reward)
        average_epochs.append(r)
        last_catch = catch_count
        last_reward = total_reward
        ft = open(averages_plot_file_name, 'a') 
        ft.write(str(r) + "," + str(average_reward) + "," + str(average_catch) + "\n" ) 
        ft.close()
 


plt.figure(1)
plt.plot(num_epochs,total_rewards)
plt.title("Cumulative Reward in 3D Simulation: " + str(TYPE))
plt.ylabel("Cumulative Reward")
plt.xlabel("Number of Ball Rolls")
plt.show()

plt.figure(1)
plt.plot(num_epochs,total_catches)
plt.title("Total Catches in 3D Simulation: " + str(TYPE))
plt.ylabel("Catches")
plt.xlabel("Number of Ball Rolls")
plt.show()

plt.figure(1)
plt.plot(average_epochs,average_rewards)
plt.title("Average Reward in 3D Simulation: " + str(TYPE))
plt.ylabel("Average Reward")
plt.xlabel("Number of Ball Rolls")
plt.show()

plt.figure(1)
plt.plot(average_epochs,average_catches)
plt.title("Average Catches in 3D Simulation: " + str(TYPE))
plt.ylabel("Average Catches")
plt.xlabel("Number of Ball Rolls")
plt.show()

