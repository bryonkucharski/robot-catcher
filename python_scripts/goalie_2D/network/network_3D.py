

'''

Bryon Kucharski
Wentorth Institute of Technology
Summer 2018

Applying a DQN to a 3D simulation ( Unity) of a 2D robot


A state consists of a vector of [ball_x, ball_y]

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

TYPE = "2D"

plot_file_name = 'poster_data_2000_plot_network_5x3_' + str(TYPE) + '_robot.txt'
averages_plot_file_name = 'poster_data_2000_plot_network_5x3_' + str(TYPE) + '_robot_averages.txt'

t = 0
EPOCHS = 2000
OBSERVE = 32#320
REPLAY_MEMORY = 50000
BATCH = 32

model_name = "poster_data_2000_goalie_network_5x3.h5"
save_model = False
load_model = False
update_model = True


if (load_model):
    esp = 0.01
else:
    esp = 1

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



agent = DQNAgent(#state_size =num_grid_y*num_grid_x,
                state_size =num_states, 
                action_size = num_actions,
                gamma = 0.95,
                #gamma = 0,
                epsilon = esp,
                epsilon_min = 0.01,
                epsilon_decay = 0.995,
                learning_rate = 0.001, 
                model_type = 'DeepModel'
                )


done = False
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

open(plot_file_name, 'w').close() #resets the text file
open(averages_plot_file_name, 'w').close() #resets the text file

unity.wait_for_phrase("start")

if load_model: 
    agent.load(model_name)
i = 0
for r in range(EPOCHS+1):
    
    state = unity.get_state_unity(type = TYPE)

    while not done:
        
        action = agent.take_action(np.array([state]))
        #action = agent.get_action(str(state))
        unity.send_action(action, TYPE)

        state_prime, reward, done = unity.step(type = TYPE)
        total_reward += reward

        if update_model:
            agent.remember(np.array([state]), action, reward, np.array([state_prime]), done)

        #print("State: " + str(state) + " action: " + str(action) + " Reward: " + str(reward) + " State Prime: " + str(state_prime))
        state = state_prime
        #agent.update(str(state),action,reward,str(state_prime))
        if done:
            done = False
            #check for a catch
            if reward == 1:
                catch_count += 1
                print("CATCH!!!")

            #exit this epoch    
            break

    i = i + 1
    
    if(agent.memory_length() > BATCH) and (update_model):
        history = agent.replay(BATCH)
        #print("epoch: " + str(r) + " history: " +  str(history.history['loss']) + " reward_count: " + str(reward_count))
        total_loss.append(history.history['loss'])   
    
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

        print(" Total catches this 100: " + str(catches) + " Average: " + str(average_catch) + " Total reward this 100: " + str(rewards) + " Average: " + str(average_reward))
        average_catches.append(average_catch)
        average_rewards.append(average_reward)
        average_epochs.append(r)
        last_catch = catch_count
        last_reward = total_reward
        ft = open(averages_plot_file_name, 'a') 
        ft.write(str(r) + "," + str(average_reward) + "," + str(average_catch) + "\n" ) 
        ft.close()
 


if save_model:
    agent.save(model_name)

plt.figure(1)
plt.plot(num_epochs,total_rewards)
plt.title("Network: Cumulative Reward in 3D Simulation: " + str(TYPE))
plt.ylabel("Cumulative Reward")
plt.xlabel("Number of Ball Rolls")
plt.show()

plt.figure(1)
plt.plot(num_epochs,total_catches)
plt.title("Network: Total Catches in 3D Simulation: " + str(TYPE))
plt.ylabel("Catches")
plt.xlabel("Number of Ball Rolls")
plt.show()

plt.figure(1)
plt.plot(average_epochs,average_rewards)
plt.title("Network: Average Reward in 3D Simulation: " + str(TYPE))
plt.ylabel("Average Reward")
plt.xlabel("Number of Ball Rolls")
plt.show()

plt.figure(1)
plt.plot(average_epochs,average_catches)
plt.title("Network: Average Catches in 3D Simulation: " + str(TYPE))
plt.ylabel("Average Catches")
plt.xlabel("Number of Ball Rolls")
plt.show()
