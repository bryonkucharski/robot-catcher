

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

from unityUtils import UnityInterface

def step(action, unity):
        
    unity.send_action(action)
    state_prime =  unity.get_state_unity()
    reward, done  = unity.getReward()
    
    #print(state_prime, reward, done)
    return state_prime, reward, done


t = 0
EPOCHS = 2000
OBSERVE = 32#320
REPLAY_MEMORY = 50000
BATCH = 32
LEARNING_RATE = 1e-4

model_name = "goalie_2d_network.py"
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


done = False
reward_count = 0
total_reward = 0
total_rewards = []
num_epochs = []
total_loss = []

if load_model: 
    agent.load(model_name)

for r in range(EPOCHS):
    state = unity.get_state_unity()

    i = 0

    while not done:

        action = agent.take_action(np.array([state]))
        unity.send_action(action)
        time.sleep(.05)
        state_prime, reward, done = unity.step()
        total_reward += reward

        if update_model:
            agent.remember(np.array([state]), action, reward, np.array([state_prime]), done)

        #print("State: " + str(state) + " action: " + str(action) + " Reward: " + str(reward) + " State Prime: " + str(state_prime))
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
    
    if(agent.memory_length() > BATCH) and (update_model):
        #start = time.time()
        history = agent.replay(BATCH)
        print("epoch: " + str(r) + " history: " +  str(history.history['loss']) + " reward_count: " + str(reward_count))
        total_loss.append(history.history['loss'])   

    if r % 10 == 0:
        total_rewards.append(total_reward)
        num_epochs.append(r)
 


if save_model:
    agent.save(model_name)


plt.figure(1)
plt.plot(num_epochs,total_rewards)
plt.title("Cumulative Reward in Deep Learning 3D Simulation: Vector State")
plt.ylabel("Cumulative Reward")
plt.xlabel("Number of Updates")
plt.show()