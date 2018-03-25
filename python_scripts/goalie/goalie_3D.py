import os, sys, inspect
import random
import time
from PIL import ImageGrab
import numpy as np

#this is just to import rl agent from a different folder
rl_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../rl")))
if rl_subfolder not in sys.path:
    sys.path.insert(0, rl_subfolder)

from qlearning_agent import rl_agent

socket_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../socket")))
if socket_subfolder not in sys.path:
    sys.path.insert(0, socket_subfolder)

from tcp_server import tcp_socket


vision_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../vision")))
if vision_subfolder not in sys.path:
    sys.path.insert(0, vision_subfolder)

import discretize_vision as v

#RL constants
EPSILON =       1    # greedy police
ALPHA =         0.5     # learning rate
GAMMA =         1       # discount 


def wait_to_start():
    while(server.getData() != 'start'):
        print("waiting to start")
    print('Unity is Ready')

def get_state_vision(grid_dim):
    
    screenImage = ImageGrab.grab(bbox=(305, 157, 580, 597))#(X, Y) starting position ; (W, H) ending position
    img = np.array(screenImage)#convert the image to a numpy array
    img_dim = img.shape[1], img.shape[0]
    cell_dim = v.get_cell_dimensions(img_dim, grid_dim)
    circle_center, radius = v.get_circle(img)
    cell = v.pixel_to_cell(circle_center, cell_dim)
    #print(cell)
    robot_x = get_robot_pos()
    if(len(cell) == 0):
        return
    else:
        return [ robot_x, cell[0] ]
    

def get_robot_pos():
    server.sendData('3')
    header = '-1'
    while header != '3':
        data = server.getData().split(',')
        #print(data)
        header = data[0]

    #ball_y = float(data[3])
    robot_x = int(data[1])

    return robot_x

   
def get_state_unity():
    '''
    requst data from unity
    wait until socket header is 0
    parse data

    '''
    server.sendData('0')
    header = '-1'
    while header != '0':
        data = server.getData().split(',')
        #print(data)
        header = data[0]

    #print('Getting State From Unity')
    ball_x = float(data[2])
    #ball_y = float(data[3])
    robot = int(data[1])
    return [robot, ball_x]
    #return [robot,ball_x,ball_y]

def send_action(a):
    server.sendData('1,' + str(a));

def get_reward():
    header = '-1'
    while header != '2':
        #print('Getting Reward From Unity')
        data = server.getData().split(',')
        header = data[0]
        reward = float(data[1])
        #print(reward)
        return reward

#def calculateReward():
    

agent = rl_agent(
                list(range(3)), #STAY,LEFT,RIGHT
                GAMMA,
                ALPHA,
                EPSILON
               )
           
server = tcp_socket(
                    host = '',
                    port = 50000, 
                    backlog = 5, #amount of requests to queue at one time
                    size = 1024 
                    )

agent.init_q_table()

#wait_to_start()
i = 0
epochs = 10000
update_rate = 1/5
grid_dim = (5,10)



start = time.time()
test = time.time()




while(i < epochs):

    end = time.time()
    elapsed = end - start

   # if(elapsed > update_rate):
    start = time.time()

    state = get_state_vision(grid_dim)
    #state = get_state_unity()

    #get action
    action = agent.get_action(str(state))
    send_action(action)

    reward = get_reward()

    state_prime = get_state_vision(grid_dim)
    #state_prime = get_state_unity()

    #print(str(state) + ", " + str(action) + ", " + str(reward) + ", " + str(state_prime))
    agent.update(str(state),action,reward,str(state_prime))

    if (i % 10 == 0):
        os.system('cls')
        agent.print_q_table()


    i = i + 1
