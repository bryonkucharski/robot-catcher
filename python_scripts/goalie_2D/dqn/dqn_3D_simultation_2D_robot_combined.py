'''
    Bryon Kucharski
    Wentorth Institute of Technology
    Summer 2018
    
    Applying a DQN to a 3D simulation ( Unity) of a 2D robot in both x and y direction
    X and Y are trained seperately, and combined in this file
    
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

def wait_for_phrase(phrase, server):
    """
        Blocking call - reads socket until the data is the same as phrase "start", "stop", "test", etc.

        Args:
            phrase: The string to listen to over the socket
    """
    while(server.getData() != phrase):
        print("waiting for" + phrase )

def wait_for_number(num, server):
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

def getReward(server):
    server.sendData('2')
    data = wait_for_number('2',server)
    reward = float(data[1])
    done = (data[2] == "True")
    i = int(data[3])
    return reward, done, i

def send_action(a, server):
    """
    Sends the string over a socket in the form of '1,action'
    To move left, it would be the string '1,1'
    Unity is checking for the header to be 1
    """

    server.sendData('1,' + str(a))
    wait_for_number('1', server)

def get_state_binary_y(bounding_box, resize_shape,previous_state = None, stack_image = False,initalState = False, epoch = None, iter = None ):


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
    
    if(ball_in_sight(img) is not True):

        return None

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
            state = state.reshape(1, state.shape[0], state.shape[1], state.shape[2])  #1*80*80*4
            
        else:
            resized_img = resized_img.reshape(1, resized_img.shape[0], resized_img.shape[1], 1) #1x80x80x1
            state = np.append(resized_img, previous_state[:, :, :, :3], axis=3) #1x80x80x4
            '''
            img1 = state[:,:,:,0].reshape(resize_shape[0], resize_shape[1])
            img2 = state[:,:,:,1].reshape(resize_shape[0], resize_shape[1])
            img3 = state[:,:,:,2].reshape(resize_shape[0], resize_shape[1])
            img4 = state[:,:,:,3].reshape(resize_shape[0], resize_shape[1])
            plt.figure(1)
            plt.subplot(411)
            plt.imshow(img1)

            plt.subplot(412)
            plt.imshow(img2)

            plt.subplot(413)
            plt.imshow(img3)

            plt.subplot(414)
            plt.imshow(img4)
            plt.savefig('animation%s_%s.png'%(epoch,iter))

        
            plt.show()
            '''
            
            
           
    else:
        state = resized_img.reshape((1,-1)) # 1 x shape[0] x shape[1]
    
   


    #print(resized_img.shape)
    #cv2.imshow('Original', img)
    #cv2.imshow('Mask', mask)
   
    return state

def get_state_binary_x(bounding_box, resize_shape,previous_state = None, stack_image = False,initalState = False):
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

def step(type,server,action, bounding_box ,resize_shape, stack_image, previous_state = None, epoch = None,iter = None):
    
    send_action(action,server)
    reward, done, i  = getReward(server)

    if type == 'x':
        state_prime =  get_state_binary_x(bounding_box, resize_shape, initalState=False, stack_image=False)
    elif type == 'y':
        state_prime =  get_state_binary_y(bounding_box, resize_shape, initalState=False, stack_image=stack_image, previous_state = previous_state, epoch = epoch, iter = iter)
    return state_prime, reward, done

def ball_in_sight(img):
    grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur_img = cv2.blur(grey_img, (4,4))
    circles = cv2.HoughCircles(blur_img, cv2.HOUGH_GRADIENT, 1, 20, param1 = 50, param2 = 30, minRadius = 1, maxRadius = 50)

    return circles is not None

def convert_action_to_unity_action(action):
    actionToSend = -1
    if action == 1:
        actionToSend = 3 #up
    elif action == 2:
        actionToSend = 4 #down
    return actionToSend

t = 0
EPOCHS = 1000000
OBSERVE = 32#320
REPLAY_MEMORY = 50000
BATCH = 32
LEARNING_RATE = 1e-4

load_model = True

esp = 1
reward_count = 0
total_reward = 0
total_reward_x = 0
total_reward_y = 0
total_loss = []
total_rewards_x = []
total_rewards_y = []
total_rewards = []
num_epochs = []

#bounding_box = [160,831,1018 - 831,757 - 160] #for x
#bounding_box = [109,1060,1640 - 1060,758 - 109] #for y camera monitors
bounding_box_x = [109,891,949 - 891,432 - 109]
bounding_box_y = [433,980,1323 - 980,756 - 433] #for y camera laptop

resize_shape_y = (100,100)
resize_shape_x = (80,200)

if (load_model):
    esp = 0.01
else:
    esp = 1

server_x = tcp_socket(
                    host = '',
                    port = 50000, 
                    backlog = 5, #amount of requests to queue at one time
                    size = 1024 
                    )
server_y = tcp_socket(
                    host = '',
                    port = 50001, 
                    backlog = 5, #amount of requests to queue at one time
                    size = 1024 
                    )
agent_x = DQNAgent(
                state_size = resize_shape_x[0]*resize_shape_x[1], 
                action_size = 3,
                gamma = 0.99,
                epsilon = esp,
                epsilon_min = 0.01,
                epsilon_decay = 0.995,
                learning_rate = LEARNING_RATE, 
                model_type = 'DeepModel'
                )
agent_y = DQNAgent(
                state_size = resize_shape_y[0]*resize_shape_y[1]*4, 
                action_size = 3,
                gamma = 0.99,
                epsilon = esp,
                epsilon_min = 0.01,
                epsilon_decay = 0.995,
                learning_rate = LEARNING_RATE, 
                model_type = 'DeepModel'
                )

#give time for unity to connect and start up
time.sleep(.5)

if load_model:
    agent_x.load('dqn_x_topview.h5')
    agent_y.load('dqn_y_sideview.h5')
    print("Agents Loaded.")

wait_for_phrase("start", server_x)
wait_for_phrase("start", server_y)

open('plot_combined.txt', 'w').close() #resets the text file

r = 0
while(True):
    
    
    state_x = get_state_binary_x(bounding_box_x, resize_shape_x, stack_image=False, initalState=True)
    state_y = get_state_binary_y(bounding_box_y, resize_shape_y, stack_image=True, initalState=True)

    y_found = True
    state_prime_y = None
    reward_x = 0
    reward_y = 0
    if(state_y is not  None):

        action_x = agent_x.take_action(state_x.reshape(1,-1))
        action_y = agent_y.take_action(state_y.reshape(1,-1))
        action_y = convert_action_to_unity_action(action_y)

        state_prime_x, reward_x, done_x = step('x',server_x,action_x, bounding_box_x, resize_shape_x, stack_image=False, epoch = r, iter= t)
        state_prime_y, reward_y, done_y = step('y',server_y,action_y, bounding_box_y, resize_shape_y, previous_state=state_y ,stack_image=True, epoch = r, iter= t)
    
    
    if(state_prime_y is not None):
      
        total_reward += (reward_x + reward_y)
        total_reward_x += reward_x
        total_reward_y += reward_y
        state_x = state_prime_x
        state_y = state_prime_y

    t=t+1

    if r % 10 == 0:
        total_rewards_x.append(reward_x)
        total_rewards_y.append(reward_y)
        total_rewards.append(total_reward)
        num_epochs.append(r)
        fh = open('plot_combined.txt', 'a') 
        fh.write(str(r) + "," + str(total_reward) + "," + str(total_reward_x) + "," + str(total_reward_y) + "\n" ) 
        fh.close()

    r = r + 1
'''
plt.figure(1)       
plt.plot(num_epochs,total_rewards_x)
plt.plot(num_epochs,total_rewards_y)
plt.title("Cumulative Reward in DQN 2D Simulation. Iterations: " + str(t))
plt.ylabel("Cumulative Reward")
plt.xlabel("Number of Updates")


plt.show()
'''