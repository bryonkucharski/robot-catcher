'''
    Bryon Kucharski
    Wentorth Institute of Technology
    Summer 2018
    
    Applying a DQN to a 3D simulation ( Unity) of a 2D robot
    

    A state consists of a binary image of the 

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
from PIL import Image
import mss #pip install --upgrade mss
import mss.tools
import cv2

socket_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../socket")))
if socket_subfolder not in sys.path:
    sys.path.insert(0, socket_subfolder)

from tcp_server import tcp_socket

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

def wait_for_phrase(phrase):
    """
        Blocking call - reads socket until the data is the same as phrase "start", "stop", "test", etc.

        Args:
            phrase: The string to listen to over the socket
    """
    while(server.getData() != phrase):
        print("waiting for" + phrase )

def wait_for_number(num):
    """
        Blocking call - reads socket until the header is the same as num "0", "1", "2", etc.

        Args:
            num: The num to listen to over the socket

    """
    header = '-1'
    while header != num:
        data = server.getData().split(',')
        #print(data)
        header = data[0]
    return data

def getReward():
    server.sendData('2')
    data = wait_for_number('2')
    reward = float(data[1])
    done = (data[2] == "True")
    i = int(data[3])
    return reward, done, i

def send_action(a):
    """
    Sends the string over a socket in the form of '1,action'
    To move left, it would be the string '1,1'
    Unity is checking for the header to be 1
    """

    server.sendData('1,' + str(a))
    wait_for_number('1')

def get_state_binary(bounding_box, resize_shape,previous_state = None, stack_image = False,initalState = False ):
    """
    Take a screenshot of the screen at Bounding Box
    Convert to binary image
    stack 
    Bounding Box: Top, Left, Width, Height
    """
    with mss.mss() as sct:
    # Use the 1st monitor
        monitor = {'top': bounding_box[0], 'left': bounding_box[1], 'width': bounding_box[2], 'height': bounding_box[3]}
        # Get raw pixels from the screen, save it to a Numpy array
        img = np.array(sct.grab(monitor))
    ## convert to hsv
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    ## mask of green (36,0,0) ~ (70, 255,255)
    lower_green = np.array([65,60,60])
    upper_green = np.array([80,255,255])
    mask1 = cv2.inRange(hsv, lower_green, upper_green) #hardcoded values for green

    lower_blue = np.array([120,0,0])
    upper_blue = np.array([255,255,255])
    mask2 = cv2.inRange(hsv,lower_blue,upper_blue )

    ## final mask and masked
    mask = cv2.bitwise_or(mask1, mask2)

    resized_img = cv2.resize(mask, resize_shape)

    if stack_image:
        if initalState:
            state = np.stack((resized_img, resized_img, resized_img, resized_img), axis=2) #80x80x4
            cv2.imshow('Init State', state[0])
            state = state.reshape(1, state.shape[0], state.shape[1], state.shape[2])  #1*80*80*4
            
        else:
            resized_img = resized_img.reshape(1, resized_img.shape[0], resized_img.shape[1], 1) #1x80x80x1
            state = np.append(resized_img, previous_state[:, :, :, :3], axis=3) #1x80x80x4
    else:
        state = resized_img.reshape((1,-1)) # 1 x shape[0] x shape[1]
    


    #print(resized_img.shape)
    #plt.imshow(resized_img)
    #plt.show()
   
    return state

def step(action, bounding_box ,resize_shape, stack_image, previous_state = None):
    
    send_action(action)
    reward, done, i  = getReward()
    state_prime =  get_state_binary(bounding_box, resize_shape, initalState=False, stack_image=stack_image, previous_state = previous_state)
    #print(state_prime, reward, done)
    return state_prime, reward, done, i



t = 0
EPOCHS = 1000000
OBSERVE = 32#320
REPLAY_MEMORY = 50000
BATCH = 32
LEARNING_RATE = 1e-4
FRAME_PER_ACTION = 1

update_model = True
load_model = False

esp = 1
reward_count = 0
total_reward = 0
total_loss = []
total_rewards = []
num_epochs = []

#bounding_box = [160,831,1018 - 831,757 - 160] #for x
#bounding_box = [109,865,970 - 865,757 - 109] #for x on laptop
bounding_box = [109,891,949 - 891,432 - 109]# for x on dual camera

stack_image = False
resize_shape = (80,200)

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

agent = DQNAgent(
                state_size = resize_shape[0]*resize_shape[1], 
                action_size = 3,
                gamma = 0.99,
                epsilon = esp,
                epsilon_min = 0.01,
                epsilon_decay = 0.995,
                learning_rate = LEARNING_RATE, 
                model_type = 'DeepModel'
                )
time.sleep(.5)

if load_model:
    agent.load('dqn_x_topview.h5')

wait_for_phrase("start")

open('plot.txt', 'w').close() #resets the text file

for r in range(EPOCHS):
    
    if total_reward > 1000 and update_model:
        agent.save('dqn_x_topview.h5')
        break


    state = get_state_binary(bounding_box, resize_shape, stack_image=stack_image)
   
    done = False
    while not done:
        
        
    
        action = agent.take_action(state)

        state_prime, reward, done, i = step(action, bounding_box, resize_shape, stack_image)

        if t > OBSERVE:
            total_reward += reward

        if update_model:
            agent.remember(state, action, reward, state_prime, done)
        
        if t > OBSERVE and update_model:
            history = agent.replay(BATCH)
            print("epoch: " + str(r) + " iteration: " + str(t) +  " loss: " +  str(history.history['loss']) + " total reward: " + str(total_reward))
            total_loss.append(history.history['loss'])
            
        state = state_prime   
        t=t+1
        if r % 10 == 0:
            total_rewards.append(total_reward)
            num_epochs.append(r)
            fh = open('plot.txt', 'a') 
            fh.write(str(r) + "," + str(total_reward) + "\n" ) 
            fh.close()

        if (t % 1000 == 0) and update_model:
           agent.save('dqn_x_topview.h5')

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